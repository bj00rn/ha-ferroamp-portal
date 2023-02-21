"""Api client"""
import asyncio
import enum
import json
import logging
import re

import aiohttp


class State(enum.Enum):
    """Client connection state"""

    NONE = "none"
    STOPPED = "stopped"
    RUNNING = "running"
    RETRYING = "retry"


RETRY_TIMER = 15

_LOGGER = logging.getLogger(__package__)


class ApiClient:
    """Portal client"""

    baseurl = "https://portal.ferroamp.com"
    auth_endpoint = f"{baseurl}/login"
    api_endpoint = f"{baseurl}/graphql/stream"
    cookie = None
    system_id = None
    session = None

    def _get_api_endpoint(self):
        return f"{self.api_endpoint}{self.system_id}/"

    async def __aenter__(self, *args, **kwargs):
        await self.connect()
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        system_id: int,
    ) -> None:

        assert username, "username not provided"
        assert password, "password not provided"
        assert system_id, "facility ID not provided"

        self.username = username
        self.password = password
        self.system_id = system_id
        self.session = session
        self.state = None
        self.stream = None
        self.headers = {"content-type": "application/json"}
        self.data = {}
        self.loop = asyncio.get_running_loop()
        self.state = State.NONE

    async def _auth(self):
        _LOGGER.debug("Authentication to %s", self.auth_endpoint)
        data = {"email": self.username, "password": self.password}
        await self.session.post(self.auth_endpoint, data=data, allow_redirects=False)

    async def running(self):
        """Get data"""

        if self.state == State.RUNNING:
            return

        headers = self.headers | {"accept": "text/event-stream"}
        data = {
            "variables": {"facilityId": f"{self.system_id}"},
            "extensions": {},
            "operationName": "OnEvseMetervalue",
            "query": "subscription OnEvseMetervalue($facilityId: FacilityID!) {\n  newEvseMeterValue(facilityId: $facilityId) {\n    terminalId\n    timestamp\n    powerActive\n    energyActiveMeter\n    currentL1\n    currentL2\n    currentL3\n    __typename\n  }\n}\n",
        }
        try:
            async with self.session.post(
                self.api_endpoint, headers=headers, json=data
            ) as response:
                self._set_state(State.RUNNING)
                _LOGGER.debug("Got response from %s", self.api_endpoint)
                async for line in response.content:
                    if self.state == State.STOPPED:
                        _LOGGER.debug("Got stop signal")
                        break
                    if line:
                        decoded_line: str = line.decode("utf-8")
                        _LOGGER.debug("Received [%s]", decoded_line)
                        if re.match("^data: ", decoded_line):
                            self.data = json.loads(decoded_line.split(": ", 1)[1])[
                                "data"
                            ]["newEvseMeterValue"]
        except (asyncio.TimeoutError, TimeoutError):
            _LOGGER.warning("Connection timeout", exc_info=True)
        except aiohttp.ClientError:
            _LOGGER.error("Connection error", exc_info=True)
        except Exception as e:
            _LOGGER.error("Unexpected exception", exc_info=True)
            raise e

        self.retry()

    async def connect(self):
        """Connect to system and wait for connection"""

        async def check_connection():
            while True:
                if self.state == State.RUNNING:
                    break
                await asyncio.sleep(0.2)

        await self._auth()
        self.start()
        await asyncio.wait_for(check_connection(), 10)

    def start(self):
        """Start client"""
        asyncio.create_task(self.running())

    def retry(self):
        """Retry connection"""
        if self.state != State.STOPPED:
            self.state = State.RETRYING
            self.loop.call_later(RETRY_TIMER, self.start)

    def stop(self):
        """Stop client"""
        self._set_state(State.STOPPED)

    def _set_state(self, state):
        self.state = state

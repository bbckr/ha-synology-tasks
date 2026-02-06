"""API client for Synology DSM."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests
from homeassistant.exceptions import HomeAssistantError

from .const import (
    API_ENABLE_SYNO_TOKEN,
    API_EVENT_SCHEDULER,
    API_LOGIN,
    API_METHOD_EVENT_SCHEDULER,
    API_METHOD_LOGIN,
    API_METHOD_TASK_SCHEDULER,
    API_SORT_BY_NAME,
    API_SORT_DIRECTION_ASC,
    API_SYNO_TOKEN,
    API_TASK_LIMIT,
    API_TASK_OFFSET,
    API_TASK_SCHEDULER,
    API_UNKNOWN,
    API_VERSION_EVENT_SCHEDULER,
    API_VERSION_LOGIN,
    API_VERSION_TASK_SCHEDULER,
    API_WEBAPI_ENDPOINT,
    API_YES,
    DATA_CODE_KEY,
    DATA_ERROR_KEY,
    DATA_KEY,
    DATA_SID_KEY,
    DATA_SUCCESS_KEY,
    DATA_SYNOTOKEN_KEY,
    DATA_TASKS_KEY,
    PROTOCOL_HTTP,
    PROTOCOL_HTTPS,
    SERVICE_DATA_TASK_NAME,
)
from .models import (
    SynologyAuthData,
    SynologyResponse,
    SynologyTask,
    SynologyTaskData,
    Task,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class SynologyDSM:
    """Synology DSM API client."""

    def __init__(self, hass: HomeAssistant, dsm_entry: ConfigEntry) -> None:
        """Initialize the API client."""
        self.hass = hass

        host = dsm_entry.data.get("host")
        port = dsm_entry.data.get("port")
        ssl = dsm_entry.data.get("ssl", True)

        self._verify_ssl = dsm_entry.data.get("verify_ssl", True)
        self._username = dsm_entry.data.get("username")
        self._password = dsm_entry.data.get("password")
        self._url = f"{(ssl and PROTOCOL_HTTPS) or PROTOCOL_HTTP}://{host}:{port}{API_WEBAPI_ENDPOINT}"

        self._session = None
        self._sid = None
        self._synotoken = None

    async def get_tasks(self) -> list[Task]:
        """Get list of tasks."""
        params = {
            "api": API_TASK_SCHEDULER,
            "method": API_METHOD_TASK_SCHEDULER,
            "version": API_VERSION_TASK_SCHEDULER,
            "sort_by": API_SORT_BY_NAME,
            "sort_direction": API_SORT_DIRECTION_ASC,
            "limit": API_TASK_LIMIT,
            "offset": API_TASK_OFFSET,
        }

        try:
            response = await self.hass.async_add_executor_job(
                self._sync_request, params
            )
        except Exception as err:
            _LOGGER.exception("Error getting tasks")
            raise SynologyTaskRunError from err

        tasks_data: SynologyTaskData = response.get(DATA_KEY, {})
        tasks: list[SynologyTask] = tasks_data.get(DATA_TASKS_KEY, [])
        return [Task.from_api(task) for task in tasks]

    async def run_task(self, task_name: str) -> None:
        """Run a task by name."""
        params = {
            "api": API_EVENT_SCHEDULER,
            "method": API_METHOD_EVENT_SCHEDULER,
            "version": API_VERSION_EVENT_SCHEDULER,
            SERVICE_DATA_TASK_NAME: task_name,
        }

        _LOGGER.debug(
            "Running task via DSM API: task_name=%s, api=%s, method=%s",
            task_name,
            API_EVENT_SCHEDULER,
            API_METHOD_EVENT_SCHEDULER,
        )

        try:
            response = await self.hass.async_add_executor_job(
                self._sync_request, params
            )
            _LOGGER.debug(
                "DSM run_task response for '%s': success=%s",
                task_name,
                response.get(DATA_SUCCESS_KEY),
            )
        except Exception as err:
            _LOGGER.exception(
                "Error running task '%s': %s",
                task_name,
                err,
            )
            raise SynologyTaskRunError from err

    def _sync_login(self) -> None:
        """Login to the DSM."""
        if self._session is None:
            self._session = requests.Session()

        params = {
            "api": API_LOGIN,
            "version": API_VERSION_LOGIN,
            "method": API_METHOD_LOGIN,
            API_ENABLE_SYNO_TOKEN: API_YES,
            "account": self._username,
            "passwd": self._password,
        }

        response = self._sync_request(params, is_login=True)
        data: SynologyAuthData = response.get(DATA_KEY, {})
        self._sid = data.get(DATA_SID_KEY)
        self._synotoken = data.get(DATA_SYNOTOKEN_KEY)

    def _sync_request(
        self, params: dict | None = None, *, is_login: bool = False
    ) -> SynologyResponse:
        """Do a request to the DSM."""
        if not is_login and (not self._sid or not self._synotoken or not self._session):
            self._sync_login()

        params[API_SYNO_TOKEN] = self._synotoken

        response: SynologyResponse | None = None
        try:
            r = self._session.get(self._url, params=params, verify=self._verify_ssl)
            response = r.json()
        except Exception as err:
            _LOGGER.exception("Unable to get response form DSM")
            raise SynologyDSMAPIError from err

        if not response.get(DATA_SUCCESS_KEY, False):
            _LOGGER.error("Error requesting: %s", r.text)
            error_code = response.get(DATA_ERROR_KEY, {}).get(
                DATA_CODE_KEY, API_UNKNOWN
            )
            error_message = f"Received error code: {error_code}"
            raise SynologyDSMAPIError(error_message)

        return response


class SynologyTaskRunError(HomeAssistantError):
    """Error to indicate the task run failed."""


class SynologyDSMAPIError(HomeAssistantError):
    """Error to indicate the DSM API error."""

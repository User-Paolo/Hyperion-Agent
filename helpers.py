import os

import httpx

IDE_BACKEND_URL = os.environ.get("IDE_BACKEND_URL", "http://localhost:3001/api")


class ReadFileError(Exception):
    """The IDE could not give us the file."""


class ValidateFileError(Exception):
    """The IDE could not validate the file."""


async def read_file(path: str) -> str:
    """Return the contents of a file in the IDE workspace.

    `path` is either a full path (`demo/app.yaml`) or just a file name, in which
    case the IDE searches the whole workspace for it. Raises ReadFileError with a
    message you can hand straight to a model.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{IDE_BACKEND_URL}/agent/file", params={"path": path}
            )
    except httpx.HTTPError as exc:
        raise ReadFileError(
            f"cannot reach the IDE backend at {IDE_BACKEND_URL} ({exc})"
        ) from exc

    if response.status_code == 404:
        raise ReadFileError(f"{path} is not in the workspace")

    if response.status_code == 409:
        matches = ", ".join(response.json().get("matches", []))
        raise ReadFileError(
            f"several files are named {path} ({matches}) - use the full path"
        )

    if response.status_code != 200:
        raise ReadFileError(
            response.json().get("error", f"HTTP {response.status_code}")
        )

    return response.json().get("content", "")


async def validate_file(path: str) -> dict:
    """Validate a file in the IDE workspace and return the report.

    `path` is either a full path (`demo/app.yaml`) or just a file name, in which
    case the IDE searches the whole workspace for it. The report is a dict with
    `path`, `type`, `valid`, `errors` and `warnings`. Raises ValidateFileError
    with a message you can hand straight to a model.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{IDE_BACKEND_URL}/agent/validation/file", params={"path": path}
            )
    except httpx.HTTPError as exc:
        raise ValidateFileError(
            f"cannot reach the IDE backend at {IDE_BACKEND_URL} ({exc})"
        ) from exc

    if response.status_code == 404:
        raise ValidateFileError(f"{path} is not in the workspace")

    if response.status_code == 409:
        matches = ", ".join(response.json().get("matches", []))
        raise ValidateFileError(
            f"several files are named {path} ({matches}) - use the full path"
        )

    if response.status_code != 200:
        raise ValidateFileError(
            response.json().get("error", f"HTTP {response.status_code}")
        )

    return response.json()

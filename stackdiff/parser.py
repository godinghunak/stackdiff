"""Parser module for loading and normalizing Docker Compose files."""

import yaml
from pathlib import Path
from typing import Union


class ComposeParseError(Exception):
    """Raised when a Compose file cannot be parsed."""


def load_compose_file(path: Union[str, Path]) -> dict:
    """Load a Docker Compose YAML file and return its contents as a dict.

    Args:
        path: Path to the docker-compose.yml file.

    Returns:
        Parsed contents of the Compose file.

    Raises:
        ComposeParseError: If the file is missing, unreadable, or invalid YAML.
    """
    path = Path(path)

    if not path.exists():
        raise ComposeParseError(f"File not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ComposeParseError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ComposeParseError(f"Expected a YAML mapping at the top level in {path}")

    return data


def extract_services(compose_data: dict) -> dict:
    """Extract the services section from parsed Compose data.

    Args:
        compose_data: The full parsed Compose file dict.

    Returns:
        A dict of service name -> service definition.  Returns an empty dict
        if the file defines no services.
    """
    services = compose_data.get("services", {})
    if services is None:
        return {}
    if not isinstance(services, dict):
        raise ComposeParseError(
            "'services' key must be a mapping, got: " + type(services).__name__
        )
    return services

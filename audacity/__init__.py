"""Audacity MCP client package.

This package provides a Python client for controlling Audacity via its
mod-script-pipe interface. It includes:

- AudacityConnection: Client for communicating with Audacity
- Command definitions: All available Audacity scripting commands
- Custom exceptions: Error handling for connection and command failures

Example:
    Basic usage with context manager::

        from audacity import AudacityConnection

        with AudacityConnection() as conn:
            conn.send_command("Play")
            conn.send_command("Pause")

    Manual connection management::

        from audacity import AudacityConnection

        conn = AudacityConnection()
        if conn.connect():
            response = conn.send_command("GetInfo: Type=Tracks Format=JSON")
            print(response)
            conn.disconnect()

    Using command definitions::

        from audacity import ALL_COMMANDS, COMMAND_CATEGORIES

        # List all available commands
        for cmd_id, description in ALL_COMMANDS:
            print(f"{cmd_id}: {description}")

        # Browse by category
        for category, commands in COMMAND_CATEGORIES.items():
            print(f"\\n{category}:")
            for cmd_id, description in commands:
                print(f"  {cmd_id}")
"""

from .client import AudacityConnection
from .exceptions import AudacityConnectionError, AudacityCommandError
from .commands import (
    ALL_COMMANDS,
    COMMAND_CATEGORIES,
    FILE_COMMANDS,
    IMPORT_COMMANDS,
    EDIT_COMMANDS,
    LABEL_COMMANDS,
    SELECT_COMMANDS,
    VIEW_COMMANDS,
    TRANSPORT_COMMANDS,
    EFFECT_COMMANDS,
    GENERATE_COMMANDS,
    ANALYZE_COMMANDS,
    TOOLS_COMMANDS,
    TRANSPORT_OPTIONS_COMMANDS,
    DEVICE_COMMANDS,
    SELECTION_COMMANDS,
    TIMELINE_COMMANDS,
    FOCUS_COMMANDS,
    CURSOR_COMMANDS,
    TRACK_COMMANDS,
    SCRIPTABLES_I_COMMANDS,
    SCRIPTABLES_II_COMMANDS,
    HELP_MENU_COMMANDS,
    DIAGNOSTICS_COMMANDS,
    NO_MENU_COMMANDS,
)

__version__ = "0.2.0"
__all__ = [
    # Client
    "AudacityConnection",
    # Exceptions
    "AudacityConnectionError",
    "AudacityCommandError",
    # Commands
    "ALL_COMMANDS",
    "COMMAND_CATEGORIES",
    "FILE_COMMANDS",
    "IMPORT_COMMANDS",
    "EDIT_COMMANDS",
    "LABEL_COMMANDS",
    "SELECT_COMMANDS",
    "VIEW_COMMANDS",
    "TRANSPORT_COMMANDS",
    "EFFECT_COMMANDS",
    "GENERATE_COMMANDS",
    "ANALYZE_COMMANDS",
    "TOOLS_COMMANDS",
    "TRANSPORT_OPTIONS_COMMANDS",
    "DEVICE_COMMANDS",
    "SELECTION_COMMANDS",
    "TIMELINE_COMMANDS",
    "FOCUS_COMMANDS",
    "CURSOR_COMMANDS",
    "TRACK_COMMANDS",
    "SCRIPTABLES_I_COMMANDS",
    "SCRIPTABLES_II_COMMANDS",
    "HELP_MENU_COMMANDS",
    "DIAGNOSTICS_COMMANDS",
    "NO_MENU_COMMANDS",
]

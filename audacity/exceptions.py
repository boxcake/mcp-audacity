"""Custom exceptions for Audacity MCP client.

This module defines exception classes used by the Audacity client
when communicating with Audacity via mod-script-pipe.
"""


class AudacityConnectionError(Exception):
    """Exception raised when connection to Audacity fails.

    This exception is raised when the client cannot establish or maintain
    a connection to Audacity's mod-script-pipe, typically because:
    - Audacity is not running
    - mod-script-pipe is not enabled in Audacity preferences
    - Named pipe files do not exist or have incorrect permissions
    - Pipe paths are incorrectly configured
    """

    pass


class AudacityCommandError(Exception):
    """Exception raised when a command execution fails.

    This exception is raised when a command is successfully sent to Audacity
    but fails during execution or response, typically because:
    - I/O error during command transmission
    - Pipe connection was lost during execution
    - Command syntax was invalid
    - Audacity encountered an error processing the command
    """

    pass

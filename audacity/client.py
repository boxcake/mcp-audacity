"""Audacity mod-script-pipe client.

This module provides a client for communicating with Audacity via its
mod-script-pipe interface using named pipes (FIFOs).
"""

import os
import time
import logging
from typing import Optional, TextIO

from .exceptions import AudacityConnectionError, AudacityCommandError

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_PIPE_TO = "/tmp/audacity_script_pipe.to.501"
DEFAULT_PIPE_FROM = "/tmp/audacity_script_pipe.from.501"
DEFAULT_COMMAND_TIMEOUT = 0.2  # seconds to wait after sending command


class AudacityConnection:
    """Manages communication with Audacity via mod-script-pipe.

    This class handles the low-level communication with Audacity using named
    pipes (FIFOs). It provides methods to connect, disconnect, and send
    commands to Audacity.

    The connection is designed to be resilient and will attempt to reconnect
    if the connection is lost during command execution.

    Attributes:
        to_pipe: Path to the pipe for sending commands to Audacity.
        from_pipe: Path to the pipe for receiving responses from Audacity.
        pipe_to: File handle for writing commands (None when disconnected).
        pipe_from: File handle for reading responses (None when disconnected).
        command_timeout: Default timeout in seconds to wait for command processing.

    Example:
        >>> conn = AudacityConnection()
        >>> if conn.connect():
        ...     response = conn.send_command("Play")
        ...     print(response)
        ...     conn.disconnect()
    """

    def __init__(
        self,
        to_pipe: Optional[str] = None,
        from_pipe: Optional[str] = None,
        command_timeout: Optional[float] = None,
    ) -> None:
        """Initialize the connection manager.

        Args:
            to_pipe: Path to the named pipe for sending commands to Audacity.
                If None, uses AUDACITY_PIPE_TO environment variable or default.
            from_pipe: Path to the named pipe for receiving responses from Audacity.
                If None, uses AUDACITY_PIPE_FROM environment variable or default.
            command_timeout: Default timeout for command execution in seconds.
                If None, uses AUDACITY_COMMAND_TIMEOUT environment variable or default.
        """
        self.to_pipe = to_pipe or os.environ.get("AUDACITY_PIPE_TO", DEFAULT_PIPE_TO)
        self.from_pipe = from_pipe or os.environ.get(
            "AUDACITY_PIPE_FROM", DEFAULT_PIPE_FROM
        )
        self.command_timeout = (
            command_timeout
            or float(os.environ.get("AUDACITY_COMMAND_TIMEOUT", DEFAULT_COMMAND_TIMEOUT))
        )
        self.pipe_to: Optional[TextIO] = None
        self.pipe_from: Optional[TextIO] = None

    def connect(self) -> bool:
        """Open the named pipes for communication with Audacity.

        Returns:
            True if connection was successful, False otherwise.

        Note:
            This method will fail if Audacity is not running or if
            mod-script-pipe is not enabled in Audacity preferences.
        """
        try:
            # Verify pipes exist before attempting to open
            if not os.path.exists(self.to_pipe):
                logger.error(f"Command pipe does not exist: {self.to_pipe}")
                return False
            if not os.path.exists(self.from_pipe):
                logger.error(f"Response pipe does not exist: {self.from_pipe}")
                return False

            # Open pipes for communication
            self.pipe_to = open(self.to_pipe, "w")
            self.pipe_from = open(self.from_pipe, "r")
            logger.info(f"Opened Audacity mod-script-pipe: {self.to_pipe}")
            return True
        except OSError as e:
            logger.error(f"Failed to open Audacity pipes: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error opening pipes: {e}")
            return False

    def disconnect(self) -> None:
        """Close the named pipes and clean up resources.

        This method safely closes both pipe file handles and sets them to None.
        It is safe to call this method multiple times.
        """
        try:
            if self.pipe_to:
                self.pipe_to.close()
                logger.debug("Closed command pipe")
            if self.pipe_from:
                self.pipe_from.close()
                logger.debug("Closed response pipe")
        except Exception as e:
            logger.error(f"Error closing pipes: {e}")
        finally:
            self.pipe_to = None
            self.pipe_from = None

    def is_connected(self) -> bool:
        """Check if the connection is currently active.

        Returns:
            True if both pipes are open, False otherwise.
        """
        return self.pipe_to is not None and self.pipe_from is not None

    def send_command(
        self, command: str, timeout: Optional[float] = None
    ) -> str:
        """Send a command to Audacity and return its response.

        This method sends a command string to Audacity via the command pipe,
        waits for Audacity to process it, and then reads the response from
        the response pipe.

        If not currently connected, this method will attempt to establish
        a connection before sending the command.

        Args:
            command: The Audacity scripting command to execute.
            timeout: Time in seconds to wait for Audacity to process the command.
                If None, uses the instance's default command_timeout.

        Returns:
            The response string from Audacity (stripped of whitespace).

        Raises:
            AudacityConnectionError: If not connected or connection fails.
            AudacityCommandError: If command execution fails.

        Note:
            Commands must be valid Audacity scripting commands. See
            https://manual.audacityteam.org/man/scripting_reference.html
        """
        if timeout is None:
            timeout = self.command_timeout

        # Ensure we're connected
        if not self.is_connected():
            if not self.connect():
                raise AudacityConnectionError(
                    "Could not connect to Audacity mod-script-pipe. "
                    "Ensure Audacity is running with mod-script-pipe enabled."
                )

        try:
            # Send command with newline terminator
            self.pipe_to.write(command + "\n")
            self.pipe_to.flush()

            # Wait for Audacity to process the command
            time.sleep(timeout)

            # Read single-line response
            response = self.pipe_from.readline().strip()
            logger.info(f"Command: '{command}' → Response: '{response}'")
            return response

        except OSError as e:
            logger.error(f"I/O error sending command '{command}': {e}")
            self.disconnect()
            raise AudacityCommandError(f"Failed to send command: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error sending command '{command}': {e}")
            self.disconnect()
            raise AudacityCommandError(f"Command execution failed: {e}") from e

    def __enter__(self) -> "AudacityConnection":
        """Context manager entry: establish connection.

        Returns:
            Self for use in with statement.

        Raises:
            AudacityConnectionError: If connection fails.
        """
        if not self.connect():
            raise AudacityConnectionError("Failed to connect to Audacity")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit: clean up connection."""
        self.disconnect()

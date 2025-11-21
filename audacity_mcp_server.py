#!/usr/bin/env python3
"""Audacity MCP Server.

An MCP (Model Context Protocol) server that connects to Audacity via the
mod-script-pipe interface and exposes a comprehensive set of Audacity
scripting commands as MCP tool endpoints.

This server uses named pipes (FIFOs) to communicate with Audacity. Before
running, ensure that Audacity's mod-script-pipe is enabled:
  - For Audacity 3.x or later, open Preferences → Scripting
  - Enable the mod-script-pipe option
  - Restart Audacity

The server will attempt to connect to the named pipes, which are typically
located in /tmp on macOS/Linux. The pipe paths can be customized using
environment variables AUDACITY_PIPE_TO and AUDACITY_PIPE_FROM.

For more information about Audacity scripting:
https://manual.audacityteam.org/man/scripting_reference.html
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable, Dict, Optional

from mcp.server.fastmcp import Context, FastMCP

from audacity import ALL_COMMANDS, AudacityConnection, AudacityConnectionError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AudacityMCPServer")

# Global connection instance
_audacity_connection: Optional[AudacityConnection] = None


def get_audacity_connection() -> AudacityConnection:
    """Get or create the global Audacity connection instance.

    This function implements a singleton pattern for the Audacity connection.
    The connection is created on first use and reused for subsequent calls.

    Returns:
        The global AudacityConnection instance.

    Raises:
        AudacityConnectionError: If initial connection fails.
    """
    global _audacity_connection
    if _audacity_connection is None:
        _audacity_connection = AudacityConnection()
        if not _audacity_connection.connect():
            raise AudacityConnectionError(
                "Could not open mod-script-pipe to Audacity. "
                "Make sure Audacity is running with mod-script-pipe enabled. "
                f"Expected pipes: {_audacity_connection.to_pipe} "
                f"and {_audacity_connection.from_pipe}"
            )
    return _audacity_connection


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle.

    This async context manager handles initialization and cleanup for the
    MCP server. It attempts to connect to Audacity on startup and ensures
    proper cleanup on shutdown.

    Args:
        server: The FastMCP server instance.

    Yields:
        An empty dictionary (required by FastMCP lifespan protocol).
    """
    try:
        logger.info("Audacity MCP server starting up")

        # Attempt initial connection
        try:
            conn = get_audacity_connection()
            logger.info(
                f"Looking for pipes: TO={conn.to_pipe}, FROM={conn.from_pipe}"
            )
            logger.info("Connected to Audacity mod-script-pipe")
        except AudacityConnectionError as e:
            logger.warning(f"Initial connection failed: {e}")
            logger.warning("Server will retry connection on first command")

        yield {}

    finally:
        # Cleanup on shutdown
        global _audacity_connection
        if _audacity_connection:
            logger.info("Disconnecting from Audacity mod-script-pipe")
            _audacity_connection.disconnect()
            _audacity_connection = None
        logger.info("Audacity MCP server shut down")


# Create the MCP server instance
mcp = FastMCP(
    "AudacityMCP",
    description="MCP server to control Audacity via mod-script-pipe with comprehensive commands",
    lifespan=server_lifespan,
)


def make_command_function(cmd_id: str, doc: str) -> Callable[[Context], str]:
    """Create a command function for an Audacity scripting command.

    This factory function generates a wrapper function that executes the
    specified Audacity command and handles errors appropriately.

    Args:
        cmd_id: The Audacity command identifier (e.g., "Play", "Record").
        doc: Documentation string describing what the command does.

    Returns:
        A function that can be registered as an MCP tool endpoint.
    """

    def command_func(ctx: Context) -> str:
        """Execute Audacity command via mod-script-pipe.

        Args:
            ctx: MCP context (unused but required by MCP protocol).

        Returns:
            The response from Audacity or an error message.
        """
        try:
            return get_audacity_connection().send_command(cmd_id)
        except Exception as e:
            error_msg = f"Error executing {cmd_id}: {e}"
            logger.error(error_msg)
            return error_msg

    # Set function metadata for better debugging and documentation
    command_func.__doc__ = doc
    command_func.__name__ = f"cmd_{cmd_id}"
    return command_func


def register_commands() -> None:
    """Register all Audacity commands as MCP tool endpoints.

    This function iterates through all command definitions and registers
    each one as an MCP tool that can be invoked by MCP clients.
    """
    for cmd_id, doc in ALL_COMMANDS:
        func_name = f"cmd_{cmd_id}"
        # Dynamically create and register the command function
        globals()[func_name] = mcp.tool()(make_command_function(cmd_id, doc))

    logger.info(f"Registered {len(ALL_COMMANDS)} Audacity commands as MCP tools")


# Register all commands
register_commands()


def main() -> None:
    """Run the MCP server with stdio transport.

    This is the main entry point for the server. It starts the FastMCP
    server using standard I/O for communication with MCP clients.
    """
    logger.info("Starting Audacity MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

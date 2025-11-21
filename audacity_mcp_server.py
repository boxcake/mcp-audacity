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

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, TextIO, Tuple

from mcp.server.fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AudacityMCPServer")

# Configuration constants
DEFAULT_PIPE_TO = "/tmp/audacity_script_pipe.to.501"
DEFAULT_PIPE_FROM = "/tmp/audacity_script_pipe.from.501"
DEFAULT_COMMAND_TIMEOUT = 0.2  # seconds to wait after sending command

# Get pipe paths from environment variables or use defaults
PIPE_TO = os.environ.get("AUDACITY_PIPE_TO", DEFAULT_PIPE_TO)
PIPE_FROM = os.environ.get("AUDACITY_PIPE_FROM", DEFAULT_PIPE_FROM)
COMMAND_TIMEOUT = float(os.environ.get("AUDACITY_COMMAND_TIMEOUT", DEFAULT_COMMAND_TIMEOUT))


class AudacityConnectionError(Exception):
    """Exception raised when connection to Audacity fails."""

    pass


class AudacityCommandError(Exception):
    """Exception raised when a command execution fails."""

    pass


class AudacityConnection:
    """Manages communication with Audacity via mod-script-pipe.

    This class handles the low-level communication with Audacity using named
    pipes (FIFOs). It provides methods to connect, disconnect, and send
    commands to Audacity.

    Attributes:
        to_pipe: Path to the pipe for sending commands to Audacity.
        from_pipe: Path to the pipe for receiving responses from Audacity.
        pipe_to: File handle for writing commands (None when disconnected).
        pipe_from: File handle for reading responses (None when disconnected).
    """

    def __init__(self, to_pipe: str, from_pipe: str) -> None:
        """Initialize the connection manager.

        Args:
            to_pipe: Path to the named pipe for sending commands to Audacity.
            from_pipe: Path to the named pipe for receiving responses from Audacity.
        """
        self.to_pipe = to_pipe
        self.from_pipe = from_pipe
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

    def send_command(self, command: str, timeout: float = COMMAND_TIMEOUT) -> str:
        """Send a command to Audacity and return its response.

        This method sends a command string to Audacity via the command pipe,
        waits for Audacity to process it, and then reads the response from
        the response pipe.

        Args:
            command: The Audacity scripting command to execute.
            timeout: Time in seconds to wait for Audacity to process the command.

        Returns:
            The response string from Audacity (stripped of whitespace).

        Raises:
            AudacityConnectionError: If not connected or connection fails.
            AudacityCommandError: If command execution fails.

        Note:
            Commands must be valid Audacity scripting commands. See
            https://manual.audacityteam.org/man/scripting_reference.html
        """
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
        _audacity_connection = AudacityConnection(PIPE_TO, PIPE_FROM)
        if not _audacity_connection.connect():
            raise AudacityConnectionError(
                f"Could not open mod-script-pipe to Audacity. "
                f"Make sure Audacity is running with mod-script-pipe enabled. "
                f"Expected pipes: {PIPE_TO} and {PIPE_FROM}"
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
        logger.info(f"Looking for pipes: TO={PIPE_TO}, FROM={PIPE_FROM}")

        try:
            conn = get_audacity_connection()
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
        except (AudacityConnectionError, AudacityCommandError) as e:
            error_msg = f"Error executing {cmd_id}: {e}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error executing {cmd_id}: {e}"
            logger.error(error_msg)
            return error_msg

    # Set function metadata for better debugging and documentation
    command_func.__doc__ = doc
    command_func.__name__ = f"cmd_{cmd_id}"
    return command_func


# Command definitions organized by category
# Each tuple contains (CommandID, Description)

file_commands: List[Tuple[str, str]] = [
    ("New", "New: Create a new empty project window."),
    ("Open", "Open: Open an audio file, list of files, or project."),
    ("Close", "Close: Close the current project window."),
    ("Save", "Save: Save the current project."),
    ("SaveAs", "SaveAs: Save the current project under a new name."),
    ("SaveCopy", "SaveCopy: Save a lossless copy of the project."),
    ("SaveCompressed", "SaveCompressed: Save a compressed copy of the project."),
    ("ExportAudio", "ExportAudio: Export audio files in various formats."),
    ("Print", "Print: Print all waveforms in the current project."),
    ("Exit", "Exit: Close all project windows and exit Audacity."),
]

import_commands: List[Tuple[str, str]] = [
    ("ImportAudio", "ImportAudio: Import an audio file as a new track."),
    ("ImportLabels", "ImportLabels: Import labels into the project."),
    ("ImportMIDI", "ImportMIDI: Import a MIDI file into a note track."),
    ("ImportRaw", "ImportRaw: Import raw audio data without headers."),
]

edit_commands: List[Tuple[str, str]] = [
    ("Undo", "Undo: Undo the most recent editing action."),
    ("Redo", "Redo: Redo the most recent undone action."),
    ("Cut", "Cut: Remove the selected audio and place it on the clipboard."),
    ("Delete", "Delete: Remove the selected audio without copying it."),
    ("Copy", "Copy: Copy the selected audio to the clipboard."),
    ("Paste", "Paste: Insert clipboard contents at the selection."),
    ("Duplicate", "Duplicate: Duplicate the current selection as a new clip."),
    ("EditMetaData", "EditMetaData: Edit the metadata for a track."),
    ("SplitCut", "SplitCut: Split the current clip and remove audio to right of the cut."),
    ("SplitDelete", "SplitDelete: Remove selected audio without shifting remaining audio."),
    ("Silence", "Silence: Replace selected audio with silence."),
    ("Trim", "Trim: Delete all audio except for the selected portion."),
]

label_commands: List[Tuple[str, str]] = [
    ("EditLabels", "EditLabels: Open the Label Editor dialog."),
    ("AddLabel", "AddLabel: Create a new label at the selection."),
    ("PasteNewLabel", "PasteNewLabel: Paste text from the clipboard into a new label."),
    ("TypeToCreateLabel", "TypeToCreateLabel: Create a label by typing (if enabled)."),
]

select_commands: List[Tuple[str, str]] = [
    ("SelectAll", "SelectAll: Select all audio in all tracks."),
    ("SelectNone", "SelectNone: Deselect all audio in all tracks."),
    ("StoreCursorPosition", "StoreCursorPosition: Store current cursor position for later selection."),
    ("SelCursorStoredCursor", "SelCursorStoredCursor: Select audio from current cursor to stored position."),
    ("ZeroCross", "ZeroCross: Adjust selection boundaries to the nearest zero crossing."),
]

view_commands: List[Tuple[str, str]] = [
    ("UndoHistory", "UndoHistory: Display the undo history window."),
    ("Karaoke", "Karaoke: Display the karaoke window."),
    ("MixerBoard", "MixerBoard: Switch to the mixer board view."),
    ("ShowExtraMenus", "ShowExtraMenus: Toggle extra menus display."),
    ("ShowClipping", "ShowClipping: Toggle display of clipping in the waveform."),
    ("ZoomIn", "ZoomIn: Zoom in horizontally."),
    ("ZoomNormal", "ZoomNormal: Reset zoom to the default view."),
    ("ZoomOut", "ZoomOut: Zoom out horizontally."),
    ("ZoomSel", "ZoomSel: Zoom to fill the current selection."),
    ("ZoomToggle", "ZoomToggle: Toggle between two preset zoom levels."),
]

transport_commands: List[Tuple[str, str]] = [
    ("PlayStop", "PlayStop: Toggle playback on and off."),
    ("PlayStopSelect", "PlayStopSelect: Play/Stop and update cursor position."),
    ("Pause", "Pause: Temporarily pause playback or recording."),
    ("Record1stChoice", "Record1stChoice: Start recording on the currently selected track."),
    ("Record2ndChoice", "Record2ndChoice: Start recording on a new track."),
    ("TimerRecord", "TimerRecord: Open Timer Record dialog."),
    ("PunchAndRoll", "PunchAndRoll: Start punch and roll recording."),
    ("Scrub", "Scrub: Scrub through audio."),
    ("Seek", "Seek: Jump to a specified position in the audio."),
]

effect_commands: List[Tuple[str, str]] = [
    ("Amplify", "Amplify: Adjust the volume of the selected audio."),
    ("AutoDuck", "AutoDuck: Automatically lower one track's volume when another is active."),
    ("BassAndTreble", "BassAndTreble: Adjust bass and treble levels."),
    ("ChangePitch", "ChangePitch: Change pitch without changing tempo."),
    ("ChangeSpeed", "ChangeSpeed: Change both speed and pitch."),
    ("ChangeTempo", "ChangeTempo: Change tempo without affecting pitch."),
    ("ClickRemoval", "ClickRemoval: Remove clicks from the audio."),
    ("Compressor", "Compressor: Compress the dynamic range."),
    ("Distortion", "Distortion: Apply a distortion effect."),
    ("Delay", "Delay: Apply a delay effect."),
    ("Echo", "Echo: Apply an echo effect."),
    ("FadeIn", "FadeIn: Apply a linear fade-in."),
    ("FadeOut", "FadeOut: Apply a linear fade-out."),
    ("FilterCurve", "FilterCurve: Adjust frequency response using a custom curve."),
    ("GraphicEq", "GraphicEq: Apply a graphic equalizer effect."),
    ("Invert", "Invert: Invert the polarity of the audio."),
    ("LoudnessNormalization", "LoudnessNormalization: Normalize perceived loudness."),
    ("NoiseReduction", "NoiseReduction: Reduce background noise."),
    ("Normalize", "Normalize: Normalize audio volume levels."),
    ("Paulstretch", "Paulstretch: Apply an extreme time-stretch effect."),
    ("Phaser", "Phaser: Apply a phaser effect."),
    ("Repair", "Repair: Attempt to fix short clicks or glitches."),
    ("Repeat", "Repeat: Repeat the selected audio a specified number of times."),
    ("Reverb", "Reverb: Apply a reverberation effect."),
    ("Reverse", "Reverse: Reverse the selected audio."),
    ("SlidingStretch", "SlidingStretch: Continuously change tempo and/or pitch."),
    ("TruncateSilence", "TruncateSilence: Remove or compress silences."),
    ("Wahwah", "Wahwah: Apply a wahwah effect."),
]

generate_commands: List[Tuple[str, str]] = [
    ("Chirp", "Chirp: Generate a chirp tone with adjustable frequency and amplitude."),
    ("DtmfTones", "DtmfTones: Generate dual-tone multi-frequency (DTMF) tones."),
    ("Noise", "Noise: Generate noise (white, pink, or brown)."),
    ("Tone", "Tone: Generate a tone of specific frequency, amplitude, and waveform."),
    ("Nyquist", "Nyquist: Open the Nyquist scripting prompt."),
    ("Pluck", "Pluck: Generate a plucked tone effect."),
    ("RhythmTrack", "RhythmTrack: Generate a rhythmic track at a specified tempo."),
    ("RissetDrum", "RissetDrum: Generate a continuously evolving drum sound."),
]

analyze_commands: List[Tuple[str, str]] = [
    ("ManageAnalyzers", "ManageAnalyzers: Open the analyzers plugin manager."),
    ("ContrastAnalyser", "ContrastAnalyser: Analyze the contrast between foreground and background audio."),
    ("PlotSpectrum", "PlotSpectrum: Plot the frequency spectrum of the selected audio."),
]

tools_commands: List[Tuple[str, str]] = [
    ("ManageTools", "ManageTools: Open the tools/effects/generators manager."),
    ("ManageMacros", "ManageMacros: Create or edit macros."),
    ("ApplyMacro", "ApplyMacro: Apply a defined macro to the project."),
    ("Screenshot", "Screenshot: Capture a screenshot of Audacity (short format)."),
]

transport_options_commands: List[Tuple[str, str]] = [
    ("SoundActivationLevel", "SoundActivationLevel: Set the threshold level for sound-activated recording."),
    ("SoundActivation", "SoundActivation: Toggle sound-activated recording."),
]

device_commands: List[Tuple[str, str]] = [
    ("InputDevice", "InputDevice: Open the recording device selection dialog."),
    ("OutputDevice", "OutputDevice: Open the playback device selection dialog."),
    ("ChangeAudio", "ChangeAudio: Open the audio host/interface selection dialog."),
]

selection_commands: List[Tuple[str, str]] = [
    ("SnapToOff", "SnapToOff: Disable snapping for selections."),
    ("SnapToNearest", "SnapToNearest: Snap selections to the nearest time unit."),
    ("SnapToPrior", "SnapToPrior: Snap selections to the previous time unit."),
    ("SelStart", "SelStart: Set selection from cursor to start of track."),
    ("SelEnd", "SelEnd: Set selection from cursor to end of track."),
]

timeline_commands: List[Tuple[str, str]] = [
    ("MinutesandSeconds", "MinutesandSeconds: Set timeline format to minutes and seconds."),
    ("BeatsandMeasures", "BeatsandMeasures: Set timeline format to beats and measures."),
]

focus_commands: List[Tuple[str, str]] = [
    ("PrevFrame", "PrevFrame: Move focus backward from toolbars to tracks."),
    ("NextFrame", "NextFrame: Move focus forward from toolbars to tracks."),
    ("PrevTrack", "PrevTrack: Focus the previous track."),
    ("NextTrack", "NextTrack: Focus the next track."),
    ("FirstTrack", "FirstTrack: Focus the first track."),
    ("LastTrack", "LastTrack: Focus the last track."),
    ("ShiftUp", "ShiftUp: Move focus upward and select the previous track."),
    ("ShiftDown", "ShiftDown: Move focus downward and select the next track."),
    ("Toggle", "Toggle: Toggle focus on the current track."),
]

cursor_commands: List[Tuple[str, str]] = [
    ("CursorLeft", "CursorLeft: Move the cursor left by one unit."),
    ("CursorRight", "CursorRight: Move the cursor right by one unit."),
    ("CursorShortJumpLeft", "CursorShortJumpLeft: Move the cursor 1 second left."),
    ("CursorShortJumpRight", "CursorShortJumpRight: Move the cursor 1 second right."),
    ("CursorLongJumpLeft", "CursorLongJumpLeft: Move the cursor 15 seconds left."),
    ("CursorLongJumpRight", "CursorLongJumpRight: Move the cursor 15 seconds right."),
]

track_commands: List[Tuple[str, str]] = [
    ("TrackPan", "TrackPan: Open the pan dialog for the focused track."),
    ("TrackPanLeft", "TrackPanLeft: Pan the focused track to the left."),
    ("TrackPanRight", "TrackPanRight: Pan the focused track to the right."),
    ("TrackGain", "TrackGain: Open the gain dialog for the focused track."),
    ("TrackGainInc", "TrackGainInc: Increase the gain on the focused track."),
    ("TrackGainDec", "TrackGainDec: Decrease the gain on the focused track."),
    ("TrackMute", "TrackMute: Toggle mute on the focused track."),
    ("TrackSolo", "TrackSolo: Toggle solo on the focused track."),
    ("TrackClose", "TrackClose: Close the focused track."),
    ("TrackMoveUp", "TrackMoveUp: Move the focused track up one position."),
    ("TrackMoveDown", "TrackMoveDown: Move the focused track down one position."),
    ("TrackMoveTop", "TrackMoveTop: Move the focused track to the top."),
    ("TrackMoveBottom", "TrackMoveBottom: Move the focused track to the bottom."),
]

scriptables_I_commands: List[Tuple[str, str]] = [
    ("Select", "Select: Modify selection based on parameters."),
    ("SetTrackStatus", "SetTrackStatus: Set properties (name, selected, focused) for a track."),
    ("SetTrackAudio", "SetTrackAudio: Set audio properties (mute, solo, gain, pan) for a track."),
]

scriptables_II_commands: List[Tuple[str, str]] = [
    ("SetPreference", "SetPreference: Set a preference value (with optional reload)."),
    ("GetPreference", "GetPreference: Retrieve a preference value."),
    ("SetClip", "SetClip: Modify properties (color, start time) of a clip."),
    ("SetEnvelope", "SetEnvelope: Adjust the envelope value at a specified time."),
    ("SetLabel", "SetLabel: Modify an existing label."),
    ("SetProject", "SetProject: Change project window properties (size, position, caption)."),
    ("GetInfo", "GetInfo: Retrieve project information in a specified format."),
    ("Message", "Message: Send a test message to Audacity."),
    ("Help", "Help: Get help information for a command."),
    ("Import2", "Import2: Import data from a file (using a filename)."),
    ("Export2", "Export2: Export selected audio to a file with detailed options."),
    ("OpenProject2", "OpenProject2: Open a project given a filename."),
    ("SaveProject2", "SaveProject2: Save the current project with additional options."),
    ("Drag", "Drag: Simulate a mouse drag for UI interactions."),
    ("CompareAudio", "CompareAudio: Compare audio regions between tracks."),
    ("Screenshot", "Screenshot: Capture a screenshot (short format)."),
]

help_menu_commands: List[Tuple[str, str]] = [
    ("QuickHelp", "QuickHelp: Display a brief help message."),
    ("Manual", "Manual: Open Audacity's manual in the default web browser."),
    ("Updates", "Updates: Check for updates for Audacity."),
    ("About", "About: Display information about Audacity."),
]

diagnostics_commands: List[Tuple[str, str]] = [
    ("DeviceInfo", "DeviceInfo: Show technical information about audio devices."),
    ("MidiDeviceInfo", "MidiDeviceInfo: Show information about MIDI devices."),
    ("Log", "Log: Open the Audacity log window."),
    ("CrashReport", "CrashReport: Generate a support report for troubleshooting."),
    ("CheckDeps", "CheckDeps: Check dependencies for the current project."),
]

no_menu_commands: List[Tuple[str, str]] = [
    ("PrevWindow", "PrevWindow: Navigate to the previous window."),
    ("NextWindow", "NextWindow: Navigate to the next window."),
]


def add_commands(cmd_list: List[Tuple[str, str]]) -> None:
    """Register a list of Audacity commands as MCP tool endpoints.

    This helper function takes a list of command definitions and registers
    each one as an MCP tool that can be invoked by MCP clients.

    Args:
        cmd_list: List of (command_id, description) tuples to register.
    """
    for cmd_id, doc in cmd_list:
        func_name = f"cmd_{cmd_id}"
        # Dynamically create and register the command function
        globals()[func_name] = mcp.tool()(make_command_function(cmd_id, doc))


# Register all command categories with the MCP server
add_commands(file_commands)
add_commands(import_commands)
add_commands(edit_commands)
add_commands(label_commands)
add_commands(select_commands)
add_commands(view_commands)
add_commands(transport_commands)
add_commands(effect_commands)
add_commands(generate_commands)
add_commands(analyze_commands)
add_commands(tools_commands)
add_commands(transport_options_commands)
add_commands(device_commands)
add_commands(selection_commands)
add_commands(timeline_commands)
add_commands(focus_commands)
add_commands(cursor_commands)
add_commands(track_commands)
add_commands(scriptables_I_commands)
add_commands(scriptables_II_commands)
add_commands(help_menu_commands)
add_commands(diagnostics_commands)
add_commands(no_menu_commands)


def main() -> None:
    """Run the MCP server with stdio transport.

    This is the main entry point for the server. It starts the FastMCP
    server using standard I/O for communication with MCP clients.
    """
    logger.info("Starting Audacity MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

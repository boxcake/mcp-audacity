"""Audacity MCP client package.

This package provides a Python client for controlling Audacity via its
mod-script-pipe interface. It includes:

- AudacityConnection: Client for communicating with Audacity
- Command definitions: All available Audacity scripting commands
- Custom exceptions: Error handling for connection and command failures
- Data models: Structured representations of Audacity entities
- Parsers: Convert JSON responses to typed Python objects
- Validators: Validate parameters before sending commands
- Helpers: High-level convenience functions for common workflows

Example:
    Basic usage with context manager::

        from audacity import AudacityConnection

        with AudacityConnection() as conn:
            conn.send_command("Play")
            conn.send_command("Pause")

    Using high-level helpers::

        from audacity import AudacityConnection, get_tracks_info, create_label

        with AudacityConnection() as conn:
            # Get parsed track information
            tracks = get_tracks_info(conn)
            for track in tracks:
                print(f"{track.name}: {track.duration}s")

            # Create a labeled chapter marker
            create_label(conn, "Introduction", start=0.0, end=30.0)

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

# Core client and exceptions
from .client import AudacityConnection
from .exceptions import AudacityConnectionError, AudacityCommandError

# Commands
from .commands import (
    ALL_COMMANDS,
    ANALYZE_COMMANDS,
    COMMAND_CATEGORIES,
    CURSOR_COMMANDS,
    DEVICE_COMMANDS,
    DIAGNOSTICS_COMMANDS,
    EDIT_COMMANDS,
    EFFECT_COMMANDS,
    FILE_COMMANDS,
    FOCUS_COMMANDS,
    GENERATE_COMMANDS,
    HELP_MENU_COMMANDS,
    IMPORT_COMMANDS,
    LABEL_COMMANDS,
    NO_MENU_COMMANDS,
    SCRIPTABLES_I_COMMANDS,
    SCRIPTABLES_II_COMMANDS,
    SELECT_COMMANDS,
    SELECTION_COMMANDS,
    TIMELINE_COMMANDS,
    TOOLS_COMMANDS,
    TRACK_COMMANDS,
    TRANSPORT_COMMANDS,
    TRANSPORT_OPTIONS_COMMANDS,
    VIEW_COMMANDS,
)

# Models
from .models import (
    AudioFormat,
    ClipInfo,
    EnvelopePoint,
    Label,
    ProjectInfo,
    SelectionMode,
    TimeRange,
    TrackInfo,
    TrackKind,
)

# Parsers
from .parsers import (
    ParseError,
    parse_clips,
    parse_envelopes,
    parse_json_response,
    parse_labels,
    parse_project_info,
    parse_tracks,
)

# Validators
from .validators import (
    ValidationError,
    validate_audio_format,
    validate_export_quality,
    validate_file_path,
    validate_gain,
    validate_label_text,
    validate_pan,
    validate_sample_rate,
    validate_selection_mode,
    validate_time_range,
    validate_track_number,
)

# Helpers
from .helpers import (
    apply_podcast_processing,
    create_chapter_marker,
    create_label,
    detect_speech_segments,
    export_audio,
    get_clips,
    get_labels,
    get_project_info,
    get_selection_info,
    get_tracks_info,
    import_audio,
    select_time_range,
    select_tracks,
)

__version__ = "0.3.0"
__all__ = [
    # Client
    "AudacityConnection",
    # Exceptions
    "AudacityConnectionError",
    "AudacityCommandError",
    "ParseError",
    "ValidationError",
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
    # Models
    "AudioFormat",
    "ClipInfo",
    "EnvelopePoint",
    "Label",
    "ProjectInfo",
    "SelectionMode",
    "TimeRange",
    "TrackInfo",
    "TrackKind",
    # Parsers
    "parse_clips",
    "parse_envelopes",
    "parse_json_response",
    "parse_labels",
    "parse_project_info",
    "parse_tracks",
    # Validators
    "validate_audio_format",
    "validate_export_quality",
    "validate_file_path",
    "validate_gain",
    "validate_label_text",
    "validate_pan",
    "validate_sample_rate",
    "validate_selection_mode",
    "validate_time_range",
    "validate_track_number",
    # Helpers
    "apply_podcast_processing",
    "create_chapter_marker",
    "create_label",
    "detect_speech_segments",
    "export_audio",
    "get_clips",
    "get_labels",
    "get_project_info",
    "get_selection_info",
    "get_tracks_info",
    "import_audio",
    "select_time_range",
    "select_tracks",
]

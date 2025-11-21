"""High-level helper functions for common Audacity workflows.

This module provides convenient, high-level functions that combine
multiple Audacity commands to accomplish common tasks. These functions
use the client, parsers, and validators to provide a cleaner API.
"""

import logging
from typing import List, Optional

from .client import AudacityConnection
from .models import (
    AudioFormat,
    ClipInfo,
    Label,
    ProjectInfo,
    SelectionMode,
    TimeRange,
    TrackInfo,
)
from .parsers import (
    ParseError,
    parse_clips,
    parse_labels,
    parse_project_info,
    parse_tracks,
)
from .validators import (
    ValidationError,
    validate_audio_format,
    validate_file_path,
    validate_label_text,
    validate_selection_mode,
    validate_time_range,
    validate_track_number,
)

logger = logging.getLogger(__name__)


def get_tracks_info(conn: AudacityConnection) -> List[TrackInfo]:
    """Get all tracks with parsed metadata.

    Args:
        conn: Active Audacity connection.

    Returns:
        List of TrackInfo objects with complete metadata.

    Raises:
        AudacityConnectionError: If connection fails.
        ParseError: If response parsing fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     tracks = get_tracks_info(conn)
        ...     for track in tracks:
        ...         print(f"{track.name}: {track.duration}s")
    """
    response = conn.send_command("GetInfo: Type=Tracks Format=JSON")
    return parse_tracks(response)


def get_labels(conn: AudacityConnection) -> List[Label]:
    """Get all labels as Label objects.

    Args:
        conn: Active Audacity connection.

    Returns:
        List of Label objects with .text, .start, .end attributes.

    Raises:
        AudacityConnectionError: If connection fails.
        ParseError: If response parsing fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     labels = get_labels(conn)
        ...     for label in labels:
        ...         print(f"{label.text} at {label.start}-{label.end}s")
    """
    response = conn.send_command("GetInfo: Type=Labels Format=JSON")
    return parse_labels(response)


def get_clips(conn: AudacityConnection) -> List[ClipInfo]:
    """Get all clips with parsed metadata.

    Args:
        conn: Active Audacity connection.

    Returns:
        List of ClipInfo objects.

    Raises:
        AudacityConnectionError: If connection fails.
        ParseError: If response parsing fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     clips = get_clips(conn)
        ...     for clip in clips:
        ...         print(f"Clip on track {clip.track}: {clip.duration}s")
    """
    response = conn.send_command("GetInfo: Type=Clips Format=JSON")
    return parse_clips(response)


def get_project_info(conn: AudacityConnection) -> ProjectInfo:
    """Get complete project information.

    Args:
        conn: Active Audacity connection.

    Returns:
        ProjectInfo object with project metadata.

    Raises:
        AudacityConnectionError: If connection fails.
        ParseError: If response parsing fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     info = get_project_info(conn)
        ...     print(f"Project has {info.num_tracks} tracks at {info.project_rate}Hz")
    """
    response = conn.send_command("GetInfo: Type=Project Format=JSON")
    return parse_project_info(response)


def select_time_range(
    conn: AudacityConnection,
    start: float,
    end: float,
    mode: SelectionMode = SelectionMode.SET,
) -> str:
    """Select a time range with validation.

    Args:
        conn: Active Audacity connection.
        start: Start time in seconds.
        end: End time in seconds.
        mode: Selection mode (Set or Add).

    Returns:
        Response from Audacity.

    Raises:
        ValidationError: If parameters are invalid.
        AudacityConnectionError: If connection fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     select_time_range(conn, 10.0, 30.0)
        ...     # Now 10-30s is selected
    """
    validate_time_range(start, end)
    validate_selection_mode(mode.value)

    command = f"SelectTime: Start={start} End={end}"
    if mode != SelectionMode.SET:
        command += f" Mode={mode.value}"

    return conn.send_command(command)


def select_tracks(
    conn: AudacityConnection,
    track: int,
    track_count: int = 1,
    mode: SelectionMode = SelectionMode.SET,
) -> str:
    """Select one or more tracks with validation.

    Args:
        conn: Active Audacity connection.
        track: Zero-based index of first track to select.
        track_count: Number of consecutive tracks to select.
        mode: Selection mode (Set or Add).

    Returns:
        Response from Audacity.

    Raises:
        ValidationError: If parameters are invalid.
        AudacityConnectionError: If connection fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     select_tracks(conn, track=0, track_count=2)
        ...     # Now first two tracks are selected
    """
    validate_track_number(track)
    if track_count < 1:
        raise ValidationError(f"track_count must be >= 1, got {track_count}")
    validate_selection_mode(mode.value)

    command = f"SelectTracks: Track={track} TrackCount={track_count}"
    if mode != SelectionMode.SET:
        command += f" Mode={mode.value}"

    return conn.send_command(command)


def create_label(
    conn: AudacityConnection,
    text: str,
    start: float,
    end: Optional[float] = None,
) -> str:
    """Create a label at a specific time or range.

    This is a convenience function that handles the full workflow:
    selecting the time, adding the label, and setting its text.

    Args:
        conn: Active Audacity connection.
        text: Label text.
        start: Start time in seconds.
        end: End time in seconds (None for point label).

    Returns:
        Response from final command.

    Raises:
        ValidationError: If parameters are invalid.
        AudacityConnectionError: If connection fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     # Create point label
        ...     create_label(conn, "Intro starts", 0.0)
        ...
        ...     # Create region label
        ...     create_label(conn, "Chorus", 60.0, 90.0)
    """
    validate_label_text(text)

    if end is None:
        end = start

    validate_time_range(start, end)

    # Select the time range
    select_time_range(conn, start, end)

    # Add label at selection
    conn.send_command("AddLabel:")

    # Get the label index (it will be the last one)
    labels = get_labels(conn)
    if not labels:
        raise RuntimeError("Failed to create label")

    label_index = labels[-1].index

    # Set the label text
    return conn.send_command(f"SetLabel: Label={label_index} Text='{text}'")


def create_chapter_marker(
    conn: AudacityConnection, time: float, title: str, track: int = 0
) -> str:
    """Create a chapter marker at a specific time.

    This combines track selection, time selection, label creation,
    and text setting into one convenient function.

    Args:
        conn: Active Audacity connection.
        time: Time position for the chapter marker in seconds.
        title: Chapter title.
        track: Track to select (default: 0).

    Returns:
        Response from final command.

    Raises:
        ValidationError: If parameters are invalid.
        AudacityConnectionError: If connection fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     create_chapter_marker(conn, 0.0, "Introduction")
        ...     create_chapter_marker(conn, 125.5, "Chapter 1")
        ...     create_chapter_marker(conn, 450.0, "Conclusion")
    """
    validate_track_number(track)
    validate_label_text(title)

    # Select the track
    select_tracks(conn, track, track_count=1)

    # Create label at the time
    return create_label(conn, title, time)


def export_audio(
    conn: AudacityConnection,
    filename: str,
    audio_format: AudioFormat = AudioFormat.WAV,
) -> str:
    """Export audio to a file with validation.

    Args:
        conn: Active Audacity connection.
        filename: Output file path.
        audio_format: Audio format for export.

    Returns:
        Response from Audacity.

    Raises:
        ValidationError: If parameters are invalid.
        AudacityConnectionError: If connection fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     export_audio(conn, "/path/to/output.wav", AudioFormat.WAV)
        ...     export_audio(conn, "/path/to/output.mp3", AudioFormat.MP3)
    """
    validate_audio_format(audio_format.value)
    file_path = validate_file_path(filename, must_not_exist=False)

    command = f"Export2: Filename='{file_path}'"
    if audio_format != AudioFormat.WAV:
        command += f" Format={audio_format.value}"

    return conn.send_command(command)


def import_audio(conn: AudacityConnection, filename: str) -> str:
    """Import an audio file with validation.

    Args:
        conn: Active Audacity connection.
        filename: Path to audio file to import.

    Returns:
        Response from Audacity.

    Raises:
        ValidationError: If file doesn't exist.
        AudacityConnectionError: If connection fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     import_audio(conn, "/path/to/audio.wav")
    """
    file_path = validate_file_path(filename, must_exist=True)
    return conn.send_command(f"Import2: Filename='{file_path}'")


def detect_speech_segments(
    conn: AudacityConnection, threshold_db: float = -30, silence_duration: float = 0.5
) -> List[Label]:
    """Auto-detect speech segments and return as labels.

    This uses Audacity's LabelSounds analyzer to detect regions with
    audio above the threshold, then returns the resulting labels.

    Args:
        conn: Active Audacity connection.
        threshold_db: Threshold in dB (default: -30).
        silence_duration: Minimum silence duration in seconds (default: 0.5).

    Returns:
        List of Label objects marking speech regions.

    Raises:
        AudacityConnectionError: If connection fails.
        ParseError: If response parsing fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     # Detect speech in current project
        ...     conn.send_command("SelectAll:")
        ...     segments = detect_speech_segments(conn, threshold_db=-30)
        ...     for seg in segments:
        ...         print(f"Speech at {seg.start}-{seg.end}s")
    """
    # Use LabelSounds to detect speech
    command = f"LabelSounds: threshold={threshold_db} sil-dur={silence_duration}"
    conn.send_command(command)

    # Get the resulting labels
    return get_labels(conn)


def apply_podcast_processing(
    conn: AudacityConnection,
    normalize: bool = True,
    noise_reduction: bool = True,
    compress: bool = True,
) -> List[str]:
    """Apply standard podcast processing effects in the correct order.

    Args:
        conn: Active Audacity connection.
        normalize: Apply normalization (default: True).
        noise_reduction: Apply noise reduction (default: True).
        compress: Apply compression (default: True).

    Returns:
        List of responses from each effect applied.

    Raises:
        AudacityConnectionError: If connection fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     conn.send_command("SelectAll:")
        ...     responses = apply_podcast_processing(conn)
        ...     print(f"Applied {len(responses)} effects")
    """
    responses = []

    # Apply effects in recommended order
    if noise_reduction:
        # Note: Noise reduction requires noise profile first
        logger.info("Applying noise reduction")
        responses.append(conn.send_command("NoiseReduction:"))

    if normalize:
        logger.info("Applying normalization")
        responses.append(conn.send_command("Normalize:"))

    if compress:
        logger.info("Applying compression")
        responses.append(conn.send_command("Compressor:"))

    return responses


def get_selection_info(conn: AudacityConnection) -> Optional[TimeRange]:
    """Get the current selection as a TimeRange.

    Args:
        conn: Active Audacity connection.

    Returns:
        TimeRange if there is a selection, None otherwise.

    Raises:
        AudacityConnectionError: If connection fails.
        ParseError: If response parsing fails.

    Example:
        >>> with AudacityConnection() as conn:
        ...     selection = get_selection_info(conn)
        ...     if selection:
        ...         print(f"Selected {selection.duration}s")
    """
    project = get_project_info(conn)
    return project.get_selection_range()

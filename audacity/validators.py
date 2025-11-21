"""Parameter validation for Audacity commands.

This module provides validation functions to check command parameters
before sending them to Audacity, providing clear error messages early
instead of waiting for Audacity to reject invalid commands.
"""

import os
from pathlib import Path
from typing import Optional

from .models import AudioFormat, SelectionMode


class ValidationError(Exception):
    """Exception raised when parameter validation fails."""

    pass


def validate_track_number(
    track: int, min_track: int = 0, max_track: Optional[int] = None
) -> None:
    """Validate a track number.

    Args:
        track: Track number to validate (zero-based).
        min_track: Minimum valid track number (default: 0).
        max_track: Maximum valid track number (None = no max).

    Raises:
        ValidationError: If track number is invalid.

    Example:
        >>> validate_track_number(0)  # OK
        >>> validate_track_number(-1)  # Raises ValidationError
        >>> validate_track_number(5, max_track=3)  # Raises ValidationError
    """
    if track < min_track:
        raise ValidationError(f"Track number must be >= {min_track}, got {track}")

    if max_track is not None and track > max_track:
        raise ValidationError(f"Track number must be <= {max_track}, got {track}")


def validate_time_range(
    start: float, end: float, allow_equal: bool = True, min_time: float = 0.0
) -> None:
    """Validate a time range.

    Args:
        start: Start time in seconds.
        end: End time in seconds.
        allow_equal: Whether start == end is valid (default: True).
        min_time: Minimum valid time (default: 0.0).

    Raises:
        ValidationError: If time range is invalid.

    Example:
        >>> validate_time_range(1.0, 5.0)  # OK
        >>> validate_time_range(5.0, 1.0)  # Raises ValidationError
        >>> validate_time_range(-1.0, 5.0)  # Raises ValidationError
    """
    if start < min_time:
        raise ValidationError(f"Start time must be >= {min_time}, got {start}")

    if end < min_time:
        raise ValidationError(f"End time must be >= {min_time}, got {end}")

    if allow_equal:
        if start > end:
            raise ValidationError(f"Start time ({start}) must be <= end time ({end})")
    else:
        if start >= end:
            raise ValidationError(f"Start time ({start}) must be < end time ({end})")


def validate_file_path(
    path: str, must_exist: bool = False, must_not_exist: bool = False
) -> Path:
    """Validate a file path.

    Args:
        path: File path to validate.
        must_exist: If True, file must exist.
        must_not_exist: If True, file must not exist.

    Returns:
        Validated Path object.

    Raises:
        ValidationError: If path validation fails.

    Example:
        >>> validate_file_path("/path/to/file.wav", must_exist=True)
        >>> validate_file_path("/new/file.mp3", must_not_exist=True)
    """
    if not path:
        raise ValidationError("File path cannot be empty")

    file_path = Path(path).resolve()

    if must_exist and not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")

    if must_not_exist and file_path.exists():
        raise ValidationError(f"File already exists: {file_path}")

    # Check parent directory exists for new files
    if must_not_exist and not file_path.parent.exists():
        raise ValidationError(f"Parent directory does not exist: {file_path.parent}")

    return file_path


def validate_audio_format(format_str: str) -> AudioFormat:
    """Validate an audio format string.

    Args:
        format_str: Audio format string (e.g., "WAV", "MP3").

    Returns:
        AudioFormat enum value.

    Raises:
        ValidationError: If format is not supported.

    Example:
        >>> validate_audio_format("WAV")  # Returns AudioFormat.WAV
        >>> validate_audio_format("INVALID")  # Raises ValidationError
    """
    format_upper = format_str.upper()

    try:
        return AudioFormat(format_upper)
    except ValueError:
        valid_formats = ", ".join(f.value for f in AudioFormat)
        raise ValidationError(
            f"Invalid audio format '{format_str}'. "
            f"Supported formats: {valid_formats}"
        )


def validate_selection_mode(mode: str) -> SelectionMode:
    """Validate a selection mode string.

    Args:
        mode: Selection mode string (e.g., "Set", "Add").

    Returns:
        SelectionMode enum value.

    Raises:
        ValidationError: If mode is not supported.

    Example:
        >>> validate_selection_mode("Set")  # Returns SelectionMode.SET
        >>> validate_selection_mode("Invalid")  # Raises ValidationError
    """
    # Try to match case-insensitively
    mode_title = mode.title()  # "set" -> "Set"

    try:
        return SelectionMode(mode_title)
    except ValueError:
        valid_modes = ", ".join(m.value for m in SelectionMode)
        raise ValidationError(
            f"Invalid selection mode '{mode}'. " f"Supported modes: {valid_modes}"
        )


def validate_gain(gain: float, min_gain: float = 0.0, max_gain: float = 10.0) -> None:
    """Validate a gain/volume value.

    Args:
        gain: Gain value to validate.
        min_gain: Minimum valid gain (default: 0.0).
        max_gain: Maximum valid gain (default: 10.0).

    Raises:
        ValidationError: If gain is out of range.

    Example:
        >>> validate_gain(1.0)  # OK (100%)
        >>> validate_gain(2.0)  # OK (200%)
        >>> validate_gain(-0.5)  # Raises ValidationError
        >>> validate_gain(20.0)  # Raises ValidationError
    """
    if gain < min_gain:
        raise ValidationError(f"Gain must be >= {min_gain}, got {gain}")

    if gain > max_gain:
        raise ValidationError(f"Gain must be <= {max_gain}, got {gain}")


def validate_pan(pan: float) -> None:
    """Validate a pan value.

    Args:
        pan: Pan value to validate (-1.0=left, 0.0=center, 1.0=right).

    Raises:
        ValidationError: If pan is out of range.

    Example:
        >>> validate_pan(0.0)  # OK (center)
        >>> validate_pan(-1.0)  # OK (full left)
        >>> validate_pan(1.0)  # OK (full right)
        >>> validate_pan(2.0)  # Raises ValidationError
    """
    if pan < -1.0 or pan > 1.0:
        raise ValidationError(f"Pan must be between -1.0 and 1.0, got {pan}")


def validate_sample_rate(rate: int) -> None:
    """Validate a sample rate.

    Args:
        rate: Sample rate in Hz.

    Raises:
        ValidationError: If sample rate is invalid.

    Example:
        >>> validate_sample_rate(44100)  # OK
        >>> validate_sample_rate(48000)  # OK
        >>> validate_sample_rate(100)  # Raises ValidationError
    """
    common_rates = [8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000, 192000]

    if rate <= 0:
        raise ValidationError(f"Sample rate must be positive, got {rate}")

    if rate not in common_rates:
        rates_str = ", ".join(str(r) for r in common_rates)
        raise ValidationError(
            f"Sample rate {rate} is uncommon. "
            f"Common rates: {rates_str}. "
            f"Proceed with caution."
        )


def validate_label_text(text: str, max_length: int = 255) -> None:
    """Validate label text.

    Args:
        text: Label text to validate.
        max_length: Maximum text length (default: 255).

    Raises:
        ValidationError: If text is invalid.

    Example:
        >>> validate_label_text("Chapter 1")  # OK
        >>> validate_label_text("A" * 300)  # Raises ValidationError
    """
    if not text:
        raise ValidationError("Label text cannot be empty")

    if len(text) > max_length:
        raise ValidationError(
            f"Label text too long ({len(text)} characters). " f"Maximum: {max_length}"
        )


def validate_export_quality(format: AudioFormat, quality: int) -> None:
    """Validate export quality for a given format.

    Args:
        format: Audio format.
        quality: Quality value (meaning depends on format).

    Raises:
        ValidationError: If quality is invalid for the format.

    Example:
        >>> validate_export_quality(AudioFormat.MP3, 192)  # OK
        >>> validate_export_quality(AudioFormat.MP3, 500)  # Raises ValidationError
    """
    if format == AudioFormat.MP3:
        # MP3 bitrate in kbps
        valid_bitrates = [32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
        if quality not in valid_bitrates:
            bitrates_str = ", ".join(str(b) for b in valid_bitrates)
            raise ValidationError(
                f"Invalid MP3 bitrate {quality}. " f"Valid bitrates: {bitrates_str}"
            )

    elif format == AudioFormat.OGG:
        # OGG quality -1 to 10
        if quality < -1 or quality > 10:
            raise ValidationError(f"OGG quality must be -1 to 10, got {quality}")

    elif format in (AudioFormat.WAV, AudioFormat.FLAC):
        # WAV and FLAC don't use quality parameter
        if quality != 0:
            raise ValidationError(f"{format.value} format does not use quality parameter")

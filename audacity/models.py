"""Data models for Audacity entities.

This module defines structured data classes for common Audacity entities
like labels, tracks, clips, and project information. These models are used
by parsers to convert raw JSON responses into typed Python objects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TrackKind(str, Enum):
    """Types of tracks in Audacity."""

    WAVE = "wave"
    LABEL = "label"
    TIME = "time"
    NOTE = "note"


class SelectionMode(str, Enum):
    """Selection modes for track/time selection."""

    SET = "Set"
    ADD = "Add"


class AudioFormat(str, Enum):
    """Supported audio export formats."""

    WAV = "WAV"
    MP3 = "MP3"
    OGG = "OGG"
    FLAC = "FLAC"
    M4A = "M4A"


@dataclass
class TimeRange:
    """Represents a time range in seconds.

    Attributes:
        start: Start time in seconds.
        end: End time in seconds.
    """

    start: float
    end: float

    def __post_init__(self) -> None:
        """Validate that start is before end."""
        if self.start > self.end:
            raise ValueError(f"Start time ({self.start}) must be <= end time ({self.end})")

    @property
    def duration(self) -> float:
        """Get the duration of the time range in seconds."""
        return self.end - self.start

    def overlaps(self, other: "TimeRange") -> bool:
        """Check if this time range overlaps with another.

        Args:
            other: Another time range to check for overlap.

        Returns:
            True if the ranges overlap, False otherwise.
        """
        return self.start < other.end and other.start < self.end


@dataclass
class Label:
    """Represents a label in Audacity.

    Labels mark specific points or regions in the audio timeline.

    Attributes:
        index: Zero-based index of the label.
        text: Label text/title.
        start: Start time in seconds.
        end: End time in seconds (same as start for point labels).
    """

    index: int
    text: str
    start: float
    end: float

    @property
    def is_point_label(self) -> bool:
        """Check if this is a point label (not a region).

        Returns:
            True if start equals end, False otherwise.
        """
        return self.start == self.end

    @property
    def is_region_label(self) -> bool:
        """Check if this is a region label (has duration).

        Returns:
            True if start does not equal end, False otherwise.
        """
        return self.start != self.end

    @property
    def duration(self) -> float:
        """Get the duration of the label region in seconds.

        Returns:
            0.0 for point labels, end - start for region labels.
        """
        return self.end - self.start

    def as_time_range(self) -> TimeRange:
        """Convert this label to a TimeRange.

        Returns:
            TimeRange representing the label's time span.
        """
        return TimeRange(start=self.start, end=self.end)


@dataclass
class TrackInfo:
    """Represents track metadata from Audacity.

    Attributes:
        index: Zero-based track index.
        name: Track name.
        kind: Type of track (wave, label, time, note).
        start_time: Start time of audio in track (seconds).
        end_time: End time of audio in track (seconds).
        channels: Number of channels (1=mono, 2=stereo).
        sample_rate: Sample rate in Hz (e.g., 44100).
        selected: Whether the track is currently selected.
        focused: Whether the track has focus.
        mute: Whether the track is muted.
        solo: Whether the track is soloed.
        gain: Track gain/volume level.
        pan: Track pan position (-1.0=left, 0.0=center, 1.0=right).
    """

    index: int
    name: str
    kind: TrackKind
    start_time: float
    end_time: float
    channels: int = 1
    sample_rate: int = 44100
    selected: bool = False
    focused: bool = False
    mute: bool = False
    solo: bool = False
    gain: float = 1.0
    pan: float = 0.0

    @property
    def duration(self) -> float:
        """Get the duration of audio in the track in seconds."""
        return self.end_time - self.start_time

    @property
    def is_mono(self) -> bool:
        """Check if this is a mono track."""
        return self.channels == 1

    @property
    def is_stereo(self) -> bool:
        """Check if this is a stereo track."""
        return self.channels == 2


@dataclass
class ClipInfo:
    """Represents an audio clip within a track.

    Attributes:
        track: Zero-based track index containing this clip.
        start: Start time of clip in seconds.
        end: End time of clip in seconds.
        color: Color index of the clip.
        name: Clip name (optional).
    """

    track: int
    start: float
    end: float
    color: int = 0
    name: Optional[str] = None

    @property
    def duration(self) -> float:
        """Get the duration of the clip in seconds."""
        return self.end - self.start

    def as_time_range(self) -> TimeRange:
        """Convert this clip to a TimeRange.

        Returns:
            TimeRange representing the clip's time span.
        """
        return TimeRange(start=self.start, end=self.end)


@dataclass
class EnvelopePoint:
    """Represents a point in a track's volume envelope.

    Attributes:
        time: Time position in seconds.
        value: Envelope value (typically 0.0 to 1.0).
    """

    time: float
    value: float


@dataclass
class ProjectInfo:
    """Represents overall project information.

    Attributes:
        project_rate: Project sample rate in Hz.
        num_tracks: Total number of tracks.
        num_wave_tracks: Number of waveform tracks.
        num_label_tracks: Number of label tracks.
        focus_track: Index of focused track (-1 if none).
        selection_start: Start of selection in seconds.
        selection_end: End of selection in seconds.
    """

    project_rate: int
    num_tracks: int
    num_wave_tracks: int = 0
    num_label_tracks: int = 0
    focus_track: int = -1
    selection_start: float = 0.0
    selection_end: float = 0.0

    @property
    def has_selection(self) -> bool:
        """Check if there is an active selection."""
        return self.selection_start != self.selection_end

    @property
    def selection_duration(self) -> float:
        """Get the duration of the current selection in seconds."""
        return abs(self.selection_end - self.selection_start)

    def get_selection_range(self) -> Optional[TimeRange]:
        """Get the selection as a TimeRange, if there is one.

        Returns:
            TimeRange if there is a selection, None otherwise.
        """
        if self.has_selection:
            return TimeRange(
                start=min(self.selection_start, self.selection_end),
                end=max(self.selection_start, self.selection_end),
            )
        return None

"""Parsers for Audacity command responses.

This module provides functions to parse raw JSON responses from Audacity
GetInfo commands into structured Python objects defined in models.py.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .models import (
    ClipInfo,
    EnvelopePoint,
    Label,
    ProjectInfo,
    TrackInfo,
    TrackKind,
)

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Exception raised when parsing Audacity response fails."""

    pass


def parse_json_response(response: str) -> Any:
    """Parse a JSON response string from Audacity.

    Args:
        response: Raw JSON string from Audacity.

    Returns:
        Parsed JSON data structure.

    Raises:
        ParseError: If the response is not valid JSON.
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON response: {e}") from e


def parse_label(data: Dict[str, Any], index: int) -> Label:
    """Parse a single label from Audacity JSON data.

    Args:
        data: Dictionary containing label data.
        index: Index of this label in the label track.

    Returns:
        Label object with parsed data.

    Raises:
        ParseError: If required fields are missing or invalid.
    """
    try:
        return Label(
            index=index,
            text=str(data.get("text", "")),
            start=float(data.get("t0", data.get("start", 0.0))),
            end=float(data.get("t1", data.get("end", 0.0))),
        )
    except (KeyError, ValueError, TypeError) as e:
        raise ParseError(f"Failed to parse label: {e}") from e


def parse_labels(response: str) -> List[Label]:
    """Parse labels from GetInfo Type=Labels response.

    Args:
        response: Raw JSON string from GetInfo: Type=Labels command.

    Returns:
        List of Label objects.

    Raises:
        ParseError: If parsing fails.

    Example:
        >>> conn = AudacityConnection()
        >>> response = conn.send_command("GetInfo: Type=Labels Format=JSON")
        >>> labels = parse_labels(response)
        >>> for label in labels:
        ...     print(f"{label.text} at {label.start}s")
    """
    try:
        data = parse_json_response(response)

        # Handle different possible response formats
        if isinstance(data, list):
            labels_data = data
        elif isinstance(data, dict) and "labels" in data:
            labels_data = data["labels"]
        else:
            raise ParseError(f"Unexpected labels response format: {type(data)}")

        return [parse_label(label_data, idx) for idx, label_data in enumerate(labels_data)]

    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse labels response: {e}") from e


def parse_track(data: Dict[str, Any], index: int) -> TrackInfo:
    """Parse a single track from Audacity JSON data.

    Args:
        data: Dictionary containing track data.
        index: Index of this track in the project.

    Returns:
        TrackInfo object with parsed data.

    Raises:
        ParseError: If required fields are missing or invalid.
    """
    try:
        # Parse track kind/type
        kind_str = data.get("kind", data.get("type", "wave")).lower()
        try:
            kind = TrackKind(kind_str)
        except ValueError:
            logger.warning(f"Unknown track kind '{kind_str}', defaulting to 'wave'")
            kind = TrackKind.WAVE

        return TrackInfo(
            index=index,
            name=str(data.get("name", f"Track {index}")),
            kind=kind,
            start_time=float(data.get("start", data.get("startTime", 0.0))),
            end_time=float(data.get("end", data.get("endTime", 0.0))),
            channels=int(data.get("channels", 1)),
            sample_rate=int(data.get("rate", data.get("sampleRate", 44100))),
            selected=bool(data.get("selected", False)),
            focused=bool(data.get("focused", False)),
            mute=bool(data.get("mute", False)),
            solo=bool(data.get("solo", False)),
            gain=float(data.get("gain", 1.0)),
            pan=float(data.get("pan", 0.0)),
        )
    except (KeyError, ValueError, TypeError) as e:
        raise ParseError(f"Failed to parse track: {e}") from e


def parse_tracks(response: str) -> List[TrackInfo]:
    """Parse tracks from GetInfo Type=Tracks response.

    Args:
        response: Raw JSON string from GetInfo: Type=Tracks command.

    Returns:
        List of TrackInfo objects.

    Raises:
        ParseError: If parsing fails.

    Example:
        >>> conn = AudacityConnection()
        >>> response = conn.send_command("GetInfo: Type=Tracks Format=JSON")
        >>> tracks = parse_tracks(response)
        >>> for track in tracks:
        ...     print(f"{track.name}: {track.duration}s")
    """
    try:
        data = parse_json_response(response)

        # Handle different possible response formats
        if isinstance(data, list):
            tracks_data = data
        elif isinstance(data, dict) and "tracks" in data:
            tracks_data = data["tracks"]
        else:
            raise ParseError(f"Unexpected tracks response format: {type(data)}")

        return [parse_track(track_data, idx) for idx, track_data in enumerate(tracks_data)]

    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse tracks response: {e}") from e


def parse_clip(data: Dict[str, Any], track_index: int) -> ClipInfo:
    """Parse a single clip from Audacity JSON data.

    Args:
        data: Dictionary containing clip data.
        track_index: Index of the track containing this clip.

    Returns:
        ClipInfo object with parsed data.

    Raises:
        ParseError: If required fields are missing or invalid.
    """
    try:
        return ClipInfo(
            track=track_index,
            start=float(data.get("start", 0.0)),
            end=float(data.get("end", 0.0)),
            color=int(data.get("color", data.get("colorIndex", 0))),
            name=data.get("name"),
        )
    except (KeyError, ValueError, TypeError) as e:
        raise ParseError(f"Failed to parse clip: {e}") from e


def parse_clips(response: str) -> List[ClipInfo]:
    """Parse clips from GetInfo Type=Clips response.

    Args:
        response: Raw JSON string from GetInfo: Type=Clips command.

    Returns:
        List of ClipInfo objects.

    Raises:
        ParseError: If parsing fails.

    Example:
        >>> conn = AudacityConnection()
        >>> response = conn.send_command("GetInfo: Type=Clips Format=JSON")
        >>> clips = parse_clips(response)
        >>> for clip in clips:
        ...     print(f"Clip on track {clip.track}: {clip.duration}s")
    """
    try:
        data = parse_json_response(response)

        # Handle different possible response formats
        if isinstance(data, list):
            clips_data = data
        elif isinstance(data, dict) and "clips" in data:
            clips_data = data["clips"]
        else:
            raise ParseError(f"Unexpected clips response format: {type(data)}")

        clips = []
        for clip_data in clips_data:
            # Clips may include track index in the data
            track_idx = clip_data.get("track", 0)
            clips.append(parse_clip(clip_data, track_idx))

        return clips

    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse clips response: {e}") from e


def parse_envelopes(response: str) -> List[EnvelopePoint]:
    """Parse envelope points from GetInfo Type=Envelopes response.

    Args:
        response: Raw JSON string from GetInfo: Type=Envelopes command.

    Returns:
        List of EnvelopePoint objects.

    Raises:
        ParseError: If parsing fails.

    Example:
        >>> conn = AudacityConnection()
        >>> response = conn.send_command("GetInfo: Type=Envelopes Format=JSON")
        >>> points = parse_envelopes(response)
        >>> for point in points:
        ...     print(f"Envelope at {point.time}s: {point.value}")
    """
    try:
        data = parse_json_response(response)

        # Handle different possible response formats
        if isinstance(data, list):
            points_data = data
        elif isinstance(data, dict) and "envelope" in data:
            points_data = data["envelope"]
        elif isinstance(data, dict) and "points" in data:
            points_data = data["points"]
        else:
            raise ParseError(f"Unexpected envelopes response format: {type(data)}")

        points = []
        for point_data in points_data:
            if isinstance(point_data, dict):
                points.append(
                    EnvelopePoint(
                        time=float(point_data.get("t", point_data.get("time", 0.0))),
                        value=float(point_data.get("v", point_data.get("value", 1.0))),
                    )
                )
            elif isinstance(point_data, (list, tuple)) and len(point_data) >= 2:
                # Handle [time, value] format
                points.append(EnvelopePoint(time=float(point_data[0]), value=float(point_data[1])))

        return points

    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse envelopes response: {e}") from e


def parse_project_info(response: str) -> ProjectInfo:
    """Parse project info from GetInfo Type=Project response.

    Args:
        response: Raw JSON string from GetInfo: Type=Project command.

    Returns:
        ProjectInfo object with parsed data.

    Raises:
        ParseError: If parsing fails.

    Example:
        >>> conn = AudacityConnection()
        >>> response = conn.send_command("GetInfo: Type=Project Format=JSON")
        >>> info = parse_project_info(response)
        >>> print(f"Project has {info.num_tracks} tracks")
    """
    try:
        data = parse_json_response(response)

        if not isinstance(data, dict):
            raise ParseError(f"Expected dict for project info, got {type(data)}")

        return ProjectInfo(
            project_rate=int(data.get("rate", data.get("projectRate", 44100))),
            num_tracks=int(data.get("numTracks", data.get("trackCount", 0))),
            num_wave_tracks=int(data.get("numWaveTracks", 0)),
            num_label_tracks=int(data.get("numLabelTracks", 0)),
            focus_track=int(data.get("focusTrack", data.get("focusedTrack", -1))),
            selection_start=float(data.get("selectionStart", data.get("sel0", 0.0))),
            selection_end=float(data.get("selectionEnd", data.get("sel1", 0.0))),
        )

    except ParseError:
        raise
    except (KeyError, ValueError, TypeError) as e:
        raise ParseError(f"Failed to parse project info: {e}") from e

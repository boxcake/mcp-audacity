"""Tests for audacity.models module."""

import pytest
from audacity.models import Label, TimeRange, TrackInfo, TrackKind, ProjectInfo


class TestTimeRange:
    """Tests for TimeRange model."""

    def test_create_valid_range(self):
        """Test creating a valid time range."""
        tr = TimeRange(start=0.0, end=10.0)
        assert tr.start == 0.0
        assert tr.end == 10.0
        assert tr.duration == 10.0

    def test_equal_start_end(self):
        """Test time range with equal start and end (point)."""
        tr = TimeRange(start=5.0, end=5.0)
        assert tr.duration == 0.0

    def test_invalid_range_raises_error(self):
        """Test that invalid range raises ValueError."""
        with pytest.raises(ValueError, match="Start time.*must be <= end time"):
            TimeRange(start=10.0, end=5.0)

    def test_overlaps(self):
        """Test overlap detection."""
        tr1 = TimeRange(start=0.0, end=10.0)
        tr2 = TimeRange(start=5.0, end=15.0)
        tr3 = TimeRange(start=15.0, end=20.0)

        assert tr1.overlaps(tr2)
        assert tr2.overlaps(tr1)
        assert not tr1.overlaps(tr3)
        assert not tr3.overlaps(tr1)


class TestLabel:
    """Tests for Label model."""

    def test_create_point_label(self):
        """Test creating a point label."""
        label = Label(index=0, text="Marker", start=5.0, end=5.0)
        assert label.text == "Marker"
        assert label.is_point_label
        assert not label.is_region_label
        assert label.duration == 0.0

    def test_create_region_label(self):
        """Test creating a region label."""
        label = Label(index=1, text="Segment", start=5.0, end=10.0)
        assert label.text == "Segment"
        assert not label.is_point_label
        assert label.is_region_label
        assert label.duration == 5.0

    def test_as_time_range(self):
        """Test converting label to TimeRange."""
        label = Label(index=0, text="Test", start=2.0, end=8.0)
        tr = label.as_time_range()
        assert tr.start == 2.0
        assert tr.end == 8.0


class TestTrackInfo:
    """Tests for TrackInfo model."""

    def test_create_track(self):
        """Test creating a track."""
        track = TrackInfo(
            index=0,
            name="Audio Track",
            kind=TrackKind.WAVE,
            start_time=0.0,
            end_time=30.0,
            channels=2,
            sample_rate=48000,
        )
        assert track.name == "Audio Track"
        assert track.duration == 30.0
        assert track.is_stereo
        assert not track.is_mono

    def test_mono_track(self):
        """Test mono track properties."""
        track = TrackInfo(
            index=0,
            name="Mono",
            kind=TrackKind.WAVE,
            start_time=0.0,
            end_time=10.0,
            channels=1,
        )
        assert track.is_mono
        assert not track.is_stereo


class TestProjectInfo:
    """Tests for ProjectInfo model."""

    def test_create_project_info(self):
        """Test creating project info."""
        info = ProjectInfo(
            project_rate=44100,
            num_tracks=5,
            num_wave_tracks=3,
            num_label_tracks=2,
        )
        assert info.project_rate == 44100
        assert info.num_tracks == 5

    def test_has_selection(self):
        """Test selection detection."""
        # No selection
        info1 = ProjectInfo(
            project_rate=44100,
            num_tracks=1,
            selection_start=0.0,
            selection_end=0.0,
        )
        assert not info1.has_selection

        # Has selection
        info2 = ProjectInfo(
            project_rate=44100,
            num_tracks=1,
            selection_start=5.0,
            selection_end=10.0,
        )
        assert info2.has_selection
        assert info2.selection_duration == 5.0

    def test_get_selection_range(self):
        """Test getting selection as TimeRange."""
        info = ProjectInfo(
            project_rate=44100,
            num_tracks=1,
            selection_start=2.0,
            selection_end=8.0,
        )
        tr = info.get_selection_range()
        assert tr is not None
        assert tr.start == 2.0
        assert tr.end == 8.0

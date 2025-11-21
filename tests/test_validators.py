"""Tests for audacity.validators module."""

import pytest
from audacity.models import AudioFormat, SelectionMode
from audacity.validators import (
    ValidationError,
    validate_audio_format,
    validate_gain,
    validate_label_text,
    validate_pan,
    validate_selection_mode,
    validate_time_range,
    validate_track_number,
)


class TestValidateTimeRange:
    """Tests for validate_time_range function."""

    def test_valid_range(self):
        """Test valid time range passes."""
        validate_time_range(0.0, 10.0)  # Should not raise

    def test_equal_start_end_allowed(self):
        """Test equal start/end is allowed by default."""
        validate_time_range(5.0, 5.0)  # Should not raise

    def test_equal_start_end_disallowed(self):
        """Test equal start/end can be disallowed."""
        with pytest.raises(ValidationError, match="must be <"):
            validate_time_range(5.0, 5.0, allow_equal=False)

    def test_invalid_range_raises_error(self):
        """Test invalid range raises ValidationError."""
        with pytest.raises(ValidationError, match="must be <= end time"):
            validate_time_range(10.0, 5.0)

    def test_negative_start_raises_error(self):
        """Test negative start time raises error."""
        with pytest.raises(ValidationError, match="Start time must be >="):
            validate_time_range(-1.0, 10.0)


class TestValidateTrackNumber:
    """Tests for validate_track_number function."""

    def test_valid_track_number(self):
        """Test valid track number passes."""
        validate_track_number(0)
        validate_track_number(5)

    def test_negative_track_raises_error(self):
        """Test negative track number raises error."""
        with pytest.raises(ValidationError, match="must be >="):
            validate_track_number(-1)

    def test_max_track_limit(self):
        """Test max track limit validation."""
        validate_track_number(3, max_track=5)  # Should not raise

        with pytest.raises(ValidationError, match="must be <="):
            validate_track_number(10, max_track=5)


class TestValidateGain:
    """Tests for validate_gain function."""

    def test_valid_gain(self):
        """Test valid gain values pass."""
        validate_gain(0.0)
        validate_gain(1.0)
        validate_gain(2.0)

    def test_negative_gain_raises_error(self):
        """Test negative gain raises error."""
        with pytest.raises(ValidationError, match="must be >="):
            validate_gain(-0.5)

    def test_excessive_gain_raises_error(self):
        """Test excessive gain raises error."""
        with pytest.raises(ValidationError, match="must be <="):
            validate_gain(20.0)


class TestValidatePan:
    """Tests for validate_pan function."""

    def test_valid_pan(self):
        """Test valid pan values pass."""
        validate_pan(-1.0)  # Full left
        validate_pan(0.0)  # Center
        validate_pan(1.0)  # Full right

    def test_invalid_pan_raises_error(self):
        """Test invalid pan values raise error."""
        with pytest.raises(ValidationError, match="between -1.0 and 1.0"):
            validate_pan(-1.5)

        with pytest.raises(ValidationError, match="between -1.0 and 1.0"):
            validate_pan(2.0)


class TestValidateAudioFormat:
    """Tests for validate_audio_format function."""

    def test_valid_formats(self):
        """Test valid format strings."""
        assert validate_audio_format("WAV") == AudioFormat.WAV
        assert validate_audio_format("MP3") == AudioFormat.MP3
        assert validate_audio_format("wav") == AudioFormat.WAV  # Case-insensitive

    def test_invalid_format_raises_error(self):
        """Test invalid format raises error."""
        with pytest.raises(ValidationError, match="Invalid audio format"):
            validate_audio_format("INVALID")


class TestValidateSelectionMode:
    """Tests for validate_selection_mode function."""

    def test_valid_modes(self):
        """Test valid mode strings."""
        assert validate_selection_mode("Set") == SelectionMode.SET
        assert validate_selection_mode("Add") == SelectionMode.ADD
        assert validate_selection_mode("set") == SelectionMode.SET  # Case-insensitive

    def test_invalid_mode_raises_error(self):
        """Test invalid mode raises error."""
        with pytest.raises(ValidationError, match="Invalid selection mode"):
            validate_selection_mode("Invalid")


class TestValidateLabelText:
    """Tests for validate_label_text function."""

    def test_valid_label_text(self):
        """Test valid label text passes."""
        validate_label_text("Chapter 1")
        validate_label_text("A" * 100)  # Long but under limit

    def test_empty_text_raises_error(self):
        """Test empty text raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_label_text("")

    def test_too_long_text_raises_error(self):
        """Test text exceeding max length raises error."""
        with pytest.raises(ValidationError, match="too long"):
            validate_label_text("A" * 300)

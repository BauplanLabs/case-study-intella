"""Test version information."""

from case_study_telemetry import __version__


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ == "0.1.0"

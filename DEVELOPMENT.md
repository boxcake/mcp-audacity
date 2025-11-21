# Development Guide

## Platform-Specific Named Pipes

The server automatically detects your operating system and uses the appropriate named pipe paths:

### Unix/Linux/macOS (FIFOs)
- **Command Pipe**: `/tmp/audacity_script_pipe.to.501`
- **Response Pipe**: `/tmp/audacity_script_pipe.from.501`
- These are FIFO (First In, First Out) special files created by Audacity
- Verification: `ls -l /tmp | grep audacity_script_pipe`

### Windows (Named Pipes)
- **Command Pipe**: `\\.\pipe\ToSrvPipe`
- **Response Pipe**: `\\.\pipe\FromSrvPipe`
- These are Windows named pipe objects created by Audacity
- No file system verification needed; pipes exist in the pipe namespace

### Environment Variable Override
You can override the defaults on any platform:

```bash
# Unix/Linux/macOS
export AUDACITY_PIPE_TO="/tmp/audacity_script_pipe.to.12345"
export AUDACITY_PIPE_FROM="/tmp/audacity_script_pipe.from.12345"

# Windows PowerShell
$env:AUDACITY_PIPE_TO = "\\.\pipe\CustomToSrvPipe"
$env:AUDACITY_PIPE_FROM = "\\.\pipe\CustomFromSrvPipe"
```

## Audacity Scripting Quick Reference

### Key Concepts

1. **Track Numbering**: Starts at 0 (first track is track 0)
2. **Pipe Protocol**: Commands sent with newline, single-line responses
3. **JSON Support**: `GetInfo` commands can return structured JSON
4. **No Undo**: Scripted commands don't appear in undo history
5. **Label-Based Analysis**: Many analyzers output results as labels
6. **Cross-Platform**: Named pipes work differently on Windows vs Unix-like systems

### Common Command Patterns

#### Label Operations

```python
# Add label at specific time on specific track
send_command("SelectTracks: Track=1 TrackCount=1")
send_command("SelectTime: Start=125.5 End=125.5")
send_command("AddLabel:")
send_command("SetLabel: Label=0 Text='Chapter 1'")

# Get all labels as JSON
labels = send_command("GetInfo: Type=Labels Format=JSON")

# Export labels
send_command("ExportLabels:")
```

#### Selection Commands

```python
# Select time range
send_command("SelectTime: Start=10.0 End=30.0")

# Select specific tracks
send_command("SelectTracks: Track=0 TrackCount=2 Mode=Set")

# Combined selection
send_command("Select: Track=1 Start=5.0 End=15.0")
```

#### Project Information

```python
# Get all track metadata
tracks = send_command("GetInfo: Type=Tracks Format=JSON")

# Get clip information
clips = send_command("GetInfo: Type=Clips Format=JSON")

# Get envelope points
envelopes = send_command("GetInfo: Type=Envelopes Format=JSON")
```

#### Audio Analysis

```python
# Detect clipped audio (creates labels)
send_command("SelectAll:")
send_command("FindClipping:")
clipping_labels = send_command("GetInfo: Type=Labels Format=JSON")

# Auto-label speech segments
send_command("SelectAll:")
send_command("LabelSounds: threshold=-30 sil-dur=0.5 snd-dur=0.1")
speech_labels = send_command("GetInfo: Type=Labels Format=JSON")

# Find beats
send_command("SelectAll:")
send_command("BeatFinder: thresval=65")
beat_labels = send_command("GetInfo: Type=Labels Format=JSON")
```

#### Audio Effects

```python
# Normalize audio levels
send_command("SelectAll:")
send_command("Normalize:")

# Remove silence automatically
send_command("SelectAll:")
send_command("TruncateSilence:")

# Adjust volume
send_command("Select: Track=0 Start=0 End=10")
send_command("Amplify: Ratio=1.5")
```

### Important Scripting Commands for Future Implementation

#### Label Management
- `AddLabel:` - Create label at cursor/selection
- `SetLabel: Label=<n> Text='<text>' Start=<time> End=<time>` - Modify label
- `GetInfo: Type=Labels Format=JSON` - Get all labels as JSON
- `ImportLabels:` - Import labels from file
- `ExportLabels:` - Export labels to file

#### Selection
- `SelectTime: Start=<time> End=<time>` - Select time range
- `SelectTracks: Track=<n> TrackCount=<count> Mode=<Set|Add>` - Select tracks
- `Select: Track=<n> Start=<time> End=<time>` - Combined selection

#### Analysis
- `FindClipping:` - Detect clipped audio (creates labels)
- `LabelSounds: threshold=<db> sil-dur=<sec>` - Auto-label speech segments
- `BeatFinder: thresval=<percent>` - Find beats

#### Track Information
- `GetInfo: Type=Tracks Format=JSON` - Get all track metadata
- `GetInfo: Type=Clips Format=JSON` - Get clip information
- `GetInfo: Type=Envelopes Format=JSON` - Get envelope points

## Development Environment Setup

### Prerequisites
- Python 3.13 or newer
- `uv` package manager
- Audacity 3.x or later

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd mcp-audacity

# Create virtual environment
uv venv --python=python3.13
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx
```

### Running the Server

```bash
# From project directory with venv activated
uv run audacity_mcp_server.py
```

### Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "audacity": {
      "command": "/absolute/path/to/uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-audacity",
        "run",
        "audacity_mcp_server.py"
      ]
    }
  }
}
```

## Code Style Guidelines

### Python Style
- Follow PEP 8
- Maximum line length: 88 characters (Black standard)
- Use type hints everywhere
- Docstrings for all public APIs (Google or NumPy style)

### Type Hints
```python
from typing import Dict, List, Optional, Any, Tuple

def send_command(command: str) -> str:
    """Send command and return response."""
    ...

async def async_function() -> Optional[Dict[str, Any]]:
    """Example async function."""
    ...
```

### Docstring Format (Google Style)
```python
def send_command(command: str, timeout: float = 0.2) -> str:
    """Send a command to Audacity via mod-script-pipe.

    Args:
        command: The command string to send to Audacity.
        timeout: Time to wait for response in seconds.

    Returns:
        The response string from Audacity.

    Raises:
        ConnectionError: If pipe is not connected.
        TimeoutError: If response takes too long.
    """
    ...
```

## Testing

### Manual Testing Checklist
- [ ] Server starts without errors
- [ ] Connects to Audacity successfully
- [ ] Can execute basic commands (PlayStop, Pause)
- [ ] Can query project info (GetInfo)
- [ ] Handles errors gracefully
- [ ] Cleans up resources on shutdown

### Audacity Setup for Testing
1. Open Audacity
2. Go to Preferences → Scripting
3. Enable mod-script-pipe
4. Restart Audacity
5. Verify pipes: `ls -l /tmp | grep audacity_script_pipe`
6. Create a test project with audio

### Common Test Commands
```bash
# Check if pipes exist
ls -l /tmp | grep audacity_script_pipe

# Check pipe permissions
stat /tmp/audacity_script_pipe.to.501

# Monitor pipe activity (in another terminal)
tail -f /tmp/audacity_script_pipe.to.501
```

## Troubleshooting

### Connection Issues

**Error: Failed to connect to Audacity: [Errno 61] Connection refused** (macOS/Linux)
- Ensure mod-script-pipe is enabled in Audacity preferences
- Check that Audacity is running
- Verify pipe files exist: `ls /tmp/audacity_script_pipe*`
- Check for number suffixes on pipe names (e.g., `.to.12345`)
- Set environment variables if pipes have different numbers

**Error: [WinError 2] The system cannot find the file specified** (Windows)
- Ensure mod-script-pipe is enabled in Audacity preferences
- Check that Audacity is running
- Restart Audacity after enabling mod-script-pipe
- Verify Audacity version supports mod-script-pipe (3.x or later)

**Error: spawn uv ENOENT**
- Use absolute path to `uv` in Claude Desktop config
- Verify `uv` is installed: `which uv` (Unix) or `where uv` (Windows)

### Pipe Issues

**Pipes have number suffixes (macOS/Linux)**
- Use environment variables to specify the correct paths:
  ```bash
  export AUDACITY_PIPE_TO="/tmp/audacity_script_pipe.to.12345"
  export AUDACITY_PIPE_FROM="/tmp/audacity_script_pipe.from.12345"
  ```

**Permission denied on pipes (macOS/Linux)**
- Check pipe permissions: `ls -l /tmp/audacity_script_pipe*`
- Ensure user has read/write access
- Pipes should have permissions like `prw-------` (0600)

**Named pipe not found (Windows)**
- Ensure Audacity has been restarted after enabling mod-script-pipe
- Check Windows Event Viewer for Audacity errors
- Try running Audacity as Administrator (though normally not required)

## Future Enhancements (Phase 2)

These are ideas for Phase 2, DO NOT implement yet:

### High-Level Helpers
```python
# Label management helper
def create_chapter_marker(track: int, time: float, title: str) -> None:
    """Create a chapter marker at specific time."""
    ...

# Batch operations
def process_podcast(audio_file: str, chapters: List[Tuple[float, str]]) -> None:
    """Process podcast with chapter markers."""
    ...

# Analysis helpers
def detect_speech_regions(threshold: float = -30) -> List[Tuple[float, float]]:
    """Detect speech regions and return time ranges."""
    ...
```

### Configuration
- Environment variable support
- Config file support (TOML/YAML)
- Auto-detect pipe paths
- Retry configuration
- Timeout configuration

### Error Handling
- Retry logic for pipe operations
- Better error messages
- Command validation
- Response parsing/validation

### Testing
- Unit tests for connection management
- Integration tests with mock pipes
- Command validation tests
- Error handling tests

---

**Note**: This document is for reference during development. Focus on Phase 1 (code quality) before considering Phase 2 features.

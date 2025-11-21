# MCP Audacity Server - Claude Development Guide

## Project Overview

This is a forked version of the `mcp-audacity` project implementing a Model Context Protocol (MCP) server that connects to Audacity via its mod-script-pipe interface. The server exposes comprehensive Audacity scripting commands as MCP tool endpoints.

**Original Repository**: https://github.com/An-3/mcp-audacity
**License**: MIT
**Current Branch**: `claude/audacity-mcp-server-016xPNbiEcBRayJYy6FYtSQo`

## Current State

### Implemented Features
- ✅ Complete Audacity command set (167 commands) organized by category
- ✅ Named pipe communication with Audacity
- ✅ MCP server using FastMCP
- ✅ Robust connection management and error handling
- ✅ Comprehensive logging infrastructure
- ✅ Environment variable configuration
- ✅ Modular package structure with separated concerns
- ✅ Full type hints and documentation
- ✅ Custom exception classes

### File Structure (Post-Refactoring)
```
mcp-audacity/
├── audacity/                   # Audacity client package
│   ├── __init__.py            # Package exports
│   ├── client.py              # AudacityConnection class
│   ├── commands.py            # All 167 command definitions
│   └── exceptions.py          # Custom exceptions
├── audacity_mcp_server.py     # MCP server orchestration (~180 lines)
├── pyproject.toml             # Project configuration
├── README.md                  # User-facing documentation
├── CLAUDE.md                  # This file - development guide
├── DEVELOPMENT.md             # Technical reference
├── .gitignore                 # Python artifacts
└── uv.lock                    # Dependency lock file
```

### Technology Stack
- **Python**: 3.13+
- **Package Manager**: `uv`
- **Dependencies**: `mcp[cli]>=1.6.0`, `httpx>=0.28.1`
- **MCP Framework**: FastMCP from `mcp.server.fastmcp`
- **Code Quality**: ruff, mypy (configured in pyproject.toml)

## Phase 1: Code Quality Improvement ✅ COMPLETE

### Objectives

This phase focused on improving code quality WITHOUT adding new features. The goal was to establish a solid, well-documented foundation.

### Tasks Completed

#### 1. Type Hints & Documentation ✅
- ✅ Added complete type hints to all functions and methods
- ✅ Added comprehensive docstrings (Google style)
- ✅ Documented all parameters, return values, and exceptions
- ✅ Added module-level docstrings
- ✅ Added inline comments for complex logic

#### 2. Code Structure & Organization ✅
- ✅ Separated concerns into modular package structure
- ✅ Created `audacity` package with client, commands, exceptions modules
- ✅ Reduced server file from ~600 to ~180 lines
- ✅ Added constants for magic values (pipe paths, timeouts)
- ✅ Improved error handling with custom exceptions

#### 3. Resource Management ✅
- ✅ Ensured proper pipe cleanup in all code paths
- ✅ Added context manager support (`__enter__`, `__exit__`)
- ✅ Improved connection lifecycle management
- ✅ Verified async/await usage is correct

#### 4. Configuration ✅
- ✅ Made pipe paths configurable via environment variables
- ✅ Added configuration validation (pipe existence checks)
- ✅ Documented all configuration options

#### 5. Project Metadata ✅
- ✅ Updated `pyproject.toml` with complete metadata
- ✅ Added development dependencies (ruff, mypy, pytest)
- ✅ Added proper project description and keywords
- ✅ Configured linting and type checking tools

### Quality Standards Achieved

- ✅ All functions have type hints (100% coverage)
- ✅ All public functions/classes have docstrings (100% coverage)
- ✅ Maximum line length: 88 characters (Black formatter standard)
- ✅ Follows PEP 8 style guidelines
- ✅ Meaningful variable and function names throughout

### Success Criteria (All Met ✅)

1. ✅ All code has type hints and docstrings
2. ✅ Code follows PEP 8 and best practices
3. ✅ Server runs without errors
4. ✅ All existing functionality works
5. ✅ Code is more maintainable and documented
6. ✅ Clean commits created and pushed
7. ✅ README reflects all changes
8. ✅ Configuration is flexible (environment variables)
9. ✅ Error messages are clear and actionable
10. ✅ **BONUS:** Separated concerns into modular package structure

## Phase 2: High-Level Features & Testing (FUTURE - DO NOT START)

**Important:** All 167 Audacity scripting commands are already implemented as MCP endpoints!

Phase 2 focuses on building **higher-level abstractions** on top of the existing commands to make common workflows easier and safer.

### Objectives

#### 1. Response Parsing & Structured Data

**Problem:** Commands like `GetInfo` return raw JSON strings that need parsing.

**Solution:** Add helper functions that return structured data:

```python
# In audacity/helpers.py
def get_tracks_info() -> List[TrackInfo]:
    """Get all tracks with parsed metadata."""

def get_labels() -> List[Label]:
    """Get all labels as Label objects with .text, .start, .end."""

def get_project_info() -> ProjectInfo:
    """Get complete project information."""
```

#### 2. High-Level Workflow Helpers

**Problem:** Common operations require multiple command sequences.

**Solution:** Add workflow functions:

```python
def create_chapter_marker(track: int, time: float, title: str) -> None:
    """Create a labeled chapter marker (handles SelectTracks, SelectTime, AddLabel, SetLabel)."""

def detect_speech_segments(threshold_db: float = -30) -> List[TimeRange]:
    """Auto-detect speech regions and return structured time ranges."""

def apply_podcast_processing(
    normalize: bool = True,
    noise_reduction: bool = True,
    compress: bool = True
) -> None:
    """Apply standard podcast processing effects in the correct order."""
```

#### 3. Type-Safe Parameter Wrappers

**Problem:** Commands that take parameters are currently just strings.

**Solution:** Add typed wrappers for complex commands:

```python
def select_time_range(start: float, end: float, mode: str = "Set") -> str:
    """Type-safe wrapper for SelectTime command with validation."""

def export_audio(
    filename: str,
    format: AudioFormat,
    quality: int = 128
) -> str:
    """Type-safe wrapper for Export2 with path validation."""
```

#### 4. Parameter Validation

**Problem:** Invalid parameters only fail after sending to Audacity.

**Solution:** Validate before execution:

```python
# Validate track numbers exist
# Validate time ranges are valid (start < end, within project)
# Validate file paths before Import2/Export2
# Check format compatibility
# Provide clear error messages
```

#### 5. Testing Infrastructure

**Problem:** No automated tests yet.

**Solution:** Add comprehensive test suite:

- Unit tests for `audacity` package (with mock pipes)
- Integration tests with test fixtures
- Command validation tests
- Error handling tests
- Response parsing tests

### Phase 2 Deliverables

- [ ] `audacity/helpers.py` - High-level helper functions
- [ ] `audacity/parsers.py` - Response parsing utilities
- [ ] `audacity/models.py` - Data classes (Label, TrackInfo, etc.)
- [ ] `audacity/validators.py` - Parameter validation
- [ ] `tests/` directory with pytest suite
- [ ] Updated documentation with examples

### Success Criteria

Phase 2 is complete when:
1. ✅ Common workflows have high-level helper functions
2. ✅ GetInfo commands return parsed, structured data
3. ✅ Complex commands have type-safe wrappers
4. ✅ Parameters validated before execution
5. ✅ Test coverage > 80% for audacity package
6. ✅ All helpers documented with examples
7. ✅ Integration tests pass with real Audacity instance

**Wait for explicit approval before starting Phase 2.**

## Development Workflow

### Making Changes

1. Work on the designated branch: `claude/audacity-mcp-server-016xPNbiEcBRayJYy6FYtSQo`
2. Make incremental changes
3. Test after each major change
4. Create meaningful commits using conventional commit format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code improvements
   - `test:` for test additions

### Git Operations

**For git push:**
- Always use: `git push -u origin claude/audacity-mcp-server-016xPNbiEcBRayJYy6FYtSQo`
- Branch must start with 'claude/' and end with session ID
- Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s) on network errors

**For git fetch/pull:**
- Prefer: `git fetch origin claude/audacity-mcp-server-016xPNbiEcBRayJYy6FYtSQo`
- Retry with same backoff strategy on failures

### Testing the Server

```bash
# Activate environment
source .venv/bin/activate

# Run the server
uv run audacity_mcp_server.py

# Expected output:
# INFO - Audacity MCP server starting up
# INFO - Opened Audacity mod-script-pipe
# INFO - Connected to Audacity mod-script-pipe
```

## Important Notes

### Pipe Communication
- **Pipe Locations**: Default: `/tmp/audacity_script_pipe.to.501` and `.from.501`
  - May have different number suffixes on different systems
  - **Configurable** via `AUDACITY_PIPE_TO` and `AUDACITY_PIPE_FROM` environment variables
- **Protocol**: Commands sent with newline terminator
- **Timing**: 0.2s delay after sending command (configurable via `AUDACITY_COMMAND_TIMEOUT`)
- **Response**: Single-line response per command

### Audacity Setup
- Mod-script-pipe must be enabled in Audacity preferences
- Go to: Preferences → Scripting → Enable mod-script-pipe
- Restart Audacity after enabling
- Verify pipes exist: `ls -l /tmp | grep audacity_script_pipe`

### Known Issues (Post-Phase 1)
1. ~~Pipe paths are hardcoded~~ ✅ **Fixed:** Now configurable via environment variables
2. ~~`main.py` is a leftover test file~~ ✅ **Fixed:** Removed
3. ~~Error handling could be more robust~~ ✅ **Improved:** Custom exceptions and better error messages
4. No retry logic for pipe operations (could be added in Phase 2 if needed)
5. Limited validation of command responses (Phase 2: add parsers and validators)

## Key Resources

### Essential Documentation
- [Audacity Scripting Reference](https://manual.audacityteam.org/man/scripting_reference.html) - Complete command list
- [Audacity Scripting Overview](https://manual.audacityteam.org/man/scripting.html) - mod-script-pipe explained
- [Scriptables I Menu](https://manual.audacityteam.org/man/extra_menu_scriptables_i.html) - Common commands
- [Scriptables II Menu](https://manual.audacityteam.org/man/extra_menu_scriptables_ii.html) - Advanced commands
- [MCP Documentation](https://docs.claude.com/en/docs/mcp) - Model Context Protocol overview
- [MCP Python SDK](https://github.com/modelcontextprotocol) - Official implementations

### Command Categories
The server implements 150+ commands organized into:
- File operations (New, Open, Save, Export)
- Import (Audio, Labels, MIDI, Raw)
- Edit (Undo, Redo, Cut, Copy, Paste, etc.)
- Labels (Add, Edit, Import/Export)
- Selection (SelectAll, SelectNone, ZeroCross)
- View (Zoom, ShowClipping, MixerBoard)
- Transport (Play, Pause, Record, Scrub)
- Effects (Amplify, Normalize, NoiseReduction, etc.)
- Generate (Tone, Noise, Chirp, DTMF)
- Analyze (Contrast, PlotSpectrum)
- Tools (Macros, Screenshots)
- Track operations (Mute, Solo, Pan, Gain)
- Scriptables I & II (Advanced scripting commands)
- Help & Diagnostics

## Questions to Consider During Phase 1

While improving code quality, keep notes on:
- Are there code smells or anti-patterns?
- Is error handling robust enough?
- Are there security concerns?
- Could the code be more maintainable or testable?
- Are there missing abstractions that would help?
- Should command registration be more dynamic?
- Is the current architecture scalable?

## Success Criteria for Phase 1

Phase 1 is complete when:
1. ✅ All code has type hints and docstrings
2. ✅ Code follows PEP 8 and best practices
3. ✅ Server runs without errors
4. ✅ All existing functionality works
5. ✅ Code is more maintainable and documented
6. ✅ A clean commit has been created
7. ✅ README reflects any API changes
8. ✅ Configuration is more flexible
9. ✅ Error messages are clear and actionable

---

**REMEMBER**: Focus ONLY on Phase 1 (code quality improvement) for now. Do not add new features. We want a solid, well-documented foundation before extending functionality.

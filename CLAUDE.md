# MCP Audacity Server - Claude Development Guide

## Project Overview

This is a forked version of the `mcp-audacity` project implementing a Model Context Protocol (MCP) server that connects to Audacity via its mod-script-pipe interface. The server exposes comprehensive Audacity scripting commands as MCP tool endpoints.

**Original Repository**: https://github.com/An-3/mcp-audacity
**License**: MIT
**Current Branch**: `claude/audacity-mcp-server-016xPNbiEcBRayJYy6FYtSQo`

## Current State

### Implemented Features
- ✅ Complete Audacity command set (150+ commands) organized by category
- ✅ Named pipe communication with Audacity
- ✅ MCP server using FastMCP
- ✅ Basic connection management and error handling
- ✅ Logging infrastructure

### File Structure
- `audacity_mcp_server.py` - Main MCP server implementation
- `main.py` - Leftover test file (can be removed)
- `pyproject.toml` - Project configuration
- `README.md` - User-facing documentation
- `uv.lock` - Dependency lock file

### Technology Stack
- **Python**: 3.13+
- **Package Manager**: `uv`
- **Dependencies**: `mcp[cli]>=1.6.0`, `httpx>=0.28.1`
- **MCP Framework**: FastMCP from `mcp.server.fastmcp`

## Phase 1: Code Quality Improvement (CURRENT PRIORITY)

### Objectives

This phase focuses on improving code quality WITHOUT adding new features. The goal is to establish a solid, well-documented foundation.

### Tasks Checklist

#### 1. Type Hints & Documentation
- [ ] Add complete type hints to all functions and methods
- [ ] Add comprehensive docstrings (Google or NumPy style)
- [ ] Document all parameters, return values, and exceptions
- [ ] Add module-level docstring
- [ ] Add inline comments for complex logic

#### 2. Code Structure & Organization
- [ ] Review and improve class structure
- [ ] Extract repeated code into helper functions
- [ ] Add constants for magic values (pipe paths, timeouts)
- [ ] Consider separating concerns (MCP logic vs pipe communication)
- [ ] Improve error handling consistency

#### 3. Resource Management
- [ ] Ensure proper pipe cleanup in all code paths
- [ ] Review connection lifecycle management
- [ ] Check for potential race conditions
- [ ] Verify async/await usage is correct

#### 4. Configuration
- [ ] Make pipe paths configurable (environment variables)
- [ ] Add configuration validation
- [ ] Document configuration options

#### 5. Project Metadata
- [ ] Update `pyproject.toml` with complete metadata
- [ ] Add development dependencies (linting, testing)
- [ ] Add proper project description and keywords

### Quality Standards

- ✅ All functions must have type hints
- ✅ All public functions/classes must have docstrings
- ✅ Maximum line length: 88 characters (Black formatter standard)
- ✅ Follow PEP 8 style guidelines
- ✅ Meaningful variable and function names

### Testing Criteria

Before marking Phase 1 complete:
1. Server starts without errors
2. Can connect to Audacity with mod-script-pipe enabled
3. Existing MCP endpoints work correctly
4. Error messages are clear and helpful
5. Code passes basic linting (ruff/flake8/pylint)

## Phase 2: Feature Enhancement (FUTURE - DO NOT START)

This phase will focus on:
- Advanced label management features
- Track selection and manipulation helpers
- Analysis plugin wrappers
- Project information queries
- Enhanced error recovery

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
- **Pipe Locations**: `/tmp/audacity_script_pipe.to.501` and `.from.501`
  - May have different number suffixes on different systems
  - Currently hardcoded - should be made configurable
- **Protocol**: Commands sent with newline terminator
- **Timing**: 0.2s delay after sending command
- **Response**: Single-line response per command

### Audacity Setup
- Mod-script-pipe must be enabled in Audacity preferences
- Go to: Preferences → Scripting → Enable mod-script-pipe
- Restart Audacity after enabling
- Verify pipes exist: `ls -l /tmp | grep audacity_script_pipe`

### Known Issues
1. Pipe paths are hardcoded (should be configurable)
2. `main.py` is a leftover test file
3. Error handling could be more robust
4. No retry logic for pipe operations
5. Limited validation of command responses

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

# Audacity MCP Server

This project implements an MCP (Model Context Protocol) server that connects to Audacity via its mod‑script‑pipe interface. Using named pipes, the server sends commands to Audacity and receives responses, allowing you to control Audacity (for example, starting/stopping recording or playback) through MCP endpoints. The server can be launched using the `uv` tool and integrated with the Claude Desktop client.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation and Setup](#installation-and-setup)
4. [Configuring Audacity](#configuring-audacity)
5. [Server Configuration](#server-configuration)
6. [Usage](#usage)
7. [Configuration with Claude Desktop Client](#configuration-with-claude-desktop-client)
8. [Troubleshooting](#troubleshooting)
9. [License](#license)

## Features

- **Audacity Integration:** Communicates with Audacity using the mod‑script‑pipe interface via named pipes.
- **Comprehensive Command Set:** Provides 150+ MCP tool endpoints for all Audacity scripting commands including:
  - File operations (New, Open, Save, Export)
  - Transport controls (Play, Pause, Record)
  - Audio editing (Cut, Copy, Paste, Trim)
  - Effects (Normalize, Amplify, NoiseReduction, etc.)
  - Labels and track management
  - Analysis tools and generators
- **Configurable:** Support for environment variables to customize pipe paths and timeouts.
- **Type-Safe:** Full type hints and comprehensive documentation.
- **uv Integration:** Uses the `uv` tool to run the MCP server.
- **Claude Desktop Compatibility:** Can be configured to launch using the Claude Desktop client.

## Requirements

- **Audacity:** Version 3.x or later is recommended.
- **Python:** Version 3.13 or newer.
- **uv Tool:** For running the MCP server.
- **mod‑script‑pipe:** Audacity’s remote control/scripting interface must be enabled.
- **Python Dependencies:** The project requires the following packages:
  - `httpx`
  - `mcp[cli]`

## Installation-and-Setup

1. **Clone or Download the Project:**

   ```
   git clone <repository-url>
   cd mcp-audacity
   ```

2. **Set Up a Virtual Environment:**
- **Use the uv tool to create and activate the virtual environment:**

   ```
   uv venv --python=python3.13
   source .venv/bin/activate
   ```

3. **Install Dependencies**
- Install the required dependencies with:
   ```
   uv add "mcp[cli]" httpx
   ```

4. **Verify the Project Structure**
Make sure your project folder contains at least:
- `audacity_mcp_server.py` (the main MCP server script)
- `pyproject.toml` (project configuration)
- `CLAUDE.md` and `DEVELOPMENT.md` (development documentation)
- (Optional) `claude_desktop_config.json` (for integration with the Claude Desktop client)

## Configuring-Audacity
- For the MCP server to connect with Audacity, its mod‑script‑pipe interface must be enabled.

**Step 1: Enable mod‑script‑pipe in Audacity**
- Open Audacity.
 - Open Preferences:
 - On macOS: Click Audacity > Preferences…
 - On Windows: Click Edit > Preferences…
- Navigate to the Scripting/Remote Control Section:
- Look for an option such as Enable mod‑script‑pipe or Enable Remote Control/Scripting.
- Enable the feature.
- Restart Audacity.

**Step 2: Verify Named Pipes**
- Audacity should create two named pipes (by default on macOS/Linux):
 - Command pipe: `/tmp/audacity_script_pipe.to.%number%`
 - Response pipe: `/tmp/audacity_script_pipe.from.%number%`
- Run the following command in a terminal to verify:

   ```
   ls -l /tmp | grep audacity_script_pipe
   ```
> If you see extra numbers or characters (e.g. `/tmp/audacity_script_pipe.to.1234`), see the [Server Configuration](#server-configuration) section below to customize the pipe paths.

## Server Configuration

The server can be configured using environment variables to match your system's pipe paths and adjust behavior.

### Environment Variables

- **`AUDACITY_PIPE_TO`**: Path to the command pipe (default: `/tmp/audacity_script_pipe.to.501`)
- **`AUDACITY_PIPE_FROM`**: Path to the response pipe (default: `/tmp/audacity_script_pipe.from.501`)
- **`AUDACITY_COMMAND_TIMEOUT`**: Time in seconds to wait after sending a command (default: `0.2`)

### Setting Environment Variables

**On macOS/Linux:**

```bash
# Set for current session
export AUDACITY_PIPE_TO="/tmp/audacity_script_pipe.to.12345"
export AUDACITY_PIPE_FROM="/tmp/audacity_script_pipe.from.12345"

# Then run the server
uv run audacity_mcp_server.py
```

**For Claude Desktop Client:**

Add environment variables to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "audacity": {
      "command": "/absolute/path/to/uv",
      "args": [
        "--directory",
        "/path/to/mcp-audacity",
        "run",
        "audacity_mcp_server.py"
      ],
      "env": {
        "AUDACITY_PIPE_TO": "/tmp/audacity_script_pipe.to.12345",
        "AUDACITY_PIPE_FROM": "/tmp/audacity_script_pipe.from.12345"
      }
    }
  }
}
```

## Usage
- Running the MCP Server from the Command Line
**1. Navigate to Your Project Directory:**

   ```MacOS
   cd /%path_to_project%/mcp-audacity
   ```

**2. Activate the Virtual Environment (if not already activated):**

   ```MacOS
   source .venv/bin/activate
   ```

**3. Launch the Server with the uv Tool:**

   ```bash
   uv run audacity_mcp_server.py
   ```

You should see log messages such as:

   ```
   INFO - Audacity MCP server starting up
   INFO - Looking for pipes: TO=/tmp/audacity_script_pipe.to.501, FROM=/tmp/audacity_script_pipe.from.501
   INFO - Opened Audacity mod-script-pipe: /tmp/audacity_script_pipe.to.501
   INFO - Connected to Audacity mod-script-pipe
   ```

## MCP Endpoints

The MCP server exposes 150+ tool endpoints that can be invoked by an MCP client, organized into the following categories:

- **File Operations**: New, Open, Close, Save, SaveAs, ExportAudio, etc.
- **Import**: ImportAudio, ImportLabels, ImportMIDI, ImportRaw
- **Edit**: Undo, Redo, Cut, Copy, Paste, Delete, Duplicate, Silence, Trim
- **Labels**: AddLabel, EditLabels, PasteNewLabel, TypeToCreateLabel
- **Selection**: SelectAll, SelectNone, ZeroCross, StoreCursorPosition
- **View**: ZoomIn, ZoomOut, ZoomSel, ShowClipping, MixerBoard
- **Transport**: PlayStop, Pause, Record1stChoice, Record2ndChoice, Scrub
- **Effects**: Amplify, Normalize, NoiseReduction, Compressor, Echo, Reverb, FadeIn, FadeOut, and 20+ more
- **Generate**: Tone, Noise, Chirp, DtmfTones, Pluck, RhythmTrack
- **Analyze**: ContrastAnalyser, PlotSpectrum, ManageAnalyzers
- **Tools**: ManageMacros, ApplyMacro, Screenshot
- **Track Controls**: TrackMute, TrackSolo, TrackGain, TrackPan, TrackMove operations
- **Scriptables I & II**: Advanced commands like Select, SetTrackStatus, GetInfo, SetLabel, Export2, Import2

All endpoints are defined in `audacity_mcp_server.py` and correspond to Audacity's scripting commands. For detailed command documentation, see the [Audacity Scripting Reference](https://manual.audacityteam.org/man/scripting_reference.html).

## Configuration with Claude Desktop Client
- If you want to run your server via the Claude Desktop client, update your `claude_desktop_config.json` to point to this project. For example:

  ```
  {
    "mcpServers": {
        "audacity": {
        "command": "/%absolute_path_to_ev%/.local/bin/uv",
        "args": [
            "--directory",
            "/Users/andriiboboshko/mcp-audacity",
            "run",
            "audacity_mcp_pipe.py"
        ]
        }
    }
  }
  ```
  
- Ensure the paths match your project location and that your virtual environment is set up correctly.

## License
This project is provided under MIT License. Feel free to modify and distribute as needed.

## Troubleshooting

**Error: spawn uv ENOENT**
- I found that it can occur when MCP server tried to launch uv and despite uv was in my PATH it did not create a process. It fixed when I added an absolute path to uv in the Claude Desktop config `claude_desktop_config.json`.

**ERROR - Failed to connect to Audacity: [Errno 61] Connection refused**
- I've got this error because Audacity created command and response pipes files in the /tmp folder with some numbers:

   ```
   /tmp/audacity_script_pipe.to.501
   /tmp/audacity_script_pipe.from.501
   ```
- After updating the code with the particular number it worked. 

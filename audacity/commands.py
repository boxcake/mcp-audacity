"""Audacity scripting command definitions.

This module contains all available Audacity scripting commands organized
by functional category. Each command is defined as a tuple of
(command_id, description).

For complete documentation on Audacity scripting commands, see:
https://manual.audacityteam.org/man/scripting_reference.html
"""

from typing import List, Tuple

# Type alias for command definitions
CommandDef = Tuple[str, str]

# File Operations
FILE_COMMANDS: List[CommandDef] = [
    ("New", "New: Create a new empty project window."),
    ("Open", "Open: Open an audio file, list of files, or project."),
    ("Close", "Close: Close the current project window."),
    ("Save", "Save: Save the current project."),
    ("SaveAs", "SaveAs: Save the current project under a new name."),
    ("SaveCopy", "SaveCopy: Save a lossless copy of the project."),
    ("SaveCompressed", "SaveCompressed: Save a compressed copy of the project."),
    ("ExportAudio", "ExportAudio: Export audio files in various formats."),
    ("Print", "Print: Print all waveforms in the current project."),
    ("Exit", "Exit: Close all project windows and exit Audacity."),
]

# Import Operations
IMPORT_COMMANDS: List[CommandDef] = [
    ("ImportAudio", "ImportAudio: Import an audio file as a new track."),
    ("ImportLabels", "ImportLabels: Import labels into the project."),
    ("ImportMIDI", "ImportMIDI: Import a MIDI file into a note track."),
    ("ImportRaw", "ImportRaw: Import raw audio data without headers."),
]

# Edit Operations
EDIT_COMMANDS: List[CommandDef] = [
    ("Undo", "Undo: Undo the most recent editing action."),
    ("Redo", "Redo: Redo the most recent undone action."),
    ("Cut", "Cut: Remove the selected audio and place it on the clipboard."),
    ("Delete", "Delete: Remove the selected audio without copying it."),
    ("Copy", "Copy: Copy the selected audio to the clipboard."),
    ("Paste", "Paste: Insert clipboard contents at the selection."),
    ("Duplicate", "Duplicate: Duplicate the current selection as a new clip."),
    ("EditMetaData", "EditMetaData: Edit the metadata for a track."),
    ("SplitCut", "SplitCut: Split the current clip and remove audio to right of the cut."),
    ("SplitDelete", "SplitDelete: Remove selected audio without shifting remaining audio."),
    ("Silence", "Silence: Replace selected audio with silence."),
    ("Trim", "Trim: Delete all audio except for the selected portion."),
]

# Label Operations
LABEL_COMMANDS: List[CommandDef] = [
    ("EditLabels", "EditLabels: Open the Label Editor dialog."),
    ("AddLabel", "AddLabel: Create a new label at the selection."),
    ("PasteNewLabel", "PasteNewLabel: Paste text from the clipboard into a new label."),
    ("TypeToCreateLabel", "TypeToCreateLabel: Create a label by typing (if enabled)."),
]

# Selection Commands
SELECT_COMMANDS: List[CommandDef] = [
    ("SelectAll", "SelectAll: Select all audio in all tracks."),
    ("SelectNone", "SelectNone: Deselect all audio in all tracks."),
    ("StoreCursorPosition", "StoreCursorPosition: Store current cursor position for later selection."),
    ("SelCursorStoredCursor", "SelCursorStoredCursor: Select audio from current cursor to stored position."),
    ("ZeroCross", "ZeroCross: Adjust selection boundaries to the nearest zero crossing."),
]

# View Commands
VIEW_COMMANDS: List[CommandDef] = [
    ("UndoHistory", "UndoHistory: Display the undo history window."),
    ("Karaoke", "Karaoke: Display the karaoke window."),
    ("MixerBoard", "MixerBoard: Switch to the mixer board view."),
    ("ShowExtraMenus", "ShowExtraMenus: Toggle extra menus display."),
    ("ShowClipping", "ShowClipping: Toggle display of clipping in the waveform."),
    ("ZoomIn", "ZoomIn: Zoom in horizontally."),
    ("ZoomNormal", "ZoomNormal: Reset zoom to the default view."),
    ("ZoomOut", "ZoomOut: Zoom out horizontally."),
    ("ZoomSel", "ZoomSel: Zoom to fill the current selection."),
    ("ZoomToggle", "ZoomToggle: Toggle between two preset zoom levels."),
]

# Transport Commands
TRANSPORT_COMMANDS: List[CommandDef] = [
    ("PlayStop", "PlayStop: Toggle playback on and off."),
    ("PlayStopSelect", "PlayStopSelect: Play/Stop and update cursor position."),
    ("Pause", "Pause: Temporarily pause playback or recording."),
    ("Record1stChoice", "Record1stChoice: Start recording on the currently selected track."),
    ("Record2ndChoice", "Record2ndChoice: Start recording on a new track."),
    ("TimerRecord", "TimerRecord: Open Timer Record dialog."),
    ("PunchAndRoll", "PunchAndRoll: Start punch and roll recording."),
    ("Scrub", "Scrub: Scrub through audio."),
    ("Seek", "Seek: Jump to a specified position in the audio."),
]

# Effect Commands
EFFECT_COMMANDS: List[CommandDef] = [
    ("Amplify", "Amplify: Adjust the volume of the selected audio."),
    ("AutoDuck", "AutoDuck: Automatically lower one track's volume when another is active."),
    ("BassAndTreble", "BassAndTreble: Adjust bass and treble levels."),
    ("ChangePitch", "ChangePitch: Change pitch without changing tempo."),
    ("ChangeSpeed", "ChangeSpeed: Change both speed and pitch."),
    ("ChangeTempo", "ChangeTempo: Change tempo without affecting pitch."),
    ("ClickRemoval", "ClickRemoval: Remove clicks from the audio."),
    ("Compressor", "Compressor: Compress the dynamic range."),
    ("Distortion", "Distortion: Apply a distortion effect."),
    ("Delay", "Delay: Apply a delay effect."),
    ("Echo", "Echo: Apply an echo effect."),
    ("FadeIn", "FadeIn: Apply a linear fade-in."),
    ("FadeOut", "FadeOut: Apply a linear fade-out."),
    ("FilterCurve", "FilterCurve: Adjust frequency response using a custom curve."),
    ("GraphicEq", "GraphicEq: Apply a graphic equalizer effect."),
    ("Invert", "Invert: Invert the polarity of the audio."),
    ("LoudnessNormalization", "LoudnessNormalization: Normalize perceived loudness."),
    ("NoiseReduction", "NoiseReduction: Reduce background noise."),
    ("Normalize", "Normalize: Normalize audio volume levels."),
    ("Paulstretch", "Paulstretch: Apply an extreme time-stretch effect."),
    ("Phaser", "Phaser: Apply a phaser effect."),
    ("Repair", "Repair: Attempt to fix short clicks or glitches."),
    ("Repeat", "Repeat: Repeat the selected audio a specified number of times."),
    ("Reverb", "Reverb: Apply a reverberation effect."),
    ("Reverse", "Reverse: Reverse the selected audio."),
    ("SlidingStretch", "SlidingStretch: Continuously change tempo and/or pitch."),
    ("TruncateSilence", "TruncateSilence: Remove or compress silences."),
    ("Wahwah", "Wahwah: Apply a wahwah effect."),
]

# Generate Commands
GENERATE_COMMANDS: List[CommandDef] = [
    ("Chirp", "Chirp: Generate a chirp tone with adjustable frequency and amplitude."),
    ("DtmfTones", "DtmfTones: Generate dual-tone multi-frequency (DTMF) tones."),
    ("Noise", "Noise: Generate noise (white, pink, or brown)."),
    ("Tone", "Tone: Generate a tone of specific frequency, amplitude, and waveform."),
    ("Nyquist", "Nyquist: Open the Nyquist scripting prompt."),
    ("Pluck", "Pluck: Generate a plucked tone effect."),
    ("RhythmTrack", "RhythmTrack: Generate a rhythmic track at a specified tempo."),
    ("RissetDrum", "RissetDrum: Generate a continuously evolving drum sound."),
]

# Analyze Commands
ANALYZE_COMMANDS: List[CommandDef] = [
    ("ManageAnalyzers", "ManageAnalyzers: Open the analyzers plugin manager."),
    ("ContrastAnalyser", "ContrastAnalyser: Analyze the contrast between foreground and background audio."),
    ("PlotSpectrum", "PlotSpectrum: Plot the frequency spectrum of the selected audio."),
]

# Tools Commands
TOOLS_COMMANDS: List[CommandDef] = [
    ("ManageTools", "ManageTools: Open the tools/effects/generators manager."),
    ("ManageMacros", "ManageMacros: Create or edit macros."),
    ("ApplyMacro", "ApplyMacro: Apply a defined macro to the project."),
    ("Screenshot", "Screenshot: Capture a screenshot of Audacity (short format)."),
]

# Transport Options
TRANSPORT_OPTIONS_COMMANDS: List[CommandDef] = [
    ("SoundActivationLevel", "SoundActivationLevel: Set the threshold level for sound-activated recording."),
    ("SoundActivation", "SoundActivation: Toggle sound-activated recording."),
]

# Device Commands
DEVICE_COMMANDS: List[CommandDef] = [
    ("InputDevice", "InputDevice: Open the recording device selection dialog."),
    ("OutputDevice", "OutputDevice: Open the playback device selection dialog."),
    ("ChangeAudio", "ChangeAudio: Open the audio host/interface selection dialog."),
]

# Selection Tools
SELECTION_COMMANDS: List[CommandDef] = [
    ("SnapToOff", "SnapToOff: Disable snapping for selections."),
    ("SnapToNearest", "SnapToNearest: Snap selections to the nearest time unit."),
    ("SnapToPrior", "SnapToPrior: Snap selections to the previous time unit."),
    ("SelStart", "SelStart: Set selection from cursor to start of track."),
    ("SelEnd", "SelEnd: Set selection from cursor to end of track."),
]

# Timeline Commands
TIMELINE_COMMANDS: List[CommandDef] = [
    ("MinutesandSeconds", "MinutesandSeconds: Set timeline format to minutes and seconds."),
    ("BeatsandMeasures", "BeatsandMeasures: Set timeline format to beats and measures."),
]

# Focus Commands
FOCUS_COMMANDS: List[CommandDef] = [
    ("PrevFrame", "PrevFrame: Move focus backward from toolbars to tracks."),
    ("NextFrame", "NextFrame: Move focus forward from toolbars to tracks."),
    ("PrevTrack", "PrevTrack: Focus the previous track."),
    ("NextTrack", "NextTrack: Focus the next track."),
    ("FirstTrack", "FirstTrack: Focus the first track."),
    ("LastTrack", "LastTrack: Focus the last track."),
    ("ShiftUp", "ShiftUp: Move focus upward and select the previous track."),
    ("ShiftDown", "ShiftDown: Move focus downward and select the next track."),
    ("Toggle", "Toggle: Toggle focus on the current track."),
]

# Cursor Commands
CURSOR_COMMANDS: List[CommandDef] = [
    ("CursorLeft", "CursorLeft: Move the cursor left by one unit."),
    ("CursorRight", "CursorRight: Move the cursor right by one unit."),
    ("CursorShortJumpLeft", "CursorShortJumpLeft: Move the cursor 1 second left."),
    ("CursorShortJumpRight", "CursorShortJumpRight: Move the cursor 1 second right."),
    ("CursorLongJumpLeft", "CursorLongJumpLeft: Move the cursor 15 seconds left."),
    ("CursorLongJumpRight", "CursorLongJumpRight: Move the cursor 15 seconds right."),
]

# Track Commands
TRACK_COMMANDS: List[CommandDef] = [
    ("TrackPan", "TrackPan: Open the pan dialog for the focused track."),
    ("TrackPanLeft", "TrackPanLeft: Pan the focused track to the left."),
    ("TrackPanRight", "TrackPanRight: Pan the focused track to the right."),
    ("TrackGain", "TrackGain: Open the gain dialog for the focused track."),
    ("TrackGainInc", "TrackGainInc: Increase the gain on the focused track."),
    ("TrackGainDec", "TrackGainDec: Decrease the gain on the focused track."),
    ("TrackMute", "TrackMute: Toggle mute on the focused track."),
    ("TrackSolo", "TrackSolo: Toggle solo on the focused track."),
    ("TrackClose", "TrackClose: Close the focused track."),
    ("TrackMoveUp", "TrackMoveUp: Move the focused track up one position."),
    ("TrackMoveDown", "TrackMoveDown: Move the focused track down one position."),
    ("TrackMoveTop", "TrackMoveTop: Move the focused track to the top."),
    ("TrackMoveBottom", "TrackMoveBottom: Move the focused track to the bottom."),
]

# Scriptables I - Advanced scripting commands
SCRIPTABLES_I_COMMANDS: List[CommandDef] = [
    ("Select", "Select: Modify selection based on parameters."),
    ("SetTrackStatus", "SetTrackStatus: Set properties (name, selected, focused) for a track."),
    ("SetTrackAudio", "SetTrackAudio: Set audio properties (mute, solo, gain, pan) for a track."),
]

# Scriptables II - More advanced scripting commands
SCRIPTABLES_II_COMMANDS: List[CommandDef] = [
    ("SetPreference", "SetPreference: Set a preference value (with optional reload)."),
    ("GetPreference", "GetPreference: Retrieve a preference value."),
    ("SetClip", "SetClip: Modify properties (color, start time) of a clip."),
    ("SetEnvelope", "SetEnvelope: Adjust the envelope value at a specified time."),
    ("SetLabel", "SetLabel: Modify an existing label."),
    ("SetProject", "SetProject: Change project window properties (size, position, caption)."),
    ("GetInfo", "GetInfo: Retrieve project information in a specified format."),
    ("Message", "Message: Send a test message to Audacity."),
    ("Help", "Help: Get help information for a command."),
    ("Import2", "Import2: Import data from a file (using a filename)."),
    ("Export2", "Export2: Export selected audio to a file with detailed options."),
    ("OpenProject2", "OpenProject2: Open a project given a filename."),
    ("SaveProject2", "SaveProject2: Save the current project with additional options."),
    ("Drag", "Drag: Simulate a mouse drag for UI interactions."),
    ("CompareAudio", "CompareAudio: Compare audio regions between tracks."),
    ("Screenshot", "Screenshot: Capture a screenshot (short format)."),
]

# Help Menu Commands
HELP_MENU_COMMANDS: List[CommandDef] = [
    ("QuickHelp", "QuickHelp: Display a brief help message."),
    ("Manual", "Manual: Open Audacity's manual in the default web browser."),
    ("Updates", "Updates: Check for updates for Audacity."),
    ("About", "About: Display information about Audacity."),
]

# Diagnostics Commands
DIAGNOSTICS_COMMANDS: List[CommandDef] = [
    ("DeviceInfo", "DeviceInfo: Show technical information about audio devices."),
    ("MidiDeviceInfo", "MidiDeviceInfo: Show information about MIDI devices."),
    ("Log", "Log: Open the Audacity log window."),
    ("CrashReport", "CrashReport: Generate a support report for troubleshooting."),
    ("CheckDeps", "CheckDeps: Check dependencies for the current project."),
]

# No Menu Commands
NO_MENU_COMMANDS: List[CommandDef] = [
    ("PrevWindow", "PrevWindow: Navigate to the previous window."),
    ("NextWindow", "NextWindow: Navigate to the next window."),
]

# All commands combined for easy access
ALL_COMMANDS: List[CommandDef] = (
    FILE_COMMANDS
    + IMPORT_COMMANDS
    + EDIT_COMMANDS
    + LABEL_COMMANDS
    + SELECT_COMMANDS
    + VIEW_COMMANDS
    + TRANSPORT_COMMANDS
    + EFFECT_COMMANDS
    + GENERATE_COMMANDS
    + ANALYZE_COMMANDS
    + TOOLS_COMMANDS
    + TRANSPORT_OPTIONS_COMMANDS
    + DEVICE_COMMANDS
    + SELECTION_COMMANDS
    + TIMELINE_COMMANDS
    + FOCUS_COMMANDS
    + CURSOR_COMMANDS
    + TRACK_COMMANDS
    + SCRIPTABLES_I_COMMANDS
    + SCRIPTABLES_II_COMMANDS
    + HELP_MENU_COMMANDS
    + DIAGNOSTICS_COMMANDS
    + NO_MENU_COMMANDS
)

# Command categories for organization
COMMAND_CATEGORIES = {
    "File Operations": FILE_COMMANDS,
    "Import": IMPORT_COMMANDS,
    "Edit": EDIT_COMMANDS,
    "Labels": LABEL_COMMANDS,
    "Selection": SELECT_COMMANDS,
    "View": VIEW_COMMANDS,
    "Transport": TRANSPORT_COMMANDS,
    "Effects": EFFECT_COMMANDS,
    "Generate": GENERATE_COMMANDS,
    "Analyze": ANALYZE_COMMANDS,
    "Tools": TOOLS_COMMANDS,
    "Transport Options": TRANSPORT_OPTIONS_COMMANDS,
    "Devices": DEVICE_COMMANDS,
    "Selection Tools": SELECTION_COMMANDS,
    "Timeline": TIMELINE_COMMANDS,
    "Focus": FOCUS_COMMANDS,
    "Cursor": CURSOR_COMMANDS,
    "Track Controls": TRACK_COMMANDS,
    "Scriptables I": SCRIPTABLES_I_COMMANDS,
    "Scriptables II": SCRIPTABLES_II_COMMANDS,
    "Help": HELP_MENU_COMMANDS,
    "Diagnostics": DIAGNOSTICS_COMMANDS,
    "Other": NO_MENU_COMMANDS,
}

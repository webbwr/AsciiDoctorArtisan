# Pane Maximize/Minimize Feature Guide

## Overview
AsciiDoc Artisan now includes pane maximize functionality, allowing you to focus on either the editor or preview pane by maximizing it to fill the entire window.

## Features

### Visual Controls
- **Maximize Buttons**: Each pane has a ⬜ button in its toolbar
- **Editor Pane**: Top-left shows "Editor" label with maximize button
- **Preview Pane**: Top-left shows "Preview" label with maximize button
- **Button States**:
  - ⬜ = Normal state (click to maximize)
  - ⬛ = Maximized state (click to restore)

### How to Use

#### Using Buttons
1. Click the ⬜ button in the Editor toolbar to maximize the editor
2. Click the ⬜ button in the Preview toolbar to maximize the preview
3. When maximized, click the ⬛ button to restore normal view

#### Using Keyboard Shortcuts
- **Ctrl+Shift+E**: Toggle maximize editor pane
- **Ctrl+Shift+R**: Toggle maximize preview pane

#### Using Menu
- **View → Maximize Editor**: Toggle editor maximization
- **View → Maximize Preview**: Toggle preview maximization

## Behavior

### When Maximizing
- The selected pane expands to fill the entire window
- The other pane is temporarily hidden
- The maximize button changes to a restore icon (⬛)
- The opposite pane's maximize button is disabled
- Status bar shows which pane is maximized

### When Restoring
- Both panes return to their previous sizes
- If no previous size is saved, panes split equally
- Both maximize buttons are re-enabled
- Status bar confirms view is restored

## Use Cases

### Focus on Writing
- Maximize the editor when you need to focus on writing content
- Useful for long documents or complex code
- No distractions from the preview

### Focus on Reading
- Maximize the preview to read rendered content
- Great for reviewing documentation
- Perfect for checking formatting

### Quick Toggle
- Use keyboard shortcuts for rapid switching
- Quickly check preview then return to editing
- Efficient workflow for iterative writing

## Technical Details
- Splitter sizes are preserved when maximizing
- State is maintained during the session
- Works seamlessly with synchronized scrolling
- Compatible with all theme modes
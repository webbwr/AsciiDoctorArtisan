# Synchronized Scrolling Feature Guide

## Overview
The AsciiDoc Artisan now includes synchronized scrolling between the editor and preview panes. This feature helps maintain visual alignment between your source code and the rendered output.

## How to Use

### Enabling/Disabling
- Go to **View → Synchronized Scrolling** in the menu
- The feature is enabled by default
- A checkmark indicates when it's active
- Status bar shows confirmation when toggling

### How It Works
- Scrolling in the editor automatically scrolls the preview to the same relative position
- Scrolling in the preview automatically scrolls the editor
- The synchronization is percentage-based, so it works with documents of different lengths
- The feature prevents recursive scroll events to ensure smooth operation

## Testing the Feature

1. **Open a document** with enough content to scroll (Markdown, AsciiDoc, etc.)
2. **Verify synchronization** is enabled (View → Synchronized Scrolling should be checked)
3. **Scroll in the editor** - watch the preview follow along
4. **Scroll in the preview** - watch the editor follow along
5. **Toggle the feature off** and verify independent scrolling
6. **Toggle it back on** and verify synchronization resumes

## Benefits
- Easier navigation in long documents
- Maintains context between source and rendered output
- Helps identify which source text produces which rendered content
- Useful for proofreading and editing

## Technical Implementation
- Uses Qt's scroll bar signals for real-time synchronization
- Calculates relative scroll positions as percentages
- Includes safeguards against infinite scroll loops
- Maintains state across document switches
#!/bin/bash
# Grandmaster TechWriter (TW) aliases for current project
# Source this file: source .claude/skills/aliases.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

alias tw="$SCRIPT_DIR/scripts/tw"
alias techwriter="$SCRIPT_DIR/scripts/tw"
alias grade5="$SCRIPT_DIR/scripts/tw"

echo "TW aliases loaded:"
echo "  tw, techwriter, grade5"
echo "Usage: tw check README.md"

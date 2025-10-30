#!/bin/bash
# Query Security Audit Logs
#
# This script provides convenient queries for security audit logs.
# It assumes logs are written to a file or can be accessed via journalctl.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage
usage() {
    cat <<EOF
Usage: $0 [COMMAND] [OPTIONS]

Query security audit logs for credential operations.

COMMANDS:
    all                 Show all security audit entries
    store               Show all store_key operations
    get                 Show all get_key operations
    delete              Show all delete_key operations
    check               Show all check_key operations
    failures            Show all failed operations
    service <name>      Show operations for specific service
    user <username>     Show operations by specific user
    today               Show today's operations
    last <N>            Show last N audit entries (default: 50)

OPTIONS:
    -h, --help          Show this help message

EXAMPLES:
    $0 all                          # Show all audit logs
    $0 failures                     # Show only failed operations
    $0 service anthropic_api_key    # Show logs for Anthropic service
    $0 user webbp                   # Show logs by user 'webbp'
    $0 today                        # Show today's audit logs
    $0 last 100                     # Show last 100 entries

NOTES:
    - Logs are searched in application log files
    - Log format: SECURITY_AUDIT: timestamp=... user=... action=... service=... success=...
    - All times are in UTC (ISO 8601 format)

EOF
    exit 1
}

# Find log files
find_log_files() {
    # Look for common log locations
    local log_files=()

    # Check application-specific log locations
    if [ -f "$PROJECT_DIR/asciidoc_artisan.log" ]; then
        log_files+=("$PROJECT_DIR/asciidoc_artisan.log")
    fi

    # Check user log directory
    if [ -d "$HOME/.local/share/AsciiDocArtisan" ]; then
        find "$HOME/.local/share/AsciiDocArtisan" -name "*.log" 2>/dev/null | while read -r f; do
            log_files+=("$f")
        done
    fi

    # Check temp directory
    if [ -d "/tmp" ]; then
        find "/tmp" -name "asciidoc_artisan*.log" -user "$USER" 2>/dev/null | while read -r f; do
            log_files+=("$f")
        done
    fi

    # If no files found, use stdin or suggest creating logs
    if [ ${#log_files[@]} -eq 0 ]; then
        echo -e "${YELLOW}No log files found. Searching system logs...${NC}" >&2
        # Try journalctl if available
        if command -v journalctl &> /dev/null; then
            journalctl --user -g "SECURITY_AUDIT" -n 1000 --no-pager 2>/dev/null || true
        fi
    else
        cat "${log_files[@]}"
    fi
}

# Query functions
query_all() {
    find_log_files | grep "SECURITY_AUDIT:" | tail -n "${1:-1000}"
}

query_store() {
    find_log_files | grep "SECURITY_AUDIT:" | grep "action=store_key"
}

query_get() {
    find_log_files | grep "SECURITY_AUDIT:" | grep "action=get_key"
}

query_delete() {
    find_log_files | grep "SECURITY_AUDIT:" | grep "action=delete_key"
}

query_check() {
    find_log_files | grep "SECURITY_AUDIT:" | grep "action=check_key"
}

query_failures() {
    find_log_files | grep "SECURITY_AUDIT:" | grep "success=False"
}

query_service() {
    local service="$1"
    find_log_files | grep "SECURITY_AUDIT:" | grep "service=$service"
}

query_user() {
    local username="$1"
    find_log_files | grep "SECURITY_AUDIT:" | grep "user=$username"
}

query_today() {
    local today=$(date -u +%Y-%m-%d)
    find_log_files | grep "SECURITY_AUDIT:" | grep "timestamp=$today"
}

query_last() {
    local n="${1:-50}"
    find_log_files | grep "SECURITY_AUDIT:" | tail -n "$n"
}

# Parse command line
if [ $# -eq 0 ]; then
    usage
fi

COMMAND="$1"
shift

case "$COMMAND" in
    all)
        echo -e "${GREEN}All Security Audit Entries:${NC}"
        query_all "$@"
        ;;
    store)
        echo -e "${GREEN}Store Key Operations:${NC}"
        query_store
        ;;
    get)
        echo -e "${GREEN}Get Key Operations:${NC}"
        query_get
        ;;
    delete)
        echo -e "${GREEN}Delete Key Operations:${NC}"
        query_delete
        ;;
    check)
        echo -e "${GREEN}Check Key Operations:${NC}"
        query_check
        ;;
    failures)
        echo -e "${RED}Failed Operations:${NC}"
        query_failures
        ;;
    service)
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: service name required${NC}" >&2
            usage
        fi
        echo -e "${GREEN}Operations for service '$1':${NC}"
        query_service "$1"
        ;;
    user)
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: username required${NC}" >&2
            usage
        fi
        echo -e "${GREEN}Operations by user '$1':${NC}"
        query_user "$1"
        ;;
    today)
        echo -e "${GREEN}Today's Operations:${NC}"
        query_today
        ;;
    last)
        echo -e "${GREEN}Last ${1:-50} Operations:${NC}"
        query_last "$@"
        ;;
    -h|--help)
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}" >&2
        usage
        ;;
esac

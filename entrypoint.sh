#!/bin/sh
set -eu

if [ $# -lt 1 ]; then
    echo "usage: $0 <db-url> [schema] [dbupgrade options...]" >&2
    exit 1
fi

DB_URL="$1"
shift

SCHEMA="${DBUPGRADE_SCHEMA:-}"
if [ $# -gt 0 ]; then
    case "$1" in
        -*) ;;
        *)
            SCHEMA="$1"
            shift
            ;;
    esac
fi

if [ -z "$SCHEMA" ]; then
    echo "error: no schema given and no default schema set (DBUPGRADE_SCHEMA)" >&2
    exit 1
fi

exec dbupgrade "$SCHEMA" "$DB_URL" "${DBUPGRADE_SCRIPT_PATH:-/app/migrations}" "$@"

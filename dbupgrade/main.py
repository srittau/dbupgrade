from __future__ import annotations

import json
import logging
import sys
from typing import Any

from .args import Arguments, parse_args
from .files import FileInfo
from .result import UpgradeResult
from .upgrade import db_upgrade
from .version import version_info_from_args


def main() -> None:
    try:
        args = parse_args(sys.argv)
        _configure_logging(args)
        result = db_upgrade(
            args.schema,
            args.db_url,
            args.script_path,
            version_info_from_args(args),
        )
        if args.json:
            _print_json(result)
        if not result.success:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


def _configure_logging(args: Arguments) -> None:
    log_level = logging.INFO
    if args.json:
        log_level = logging.ERROR
    elif args.quiet:
        log_level = logging.WARNING
    logging.basicConfig(level=log_level)


def _print_json(result: UpgradeResult) -> None:
    j: dict[str, Any] = {
        "success": result.success,
        "oldVersion": {
            "version": result.old_version.version,
            "apiLevel": result.old_version.api_level,
        },
        "newVersion": {
            "version": result.new_version.version,
            "apiLevel": result.new_version.api_level,
        },
        "appliedScripts": [
            _json_script(script) for script in result.applied_scripts
        ],
    }
    if result.failed_script:
        j["failedScript"] = _json_script(result.failed_script)
    print(json.dumps(j))


def _json_script(script: FileInfo) -> dict[str, Any]:
    return {
        "filename": script.filename,
        "version": script.version,
        "apiLevel": script.api_level,
    }

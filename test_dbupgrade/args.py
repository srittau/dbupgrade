from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from dbupgrade.args import parse_args

_DEFAULT_ARGS = ["script", "schema", "url", "dir"]


class TestParseArgs:
    def test_help(self) -> None:
        out = StringIO()
        with pytest.raises(SystemExit):
            with redirect_stdout(out):
                parse_args(["script", "--help"])
        assert out.getvalue().startswith("usage: script")

    def test_no_options(self) -> None:
        args = parse_args(_DEFAULT_ARGS)
        assert args.schema == "schema"
        assert args.db_url == "url"
        assert args.script_path == "dir"
        assert args.api_level is None
        assert args.max_version is None
        assert not args.ignore_api_level
        assert not args.quiet
        assert not args.json

    def test_simple_options(self) -> None:
        args = parse_args(_DEFAULT_ARGS + ["-q", "--json"])
        assert args.quiet
        assert args.json

    def test_small_l_option(self) -> None:
        args = parse_args(["script", "-l", "44", "schema", "url", "dir"])
        assert not args.ignore_api_level
        assert args.api_level == 44

    def test_small_l_option__no_argument(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(["script", "schema", "url", "dir", "-l"])

    def test_big_l_option(self) -> None:
        args = parse_args(["script", "-L", "schema", "url", "dir"])
        assert args.api_level is None
        assert args.ignore_api_level

    def test_big_and_small_l_option(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(
                    ["script", "-L", "-l", "25", "schema", "url", "dir"]
                )

    def test_small_m_option(self) -> None:
        args = parse_args(["script", "-m", "10", "schema", "url", "dir"])
        assert args.max_version == 10

    def test_small_m_option__without_version(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(["script", "-m", "schema", "url", "dir"])

    def test_small_m_option__invalid_version(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(["script", "-m", "INVALID", "schema", "url", "dir"])

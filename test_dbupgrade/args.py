from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from dbupgrade.args import parse_args


class TestParseArgs:
    def test_help(self) -> None:
        out = StringIO()
        with pytest.raises(SystemExit):
            with redirect_stdout(out):
                parse_args(["script", "--help"])
        assert out.getvalue().startswith("usage: script")

    def test_no_options(self) -> None:
        args = parse_args(["script", "schema", "url", "dir"])
        assert args.schema == "schema"
        assert args.db_url == "url"
        assert args.script_path == "dir"
        assert not args.quiet
        assert not args.has_explicit_api_level
        assert not args.ignore_api_level
        assert not args.has_max_version

    def test_small_q_option(self) -> None:
        args = parse_args(["script", "-q", "schema", "url", "dir"])
        assert args.quiet

    def test_small_l_option(self) -> None:
        args = parse_args(["script", "-l", "44", "schema", "url", "dir"])
        assert args.has_explicit_api_level
        assert not args.ignore_api_level
        assert args.api_level == 44

    def test_small_l_option__no_argument(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(["script", "schema", "url", "dir", "-l"])

    def test_big_l_option(self) -> None:
        args = parse_args(["script", "-L", "schema", "url", "dir"])
        assert not args.has_explicit_api_level
        assert args.ignore_api_level

    def test_big_and_small_l_option(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(
                    ["script", "-L", "-l", "25", "schema", "url", "dir"]
                )

    def test_small_m_option(self) -> None:
        args = parse_args(["script", "-m", "10", "schema", "url", "dir"])
        assert args.has_max_version
        assert args.max_version == 10

    def test_small_m_option__without_version(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(["script", "-m", "schema", "url", "dir"])

    def test_small_m_option__invalid_version(self) -> None:
        with pytest.raises(SystemExit):
            with redirect_stderr(StringIO()):
                parse_args(["script", "-m", "INVALID", "schema", "url", "dir"])

import sys

from io import StringIO
from typing import cast

from asserts import assert_false, assert_true, assert_equal, assert_raises

from dectest import TestCase, test, before

from dbupgrade.args import parse_args


class ParseArgsTest(TestCase):
    @before
    def setup_streams(self) -> None:
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    @test
    def help(self) -> None:
        with assert_raises(SystemExit):
            parse_args(["script", "--help"])
        output = cast(StringIO, sys.stdout).getvalue()
        assert_true(output.startswith("usage: script"))

    @test
    def no_options(self) -> None:
        args = parse_args(["script", "schema", "url", "dir"])
        assert_equal("schema", args.schema)
        assert_equal("url", args.db_url)
        assert_equal("dir", args.script_path)
        assert_false(args.has_explicit_api_level)
        assert_false(args.ignore_api_level)
        assert_false(args.has_max_version)

    @test
    def small_l_option(self) -> None:
        args = parse_args(["script", "-l", "44", "schema", "url", "dir"])
        assert_true(args.has_explicit_api_level)
        assert_false(args.ignore_api_level)
        assert_equal(44, args.api_level)

    @test
    def small_l_option__no_argument(self) -> None:
        with assert_raises(SystemExit):
            parse_args(["script", "schema", "url", "dir", "-l"])

    @test
    def big_l_option(self) -> None:
        args = parse_args(["script", "-L", "schema", "url", "dir"])
        assert_false(args.has_explicit_api_level)
        assert_true(args.ignore_api_level)

    @test
    def big_and_small_l_option(self) -> None:
        with assert_raises(SystemExit):
            parse_args(["script", "-L", "-l", "25", "schema", "url", "dir"])

    @test
    def small_m_option(self) -> None:
        args = parse_args(["script", "-m", "10", "schema", "url", "dir"])
        assert_true(args.has_max_version)
        assert_equal(10, args.max_version)

    @test
    def small_m_option__without_version(self) -> None:
        with assert_raises(SystemExit):
            parse_args(["script", "-m", "schema", "url", "dir"])

    @test
    def small_m_option__invalid_version(self) -> None:
        with assert_raises(SystemExit):
            parse_args(["script", "-m", "INVALID", "schema", "url", "dir"])

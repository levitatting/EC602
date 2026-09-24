"""Tests for pygrep (EC602 HW1), covering SPEC cases 01 through 49.

How this works: each test runs your program as a separate process, the same
way the shell would, and looks at what came back: standard output, standard
error, and the exit status. That is all a test of a command-line program can
see, and it is all it needs.

Run the tests from the directory that contains pygrep.py:

    uv run --no-sync pytest

The grader runs this same file against other versions of pygrep.py, so do not
change how PROG is found.
"""

import os
import re
import subprocess
import sys

import pytest

PROG = os.path.abspath(os.environ.get("PYGREP", "pygrep.py"))


def run(*args, stdin=""):
    """Run pygrep with ARGS. Returns (stdout, stderr, exit status)."""
    r = subprocess.run([sys.executable, PROG, *args], input=stdin,
                       capture_output=True, text=True)
    return r.stdout, r.stderr, r.returncode


@pytest.fixture
def files(tmp_path):
    """Make a few input files in a fresh temporary directory, and work there.

    pytest passes in `tmp_path`, a new empty directory for each test. Add the
    files your tests need here, or create them inside individual tests.
    """
    contents = {
        "a.txt": "apple\nBanana\ncherry pie\n",
        "b.txt": "pie\napple pie\n",
        "literal.txt": "a.b\naXb\nabc\n",
        "blank_lines.txt": "pie\n\nAPPLE\n",
        "empty.txt": "",
        "no_newline.txt": "apple\ncherry pie",
        "repeated.txt": "pie pie\npie\nno\n",
        "spaces.txt": "  pie \t\nx\n",
    }
    for name, content in contents.items():
        (tmp_path / name).write_text(content, encoding="utf-8", newline="\n")
    (tmp_path / "directory").mkdir()
    assert not (tmp_path / "missing.txt").exists()
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(old)


def assert_file_error(err, name):
    """Check SPEC's single FILE_ERROR diagnostic without fixing OS wording."""
    prefix = f"pygrep: {name}: "
    assert err.startswith(prefix)
    assert err.endswith("\n")
    assert err.count("\n") == 1
    reason = err[len(prefix):-1]
    assert re.fullmatch(r"[^\r\n]+", reason)
    assert re.search(r"\S", reason)
    assert "traceback" not in err.casefold()


def assert_cli_error(err):
    """Check argparse usage/error content and return its diagnostic text."""
    assert re.search(r"\busage\s*:", err, re.IGNORECASE)
    diagnostic = re.search(r"\berror\s*:\s*(\S.*)", err,
                           re.IGNORECASE | re.DOTALL)
    assert diagnostic is not None
    assert "traceback" not in err.casefold()
    return diagnostic.group(1)


def test_01_match_prints_selected_line(files):
    """SPEC 01: Print the matching line with its terminating LF."""
    out, err, code = run("pie", "a.txt")
    assert out == "cherry pie\n"
    assert err == ""
    assert code == 0


def test_02_no_match_exits_with_one(files):
    """SPEC 02: No selection produces empty streams and status 1."""
    out, err, code = run("zzz", "a.txt")
    assert out == ""
    assert err == ""
    assert code == 1


def test_03_pattern_is_literal(files):
    """SPEC 03: A dot matches itself, not an arbitrary character."""
    out, err, code = run(".", "literal.txt")
    assert out == "a.b\n"
    assert err == ""
    assert code == 0


def test_04_ignore_case_preserves_output(files):
    """SPEC 04: Ignore case for matching while preserving printed case."""
    out, err, code = run("-i", "banana", "a.txt")
    assert out == "Banana\n"
    assert err == ""
    assert code == 0


def test_05_invert_line_selection(files):
    """SPEC 05: Inversion selects the nonmatching lines in input order."""
    out, err, code = run("-v", "pie", "a.txt")
    assert out == "apple\nBanana\n"
    assert err == ""
    assert code == 0


def test_06_number_original_line(files):
    """SPEC 06: Number the selected line by its original position."""
    out, err, code = run("-n", "pie", "a.txt")
    assert out == "3:cherry pie\n"
    assert err == ""
    assert code == 0


def test_07_prefix_multiple_files(files):
    """SPEC 07: Prefix every selected line when given multiple files."""
    out, err, code = run("pie", "a.txt", "b.txt")
    assert out == "a.txt:cherry pie\nb.txt:pie\nb.txt:apple pie\n"
    assert err == ""
    assert code == 0


def test_08_prefix_files_and_restart_line_numbers(files):
    """SPEC 08: Combine filename and line prefixes; restart per file."""
    out, err, code = run("-n", "pie", "a.txt", "b.txt")
    assert out == "a.txt:3:cherry pie\nb.txt:1:pie\nb.txt:2:apple pie\n"
    assert err == ""
    assert code == 0


def test_09_count_selected_lines_per_file(files):
    """SPEC 09: Print a separate prefixed count for each file."""
    out, err, code = run("-c", "pie", "a.txt", "b.txt")
    assert out == "a.txt:1\nb.txt:2\n"
    assert err == ""
    assert code == 0


def test_10_count_suppresses_line_numbers(files):
    """SPEC 10: Count mode takes precedence over a later -n flag."""
    out, err, code = run("-c", "-n", "pie", "a.txt", "b.txt")
    assert out == "a.txt:1\nb.txt:2\n"
    assert err == ""
    assert code == 0


def test_11_count_precedence_with_reversed_flags(files):
    """SPEC 11: Reversing -n and -c preserves count mode."""
    out, err, code = run("-n", "-c", "pie", "a.txt", "b.txt")
    assert out == "a.txt:1\nb.txt:2\n"
    assert err == ""
    assert code == 0


def test_12_list_selected_files_once(files):
    """SPEC 12: List each selected filename exactly once."""
    out, err, code = run("-l", "pie", "a.txt", "b.txt")
    assert out == "a.txt\nb.txt\n"
    assert err == ""
    assert code == 0


def test_13_file_list_overrides_count(files):
    """SPEC 13: File-list mode takes precedence over a later -c flag."""
    out, err, code = run("-l", "-c", "pie", "a.txt", "b.txt")
    assert out == "a.txt\nb.txt\n"
    assert err == ""
    assert code == 0


def test_14_file_list_precedence_with_reversed_flags(files):
    """SPEC 14: Reversing -c and -l preserves file-list mode."""
    out, err, code = run("-c", "-l", "pie", "a.txt", "b.txt")
    assert out == "a.txt\nb.txt\n"
    assert err == ""
    assert code == 0


def test_15_file_list_suppresses_line_numbers(files):
    """SPEC 15: File-list mode omits selected text and line numbers."""
    out, err, code = run("-l", "-n", "pie", "a.txt", "b.txt")
    assert out == "a.txt\nb.txt\n"
    assert err == ""
    assert code == 0


def test_16_zero_count_exits_with_one(files):
    """SPEC 16: Printing a zero count does not imply a selection."""
    out, err, code = run("-c", "zzz", "a.txt")
    assert out == "0\n"
    assert err == ""
    assert code == 1


def test_17_empty_pattern_selects_blank_lines(files):
    """SPEC 17: An empty pattern selects every existing line."""
    out, err, code = run("", "blank_lines.txt")
    assert out == "pie\n\nAPPLE\n"
    assert err == ""
    assert code == 0


def test_18_inverted_empty_pattern_selects_nothing(files):
    """SPEC 18: Inverting an empty pattern selects no lines."""
    out, err, code = run("-v", "", "blank_lines.txt")
    assert out == ""
    assert err == ""
    assert code == 1


def test_19_empty_file_has_no_match(files):
    """SPEC 19: An empty file has no line to select."""
    out, err, code = run("pie", "empty.txt")
    assert out == ""
    assert err == ""
    assert code == 1


def test_20_empty_file_count_is_zero(files):
    """SPEC 20: Count an empty file as zero and exit with status 1."""
    out, err, code = run("-c", "pie", "empty.txt")
    assert out == "0\n"
    assert err == ""
    assert code == 1


def test_21_empty_pattern_does_not_invent_lines(files):
    """SPEC 21: An empty pattern still selects nothing in an empty file."""
    out, err, code = run("", "empty.txt")
    assert out == ""
    assert err == ""
    assert code == 1


def test_22_unterminated_line_gets_output_newline(files):
    """SPEC 22: Add LF when printing a selected final line without LF."""
    out, err, code = run("pie", "no_newline.txt")
    assert out == "cherry pie\n"
    assert err == ""
    assert code == 0


def test_23_number_unterminated_final_line(files):
    """SPEC 23: Preserve the final line's position and add its output LF."""
    out, err, code = run("-n", "pie", "no_newline.txt")
    assert out == "2:cherry pie\n"
    assert err == ""
    assert code == 0


def test_24_missing_file_reports_error(files):
    """SPEC 24: A missing file produces one file diagnostic and status 2."""
    out, err, code = run("pie", "missing.txt")
    assert out == ""
    assert_file_error(err, "missing.txt")
    assert code == 2


def test_25_directory_reports_file_error(files):
    """SPEC 25: A directory operand is a file error, not an empty file."""
    out, err, code = run("pie", "directory")
    assert out == ""
    assert_file_error(err, "directory")
    assert code == 2


def test_26_continue_after_initial_missing_file(files):
    """SPEC 26: Continue after an error and count all operands for prefixes."""
    out, err, code = run("pie", "missing.txt", "a.txt")
    assert out == "a.txt:cherry pie\n"
    assert_file_error(err, "missing.txt")
    assert code == 2


def test_27_continue_after_middle_error(files):
    """SPEC 27: Preserve matches on both sides of an error and status 2."""
    out, err, code = run("pie", "a.txt", "missing.txt", "b.txt")
    assert out == "a.txt:cherry pie\nb.txt:pie\nb.txt:apple pie\n"
    assert_file_error(err, "missing.txt")
    assert code == 2


def test_28_error_overrides_no_selection(files):
    """SPEC 28: A file error takes precedence over no selected lines."""
    out, err, code = run("zzz", "a.txt", "missing.txt", "b.txt")
    assert out == ""
    assert_file_error(err, "missing.txt")
    assert code == 2


def test_29_count_omits_failed_file_and_continues(files):
    """SPEC 29: Omit the failed file's count and count subsequent files."""
    out, err, code = run("-c", "pie", "missing.txt", "a.txt", "b.txt")
    assert out == "a.txt:1\nb.txt:2\n"
    assert_file_error(err, "missing.txt")
    assert code == 2


def test_30_file_list_continues_after_error(files):
    """SPEC 30: List later matching files after a middle file error."""
    out, err, code = run("-l", "pie", "a.txt", "missing.txt", "b.txt")
    assert out == "a.txt\nb.txt\n"
    assert_file_error(err, "missing.txt")
    assert code == 2


def test_31_read_standard_input(files):
    """SPEC 31: Read stdin when no file operand is supplied."""
    out, err, code = run("pie", stdin="apple\nBanana\ncherry pie\n")
    assert out == "cherry pie\n"
    assert err == ""
    assert code == 0


def test_32_number_standard_input_lines(files):
    """SPEC 32: Number stdin lines without adding a filename prefix."""
    out, err, code = run("-n", "pie", stdin="apple\nBanana\ncherry pie\n")
    assert out == "3:cherry pie\n"
    assert err == ""
    assert code == 0


def test_33_count_standard_input_lines(files):
    """SPEC 33: Print an unprefixed count for standard input."""
    out, err, code = run("-c", "pie", stdin="apple\nBanana\ncherry pie\n")
    assert out == "1\n"
    assert err == ""
    assert code == 0


def test_34_list_standard_input_label(files):
    """SPEC 34: Use the required label when listing selected stdin."""
    out, err, code = run("-l", "pie", stdin="apple\nBanana\ncherry pie\n")
    assert out == "(standard input)\n"
    assert err == ""
    assert code == 0


def test_35_empty_standard_input_selects_nothing(files):
    """SPEC 35: Empty stdin has no selected line and exits with status 1."""
    out, err, code = run("pie", stdin="")
    assert out == ""
    assert err == ""
    assert code == 1


def test_36_missing_pattern_is_cli_error(files):
    """SPEC 36: Diagnose the missing required operand, not an empty pattern."""
    out, err, code = run()
    assert out == ""
    diagnostic = assert_cli_error(err)
    # The required argument may use a custom metavar instead of PATTERN.
    assert re.search(r"\b(required|missing)\b|\btoo\s+few\b",
                     diagnostic, re.IGNORECASE)
    assert re.search(r"\b(arguments?|operands?|pattern)\b",
                     diagnostic, re.IGNORECASE)
    assert code == 2


def test_37_count_lines_not_occurrences(files):
    """SPEC 37: Multiple matches within one line contribute only one count."""
    out, err, code = run("-c", "pie", "repeated.txt")
    assert out == "2\n"
    assert err == ""
    assert code == 0


def test_38_count_inverted_selection(files):
    """SPEC 38: Count nonmatching lines when inversion is enabled."""
    out, err, code = run("-v", "-c", "pie", "a.txt")
    assert out == "2\n"
    assert err == ""
    assert code == 0


def test_39_ignore_case_before_inversion(files):
    """SPEC 39: Invert the result of case-insensitive matching."""
    out, err, code = run("-i", "-v", "banana", "a.txt")
    assert out == "apple\ncherry pie\n"
    assert err == ""
    assert code == 0


def test_40_file_list_without_selection_is_empty(files):
    """SPEC 40: No selected files means empty output and status 1."""
    out, err, code = run("-l", "zzz", "a.txt", "b.txt")
    assert out == ""
    assert err == ""
    assert code == 1


def test_41_help_succeeds_without_pattern(files):
    """SPEC 41: Help describes the options and operands without a pattern."""
    out, err, code = run("--help")
    assert out != ""
    assert re.search(r"\busage\s*:", out, re.IGNORECASE)
    for option in ("-i", "-v", "-n", "-c", "-l"):
        assert re.search(rf"(?<![\w-]){re.escape(option)}(?![\w-])",
                         out, re.IGNORECASE), option
    # Check operand meaning, allowing custom metavars and wrapped prose.
    assert re.search(r"\b(patterns?|substrings?|needle|"
                     r"search\s+(?:text|string|term))\b", out, re.IGNORECASE)
    assert re.search(r"\b(files?|filenames?|paths?)\b", out, re.IGNORECASE)
    assert err == ""
    assert code == 0


def test_42_unknown_short_option_is_cli_error(files):
    """SPEC 42: Diagnose the unknown -Z option with usage and status 2."""
    out, err, code = run("-Z", "pie", "a.txt")
    assert out == ""
    diagnostic = assert_cli_error(err)
    assert re.search(r"(?<![\w-])-Z(?![\w-])", diagnostic, re.IGNORECASE)
    assert re.search(r"\b(unrecognized|unrecognised|unknown|unexpected|invalid)\b",
                     diagnostic, re.IGNORECASE)
    assert code == 2


def test_43_default_matching_is_case_sensitive(files):
    """SPEC 43: Without -i, lowercase banana does not select Banana."""
    out, err, code = run("banana", "a.txt")
    assert out == ""
    assert err == ""
    assert code == 1


def test_44_file_list_omits_unselected_file(files):
    """SPEC 44: Omit an unselected file and retain earlier selection status."""
    out, err, code = run("-l", "pie", "a.txt", "literal.txt")
    assert out == "a.txt\n"
    assert err == ""
    assert code == 0


def test_45_count_includes_zero_for_unselected_file(files):
    """SPEC 45: Print a readable file's zero count and retain global success."""
    out, err, code = run("-c", "pie", "b.txt", "literal.txt")
    assert out == "b.txt:2\nliteral.txt:0\n"
    assert err == ""
    assert code == 0


def test_46_inverted_selection_keeps_line_numbers(files):
    """SPEC 46: Number inverted selections by their original line positions."""
    out, err, code = run("-n", "-v", "apple", "a.txt")
    assert out == "2:Banana\n3:cherry pie\n"
    assert err == ""
    assert code == 0


def test_47_preserve_file_operand_order(files):
    """SPEC 47: Process file operands in the supplied, unsorted order."""
    out, err, code = run("pie", "b.txt", "a.txt")
    assert out == "b.txt:pie\nb.txt:apple pie\na.txt:cherry pie\n"
    assert err == ""
    assert code == 0


def test_48_preserve_spaces_and_tabs(files):
    """SPEC 48: Preserve leading spaces, trailing spaces, and a tab."""
    out, err, code = run("pie", "spaces.txt")
    assert out == "  pie \t\n"
    assert err == ""
    assert code == 0


def test_49_ignore_case_normalizes_uppercase_pattern(files):
    """SPEC 49: Normalize an uppercase pattern as well as the input text."""
    (files / "a.txt").write_text("pie\n", encoding="utf-8", newline="\n")
    out, err, code = run("-i", "PIE", "a.txt")
    assert out == "pie\n"
    assert err == ""
    assert code == 0

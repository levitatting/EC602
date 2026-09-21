"""Tests for pygrep (EC602 HW1). Starter file: keep the harness, replace the examples.

How this works: each test runs your program as a separate process, the same
way the shell would, and looks at what came back: standard output, standard
error, and the exit status. That is all a test of a command-line program can
see, and it is all it needs.

Run the tests from the directory that contains pygrep.py:

    uv run pytest

The grader runs this same file against other versions of pygrep.py, so do not
change how PROG is found.
"""

import os
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
    (tmp_path / "a.txt").write_text("apple\nBanana\ncherry pie\n")
    (tmp_path / "b.txt").write_text("pie\napple pie\n")
    old = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old)


# Two examples. Each test is a function whose name starts with `test_`, and a
# test passes if every `assert` in it is true.

def test_match_prints_the_line(files):
    out, err, code = run("pie", "a.txt")
    assert out == "cherry pie\n"
    assert err == ""
    assert code == 0


def test_no_match_exits_with_1(files):
    out, err, code = run("zzz", "a.txt")
    assert out == ""
    assert code == 1


# Your tests go below. One test per numbered case in your SPEC.md, named so
# that the number is easy to find, for example test_07_count_with_two_files.

"""Search UTF-8 files or standard input for a literal substring."""

import argparse
import sys
from typing import TextIO


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the required pattern, optional files, and search flags."""
    parser = argparse.ArgumentParser(
        description="Select lines containing a fixed-string pattern.",
        allow_abbrev=False,
    )
    parser.add_argument("-i", dest="ignore_case", action="store_true",
                        help="ignore case when matching the pattern")
    parser.add_argument("-v", dest="invert", action="store_true",
                        help="select lines that do not match")
    parser.add_argument("-n", dest="line_numbers", action="store_true",
                        help="prefix selected lines with their original line numbers")
    parser.add_argument("-c", dest="count", action="store_true",
                        help="print the number of selected lines per input")
    parser.add_argument("-l", dest="list_files", action="store_true",
                        help="list input names containing selected lines")
    parser.add_argument("pattern", metavar="PATTERN",
                        help="literal substring to search for (may be empty)")
    parser.add_argument("files", metavar="FILE", nargs="*",
                        help="UTF-8 files to search; read standard input if omitted")
    return parser.parse_args(argv)


def search_stream(
    stream: TextIO,
    label: str,
    options: argparse.Namespace,
    multiple_files: bool,
) -> bool:
    """Write one input's selected output and report whether any line was selected."""
    pattern = options.pattern.lower() if options.ignore_case else options.pattern
    prefix = f"{label}:" if multiple_files else ""
    count = 0
    for line_number, raw_line in enumerate(stream, start=1):
        # Remove only one LF; preserve all spaces, tabs, and other content.
        text = raw_line.removesuffix("\n")
        candidate = text.lower() if options.ignore_case else text
        selected = pattern in candidate
        if options.invert:
            selected = not selected
        if not selected:
            continue

        count += 1
        if not options.list_files and not options.count:
            number = f"{line_number}:" if options.line_numbers else ""
            print(f"{prefix}{number}{text}")

    # Output precedence is -l, then -c, then selected lines, regardless of order.
    if options.list_files:
        if count:
            print(label)
    elif options.count:
        print(f"{prefix}{count}")
    return count > 0


def main(argv: list[str] | None = None) -> int:
    """Process inputs in operand order and return the global search status."""
    options = parse_args(argv)
    if not options.files:
        selected = search_stream(sys.stdin, "(standard input)", options, False)
        return 0 if selected else 1

    multiple_files = len(options.files) > 1
    any_selected = False
    had_error = False
    for filename in options.files:
        try:
            with open(filename, encoding="utf-8", newline="\n") as stream:
                selected = search_stream(stream, filename, options, multiple_files)
        except OSError as error:
            reason = error.strerror or str(error)
            print(f"pygrep: {filename}: {reason}", file=sys.stderr)
            had_error = True
        else:
            # Keep earlier selections, but still process every later operand.
            any_selected = any_selected or selected

    if had_error:
        return 2
    return 0 if any_selected else 1


if __name__ == "__main__":
    sys.exit(main())

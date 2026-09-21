# pygrep Specification

## 1. Basic behavior

Usage:

`pygrep [-i] [-v] [-n] [-c] [-l] PATTERN [FILE ...]`

`PATTERN` is a fixed string, not a regular expression. A line matches when
`PATTERN` occurs anywhere in the line.

With one input file and no options, pygrep writes each selected line to
standard output in the same order in which the lines occur in the file.

Example:

Given `sample.txt`:

    apple
    Banana
    cherry pie
    apple pie

Running:

    pygrep pie sample.txt

writes to standard output:

    cherry pie
    apple pie

and writes nothing to standard error. Because at least one line is selected,
the exit status is 0.

If no line is selected, pygrep writes nothing to standard output and the
exit status is 1.

For example:

    pygrep zzz sample.txt

produces no standard output, produces no standard error, and exits with
status 1.

## 2. Options

### `-i`: Ignore case

The `-i` option makes matching case-insensitive. Uppercase and lowercase
letters are treated as equivalent when determining whether a line matches.
The selected line is printed exactly as it appears in the input file.

For example, given `sample.txt` containing:

    apple
    Banana
    cherry pie
    apple pie

Running:

    pygrep -i banana sample.txt

writes:

    Banana

to standard output, writes nothing to standard error, and exits with
status 0.

### `-v`: Invert match

The `-v` option selects lines that do not match the pattern. Lines that
contain the pattern are not selected.

For example, running:

    pygrep -v pie sample.txt

writes:

    apple
    Banana

to standard output, writes nothing to standard error, and exits with
status 0.

### `-n`: Line numbers

The `-n` option prefixes each selected line with its line number. Line
numbers start at 1. The line number and the original line are separated
by a colon (`:`), with no additional space.

For example, running:

    pygrep -n pie sample.txt

writes:

    3:cherry pie
    4:apple pie

to standard output, writes nothing to standard error, and exits with
status 0.

### `-c`: Count selected lines

The `-c` option prints only the number of selected lines instead of the
selected lines themselves.

For example, running:

    pygrep -c pie sample.txt

writes:

    2

to standard output, writes nothing to standard error, and exits with
status 0.

### `-l`: Print file names

The `-l` option prints only the name of each file that has at least one
selected line, instead of printing the selected lines themselves.

For example, running:

    pygrep -l pie sample.txt

writes:

    sample.txt

to standard output, writes nothing to standard error, and exits with
status 0.

## 3. Option combinations

When `-c` and `-n` are used together, `-c` takes precedence for output.
The program prints only the count of selected lines; line numbers are not
printed.

For example, running:

    pygrep -n -c pie sample.txt

writes:

    2

to standard output, writes nothing to standard error, and exits with
status 0.

When `-l` and `-c` are used together, `-l` takes precedence for output.
If a file has at least one selected line, the program prints the file name
instead of the count.

For example, running:

    pygrep -l -c pie sample.txt

writes:

    sample.txt

to standard output, writes nothing to standard error, and exits with
status 0.

When `-l` and `-n` are used together, `-l` takes precedence for output.
If a file has at least one selected line, the program prints only the file
name; line numbers and selected lines are not printed.

For example, running:

    pygrep -l -n pie sample.txt

writes:

    sample.txt

to standard output, writes nothing to standard error, and exits with
status 0.

When `-i` and `-v` are used together, matching is first performed
case-insensitively, and then the result is inverted. Therefore, lines that
do not contain the pattern, ignoring case, are selected.

For example, running:

    pygrep -i -v banana sample.txt

writes:

    apple
    cherry pie
    apple pie

to standard output, writes nothing to standard error, and exits with
status 0.

## 4. Multiple files

When more than one input file is specified, each selected line is prefixed
with the name of the file from which it came. The file name and the line
contents are separated by a colon (`:`), with no additional space.

For example, running:

    pygrep pie sample.txt second.txt

writes:

    sample.txt:cherry pie
    sample.txt:apple pie
    second.txt:pie
    second.txt:banana pie

to standard output, writes nothing to standard error, and exits with
status 0.

When `-n` is used with multiple files, each selected line is printed in
the format:

    FILE:LINE_NUMBER:LINE

The file name, line number, and line contents are separated by colons (`:`)
with no additional spaces. Line numbers start at 1 separately for each file.

For example, running:

    pygrep -n pie sample.txt second.txt

writes:

    sample.txt:3:cherry pie
    sample.txt:4:apple pie
    second.txt:1:pie
    second.txt:3:banana pie

to standard output, writes nothing to standard error, and exits with
status 0.

When `-c` is used with multiple files, pygrep prints one count for each
file in the format:

    FILE:COUNT

The file name and count are separated by a colon (`:`), with no additional
space.

For example, running:

    pygrep -c pie sample.txt second.txt

writes:

    sample.txt:2
    second.txt:2

to standard output, writes nothing to standard error, and exits with
status 0.

When `-c` is used with multiple files, a count is printed for every
successfully read file, including files with zero selected lines.

The exit status is based on the overall result across all input files.
If at least one line is selected in any file and no error occurs, the
exit status is 0.

For example, running:

    pygrep -c pie empty.txt sample.txt

writes:

    empty.txt:0
    sample.txt:2

to standard output, writes nothing to standard error, and exits with
status 0.

## 5. Edge cases

### Empty pattern

An empty pattern matches every line in the input file. Therefore, when no
other option changes the selection, every line is selected and printed.

For example, running:

    pygrep '' sample.txt

writes:

    apple
    Banana
    cherry pie
    apple pie

to standard output, writes nothing to standard error, and exits with
status 0.

### Empty file

An empty file contains no lines, so no line can be selected.

For example, running:

    pygrep pie empty.txt

writes nothing to standard output, writes nothing to standard error, and
exits with status 1.

### File whose last line has no newline

If the last line of a file does not end with a newline, pygrep still treats
it as a complete line. If that line is selected, pygrep prints the line
followed by a newline.

For example, if `nonewline.txt` contains:

    apple
    cherry pie

where the final line has no terminating newline, running:

    pygrep pie nonewline.txt

writes:

    cherry pie

followed by a newline to standard output, writes nothing to standard error,
and exits with status 0.

### File that does not exist

If a file cannot be opened because it does not exist, pygrep writes an
error message to standard error in the form:

    pygrep: FILE: reason

For example, running:

    pygrep pie does_not_exist.txt

writes nothing to standard output and writes:

    pygrep: does_not_exist.txt: No such file or directory

to standard error. The exit status is 2.

### Directory given as a file

If a directory is given where a file is expected, pygrep cannot read it as
an input file and reports an error.

For example, running:

    pygrep pie tests

writes nothing to standard output and writes:

    pygrep: tests: Is a directory

to standard error. The exit status is 2.

### No input files

If no input files are given, pygrep reads lines from standard input.

For example, if the standard input is:

    apple
    cherry pie
    banana
    apple pie

running:

    pygrep pie

writes:

    cherry pie
    apple pie

to standard output. No file name is prefixed to the output lines. Nothing
is written to standard error, and the exit status is 0 because at least
one line is selected.

## 6. Test cases

### 1. Basic matching

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep pie sample.txt

**expect**

Standard output:

    cherry pie
    apple pie

Standard error is empty.

Exit status: `0`.

### 2. No matching lines

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep zzz sample.txt

**expect**

Standard output is empty.

Standard error is empty.

Exit status: `1`.

### 3. Case-insensitive matching with `-i`

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep -i banana sample.txt

**expect**

Standard output:

    Banana

Standard error is empty.

Exit status: `0`.

### 4. Inverted matching with `-v`

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep -v pie sample.txt

**expect**

Standard output:

    apple
    Banana

Standard error is empty.

Exit status: `0`.

### 5. Line numbers with `-n`

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep -n pie sample.txt

**expect**

Standard output:

    3:cherry pie
    4:apple pie

Standard error is empty.

Exit status: `0`.

### 6. Counting selected lines with `-c`

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep -c pie sample.txt

**expect**

Standard output:

    2

Standard error is empty.

Exit status: `0`.

### 7. Line numbers with multiple files

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

`second.txt` contains:

    pie
    orange
    banana pie

**run**

    pygrep -n pie sample.txt second.txt

**expect**

Standard output:

    sample.txt:3:cherry pie
    sample.txt:4:apple pie
    second.txt:1:pie
    second.txt:3:banana pie

Standard error is empty.

Exit status: `0`.

### 8. Combining `-l` and `-c`

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep -l -c pie sample.txt

**expect**

Standard output:

    sample.txt

Standard error is empty.

Exit status: `0`.

### 9. Empty pattern

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep '' sample.txt

**expect**

Standard output:

    apple
    Banana
    cherry pie
    apple pie

Standard error is empty.

Exit status: `0`.

### 10. Empty file

**given**

`empty.txt` is an empty file.

**run**

    pygrep pie empty.txt

**expect**

Standard output is empty.

Standard error is empty.

Exit status: `1`.

### 11. Last line without a newline

**given**

`nonewline.txt` contains:

    apple
    cherry pie

The final line `cherry pie` does not end with a newline character.

**run**

    pygrep pie nonewline.txt

**expect**

Standard output:

    cherry pie

The output ends with a newline character.

Standard error is empty.

Exit status: `0`.

### 12. Nonexistent file

**given**

`does_not_exist.txt` does not exist.

**run**

    pygrep pie does_not_exist.txt

**expect**

Standard output is empty.

Standard error:

    pygrep: does_not_exist.txt: No such file or directory

Exit status: `2`.

### 13. Directory used as an input file

**given**

`tests` is a directory.

**run**

    pygrep pie tests

**expect**

Standard output is empty.

Standard error:

    pygrep: tests: Is a directory

Exit status: `2`.

### 14. Reading from standard input when no file is given

**given**

Standard input contains:

    apple
    cherry pie
    banana
    apple pie

**run**

    pygrep pie

**expect**

Standard output:

    cherry pie
    apple pie

Standard error is empty.

Exit status: `0`.

### 15. File error with a successful match in another file

**given**

`does_not_exist.txt` does not exist.

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep pie does_not_exist.txt sample.txt

**expect**

Standard output:

    sample.txt:cherry pie
    sample.txt:apple pie

Standard error:

    pygrep: does_not_exist.txt: No such file or directory

Exit status: `2`.

### 16. Count with no matching lines

**given**

`sample.txt` contains:

    apple
    Banana
    cherry pie
    apple pie

**run**

    pygrep -c zzz sample.txt

**expect**

Standard output:

    0

Standard error is empty.

Exit status: `1`.
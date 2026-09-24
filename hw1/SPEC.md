# pygrep — Behavioral Specification

EC602 Design by Software · Homework 1

This document defines the required behavior of `pygrep.py`. The GNU grep
experiments provide observations; they do not by themselves establish
conformance to this specification.

## 1. Basis, precedence, and scope

This specification uses the supplied Homework 1 assignment sheet, the original
`hw1_test_pygrep.py` harness, and the two supplied experiment records.
References `O01`–`O16` mean cases in `grep_options.txt`; references
`E01`–`E24` mean cases in `grep_edges.txt`. The records identify GNU grep 3.11;
the boundary record specifies `LC_ALL=C`.

The assignment takes precedence over a GNU grep observation. In particular,
`pygrep` always performs fixed-string matching; the oracle experiments used
`grep -F`, but `-F` is not a required pygrep option. File errors must use the
assignment's `pygrep: FILE: reason` format, and command-line diagnostics must
come from the required `argparse` interface rather than being copied from grep.

The required search options are `-i`, `-v`, `-n`, `-c`, and lowercase letter
`-l` (not digit `-1`). The assignment also requires `--help`.
Regular expressions, additional long search options such as `--count`,
`-r`, `-w`, `-o`, binary files, and `-` as an input-file name are outside the
assignment's tested scope. The `--help` requirement is an explicit exception
to the exclusion of long search options.

This specification separates observed results from explicit contract choices:
section 7 identifies text/argument conventions not established by the logs.
Cases 01–40 trace to the experiments, with the required diagnostic adaptations.
Cases 41–49 are additional assignment- or specification-derived cases;
they are not additional GNU grep observations.

## 2. Command line, inputs, and line selection

Canonical invocation from the homework directory:

```text
python pygrep.py [-i] [-v] [-n] [-c] [-l] PATTERN [FILE ...]
python pygrep.py --help
```

`PATTERN` is one required argument. It is a literal substring, not a regular
expression. Quoting, when needed, is performed by the caller's shell and is
not part of the pattern. An explicitly supplied empty string is a valid
pattern; omitting the argument is an error. (`O03`, `E01`, `E02`, `E20`.)

`FILE ...` is zero or more named inputs. With no file operands, read standard
input until end of input. With one or more file operands, process those inputs
in the order supplied, without also reading standard input. Do not recursively
search a directory given as a file. (`E09`, `E15`–`E19`; operand order is an
explicit contract choice consistent with the observations.)

For the LF-delimited text covered by the cases, an input line is its content
followed by an LF, or a nonempty final content segment without LF. An empty
file has zero lines; an LF by itself is one empty-content line. A final LF does
not create an extra line after it. Matching is against the line content,
without its terminating LF. Printing preserves that content exactly, including
spaces, tabs, and original letter case. Every printed selected line ends with
one LF, adding it when the input's final line had none. (`E01`, `E03`, `E05`,
`E06`, `E07`; whitespace preservation is an explicit choice.)

Selection is defined in this order:

1. Without `-i`, a line matches when `PATTERN` is a case-sensitive substring
   of its content. With `-i`, ignore letter case for the comparison; do not
   change the printed content. See section 7 for the unmeasured Unicode choice.
2. Without `-v`, select matching lines. With `-v`, select nonmatching lines.
3. Apply the chosen output mode to the selected lines. Counts and exit status
   depend on **selected lines**, not raw matches and not printed characters.

Thus `-i -v` inverts the case-insensitive match, and `-v -c` counts the
nonmatching lines. (`O04`, `O05`, `E21`–`E23`.)

## 3. Output modes and exact formats

Output-mode precedence is independent of the order of the supported flags:

```text
if -l is present: file-list mode
else if -c is present: count mode
else: selected-line mode, optionally with -n
```

This adopts the observed `-l` over `-c` and `-n`, and `-c` over `-n` behavior
as a general specification rule. `-i` and `-v` still affect selection in every
mode. (`O09`–`O15`.)

For prefix decisions, `N` is the number of supplied file operands, including
operands that cannot be opened. It is not the number of readable or matching
files. With no file operands, standard input is one unprefixed input source.
Preserve the supplied spelling of a filename when it appears in output.
(`E10`; filename spelling is an explicit contract choice.)

### 3.1 Selected-line mode

`TEXT` is the selected line's unchanged content, `LINE` is its one-based
position in the original input, and `FILE` is the corresponding operand.
Line numbers restart at 1 for each input. They are not indexes into the
selected output. Colons have no extra spaces around them. (`O06`–`O08`.)

| Inputs | `-n` | Exact output for each selected line |
|---|---|---|
| One file, or standard input | absent | `TEXT\n` |
| One file, or standard input | present | `LINE:TEXT\n` |
| Two or more file operands | absent | `FILE:TEXT\n` |
| Two or more file operands | present | `FILE:LINE:TEXT\n` |

Examples for `PATTERN = 'pie'` and the case inputs in section 8:

- `python pygrep.py pie a.txt` prints `'cherry pie\n'`.
- `python pygrep.py -n pie a.txt` prints `'3:cherry pie\n'`.
- `python pygrep.py pie a.txt b.txt` starts with `'a.txt:cherry pie\n'`.
- `python pygrep.py -n pie a.txt b.txt` prints
  `'a.txt:3:cherry pie\nb.txt:1:pie\nb.txt:2:apple pie\n'`.

Preserve input order within each file and operand order across files.
An input with no selected lines contributes no output in this mode.

### 3.2 Count mode (`-c` without `-l`)

Print one decimal count of **selected lines** for each successfully read input,
even when that count is zero. Count each selected line once, regardless of how
many times the substring occurs in it. Do not print selected text or line
numbers. (`O09`–`O11`, `O16`, `E04`, `E21`, `E22`.)

| Inputs | Exact output for each readable input | Example |
|---|---|---|
| One named file | `COUNT\n` | `'1\n'` |
| Standard input | `COUNT\n` | `'1\n'` |
| Two or more file operands | `FILE:COUNT\n` | `'a.txt:1\nb.txt:2\n'` |

A file that cannot be opened contributes an error diagnostic, not a made-up
zero count. Continue counting later inputs. (`E13`.) Printing a count, including
`'0\n'`, does not by itself imply exit status 0. (`O16`, `E04`.)

### 3.3 File-list mode (`-l`)

For each named input containing at least one selected line, print exactly
`FILE\n` once for that operand. Otherwise print nothing for it. Do not print
counts, line numbers, selected text, or a duplicate filename prefix.
Continue processing later file operands, including checking them for errors.
(`O12`–`O15`, `E14`, `E24`.)

With no file operands, if standard input has a selected line, print exactly
`'(standard input)\n'`. With none selected, print nothing. (`E18`, with the
no-selection rule adopted consistently across inputs.)

## 4. Required boundary cases

| Situation | Required behavior | Basis |
|---|---|---|
| Empty pattern with existing lines | Every line matches, including blank lines; `-v` therefore selects none. | `E01`, `E02` |
| Empty input file | Zero input lines; normally no output and exit 1. `-c` prints `'0\n'`, still with exit 1. | `E03`, `E04` |
| Empty pattern and empty file | No line exists to be selected; no normal line output, exit 1. | `E05` |
| Final line lacks LF | Include it in matching and numbering; add LF when printing it. | `E06`, `E07` |
| Missing file | File diagnostic on stderr, no output for that file, continue later operands, final exit 2. | `E08`, `E10`–`E14` |
| Directory used as a file | Treat it as a file-input error, not as empty input or a recursive request. | `E09` |
| No file operands | Read standard input, with the output rules in section 3. | `E15`–`E18` |
| Empty standard input | No selected line, normal output empty, exit 1. | `E19` |
| No pattern argument | Command-line error, not an empty-pattern search; diagnostic on stderr, exit 2. | `E20` plus Assignment Part 2 |

## 5. Standard error and help

### 5.1 Named-file errors

For each named input that cannot be opened, write one diagnostic line to stderr:

```text
pygrep: FILE: reason\n
```

`FILE` is the supplied operand. `reason` must be a nonempty description of
that failure, without a traceback. Continue with later file operands. Print
no selected line, count, or listed filename on behalf of the failed input.
On success, ordinary search operations leave stderr empty.

The assignment fixes the prefix and destination. The supplied Linux experiments
show reasons such as `No such file or directory` and `Is a directory`, but
this specification deliberately does **not** require one operating system's
complete exception wording. English examples are:

```text
'pygrep: missing.txt: No such file or directory\n'
'pygrep: directory: Is a directory\n'
```

A conforming test must check the exact `pygrep: FILE: ` prefix, a nonempty reason,
a terminating LF, and the number of diagnostic lines. It must not compare
against the oracle's `/bin/grep:` prefix or require an absolute temporary path.
For multiple file errors, diagnostics follow operand order. stdout and stderr
are separate streams; no cross-stream display ordering is promised.

### 5.2 Command-line errors and `--help`

Use `argparse`, as required by the assignment. A missing required pattern or
an unknown option is a command-line error: no search output, an argparse
usage/error diagnostic on stderr identifying the problem, and exit status 2.
Do not copy GNU grep's `Usage: grep ...` diagnostic from `E20`.

`--help` works without a pattern, prints nonempty usage/help text on stdout,
describes the five supported search flags and the pattern/file operands,
leaves stderr empty, and exits with status 0. Exact wrapping, capitalization,
program-name spelling in usage, and full help wording are not fixed. Tests
check the documented stream/content contract rather than a snapshot of
argparse's formatting. (Assignment Part 2; these help/error output choices
are not GNU grep measurements.)

## 6. Exit status

| Situation | Exit status |
|---|---:|
| Valid `--help` request | 0 |
| Invalid command line | 2 |
| Search encountered a file error, even if other inputs selected lines | 2 |
| No error, and at least one selected line across all searched inputs | 0 |
| No error, and no selected line across all searched inputs | 1 |

For a search, the effective precedence is **error first, then any selection,
then no selection**. Evaluate this across inputs, not using only the last
file's result. `-v` changes which lines count as selected. `-c` and `-l`
change output format, not this exit-status contract. (`E10`–`E14`, `O16`,
`E02`, `E22`, `E24`; Assignment's exit-status rule.)

## 7. Explicit decisions beyond the measured ASCII examples

The following conventions define behavior beyond the measured ASCII examples.
They are specification decisions, not additional findings from the logs or
claims about every GNU/BSD grep behavior.

- **Text convention:** use UTF-8 text for named files and the supplied text
  stream for stdin. The numbered cases use ASCII characters and LF endings.
  For `-i`, the chosen comparison is substring search after applying Python
  `str.lower()` to the pattern and line content. The original content is
  printed unchanged. The supplied records do not verify non-ASCII case
  mappings, locale behavior, CRLF input, or malformed UTF-8; those are not
  grounds for claiming full GNU grep equivalence.
- **Canonical argument convention:** use separate supported flag tokens before
  `PATTERN`, followed by file operands. Flags may be ordered arbitrarily;
  repeating a supported boolean flag leaves it enabled rather than toggling
  it. Accept `--` as an option terminator, so a pattern starting with a hyphen
  can be passed as an operand. Flag repetition and `--` are grammar
  choices, not measurements in the supplied records. The cases do not demand
  arbitrary interleaving of options among file operands.
- **Content/order convention:** preserve line content and supplied filename
  spellings; do not trim whitespace or sort inputs. These conventions make
  the printed-line/file-order contract explicit. Cases 47 and 48 exercise
  order and whitespace, rather than pretending that the original logs
  already measured those particular inputs.

The assignment exclusions in section 1 are separate from these evidence
limitations; an unmeasured behavior is not automatically excluded by the
teacher. No additional search feature, third-party runtime library, or claim
of full grep compatibility is introduced here.

## 8. Numbered test cases (01–49): given / run / expect

Run each case independently in a fresh temporary working directory, using
the supplied harness. `PROG` must retain the instructor's lookup:

```python
PROG = os.path.abspath(os.environ.get("PYGREP", "pygrep.py"))
```

The commands below use `python pygrep.py` as readable notation. In the test
suite, call the existing `run(*args, stdin=...)`, which uses `sys.executable`
and the resolved `PROG`. Do not replace the harness with a hard-coded path
or have the final tests depend on system grep being installed. (Starter file.)

Each **Given** below specifies exact text with Python-style string literals:
`\n` is LF, `\t` is a tab, and `''` is empty. stdin is empty unless an explicit
nonempty value is shown. Other unrelated fixture files may exist; only files
passed to the command participate in its search. Each test must assert
stdout, stderr, and exit status, even when one stream is empty.

For file-error cases, `FILE_ERROR(name)` is a precise test predicate for stderr:
exactly one LF-terminated diagnostic with prefix `'pygrep: ' + name + ': '`,
a nonempty one-line reason, and no additional diagnostic or traceback.
This intentionally does not require an OS-specific reason string.
`CLI_ERROR` means nonempty stderr containing usage and an error explanation
for the stated invalid command line; exact argparse layout is not fixed.
These predicates are specified output contracts, not unfilled placeholders.

### 8.1 Cases mapped to the supplied experiments (01–40)

#### 01. Match prints the selected line

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py pie a.txt`

**Expect:** stdout = `'cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** O01.

#### 02. No match exits with 1

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py zzz a.txt`

**Expect:** stdout = `''`; stderr = `''`; exit status = **1**.

**Basis:** O02.

#### 03. Pattern is literal, not a regular expression

**Given:** `literal.txt` = `'a.b\naXb\nabc\n'`; stdin = `''`.

**Run:** `python pygrep.py . literal.txt`

**Expect:** stdout = `'a.b\n'`; stderr = `''`; exit status = **0**.

**Basis:** O03.

#### 04. Ignore case while preserving the original output

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -i banana a.txt`

**Expect:** stdout = `'Banana\n'`; stderr = `''`; exit status = **0**.

**Basis:** O04.

#### 05. Invert the line selection

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -v pie a.txt`

**Expect:** stdout = `'apple\nBanana\n'`; stderr = `''`; exit status = **0**.

**Basis:** O05.

#### 06. Use the original one-based line number

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -n pie a.txt`

**Expect:** stdout = `'3:cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** O06.

#### 07. Prefix lines when multiple files are supplied

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py pie a.txt b.txt`

**Expect:** stdout = `'a.txt:cherry pie\nb.txt:pie\nb.txt:apple pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** O07.

#### 08. Prefix file name and line number; restart numbering per file

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -n pie a.txt b.txt`

**Expect:** stdout = `'a.txt:3:cherry pie\nb.txt:1:pie\nb.txt:2:apple pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** O08.

#### 09. Count selected lines separately for each file

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -c pie a.txt b.txt`

**Expect:** stdout = `'a.txt:1\nb.txt:2\n'`; stderr = `''`; exit status = **0**.

**Basis:** O09.

#### 10. Count suppresses line-number output

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -c -n pie a.txt b.txt`

**Expect:** stdout = `'a.txt:1\nb.txt:2\n'`; stderr = `''`; exit status = **0**.

**Basis:** O10.

#### 11. Reversing -n and -c does not change count output

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -n -c pie a.txt b.txt`

**Expect:** stdout = `'a.txt:1\nb.txt:2\n'`; stderr = `''`; exit status = **0**.

**Basis:** O11.

#### 12. List each selected file once

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -l pie a.txt b.txt`

**Expect:** stdout = `'a.txt\nb.txt\n'`; stderr = `''`; exit status = **0**.

**Basis:** O12.

#### 13. File-list output takes precedence over count output

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -l -c pie a.txt b.txt`

**Expect:** stdout = `'a.txt\nb.txt\n'`; stderr = `''`; exit status = **0**.

**Basis:** O13.

#### 14. Reversing -c and -l does not change file-list output

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -c -l pie a.txt b.txt`

**Expect:** stdout = `'a.txt\nb.txt\n'`; stderr = `''`; exit status = **0**.

**Basis:** O14.

#### 15. File-list output suppresses line numbers

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -l -n pie a.txt b.txt`

**Expect:** stdout = `'a.txt\nb.txt\n'`; stderr = `''`; exit status = **0**.

**Basis:** O15.

#### 16. A printed zero count still means no selected line

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -c zzz a.txt`

**Expect:** stdout = `'0\n'`; stderr = `''`; exit status = **1**.

**Basis:** O16.

#### 17. An empty pattern selects existing blank lines too

**Given:** `blank_lines.txt` = `'pie\n\nAPPLE\n'`; stdin = `''`.

**Run:** `python pygrep.py '' blank_lines.txt`

**Expect:** stdout = `'pie\n\nAPPLE\n'`; stderr = `''`; exit status = **0**.

**Basis:** E01.

#### 18. Invert an empty pattern: select no lines

**Given:** `blank_lines.txt` = `'pie\n\nAPPLE\n'`; stdin = `''`.

**Run:** `python pygrep.py -v '' blank_lines.txt`

**Expect:** stdout = `''`; stderr = `''`; exit status = **1**.

**Basis:** E02.

#### 19. An empty file has no matching line

**Given:** `empty.txt` = `''`; stdin = `''`.

**Run:** `python pygrep.py pie empty.txt`

**Expect:** stdout = `''`; stderr = `''`; exit status = **1**.

**Basis:** E03.

#### 20. Count an empty file as zero

**Given:** `empty.txt` = `''`; stdin = `''`.

**Run:** `python pygrep.py -c pie empty.txt`

**Expect:** stdout = `'0\n'`; stderr = `''`; exit status = **1**.

**Basis:** E04.

#### 21. An empty pattern does not invent a line in an empty file

**Given:** `empty.txt` = `''`; stdin = `''`.

**Run:** `python pygrep.py '' empty.txt`

**Expect:** stdout = `''`; stderr = `''`; exit status = **1**.

**Basis:** E05.

#### 22. Add a newline when printing an unterminated final line

**Given:** `no_newline.txt` = `'apple\ncherry pie'`; stdin = `''`.

**Run:** `python pygrep.py pie no_newline.txt`

**Expect:** stdout = `'cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** E06.

#### 23. Number an unterminated final line correctly

**Given:** `no_newline.txt` = `'apple\ncherry pie'`; stdin = `''`.

**Run:** `python pygrep.py -n pie no_newline.txt`

**Expect:** stdout = `'2:cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** E07.

#### 24. Report a missing file on standard error

**Given:** `missing.txt` does not exist; stdin = `''`.

**Run:** `python pygrep.py pie missing.txt`

**Expect:** stdout = `''`; stderr = `FILE_ERROR('missing.txt')`; exit status = **2**.

**Basis:** E08; file-error destination, prefix, and reason contract adapted to section 5.1.

#### 25. Report a directory used as an input file

**Given:** `directory` is an existing empty directory; stdin = `''`.

**Run:** `python pygrep.py pie directory`

**Expect:** stdout = `''`; stderr = `FILE_ERROR('directory')`; exit status = **2**.

**Basis:** E09; file-error destination, prefix, and reason contract adapted to section 5.1.

#### 26. Continue after an initial missing file; retain filename prefixes

**Given:** `missing.txt` does not exist; `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py pie missing.txt a.txt`

**Expect:** stdout = `'a.txt:cherry pie\n'`; stderr = `FILE_ERROR('missing.txt')`; exit status = **2**.

**Basis:** E10; file-error destination, prefix, and reason contract adapted to section 5.1.

#### 27. Continue through a middle error and retain status 2

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `missing.txt` does not exist; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py pie a.txt missing.txt b.txt`

**Expect:** stdout = `'a.txt:cherry pie\nb.txt:pie\nb.txt:apple pie\n'`; stderr = `FILE_ERROR('missing.txt')`; exit status = **2**.

**Basis:** E11; file-error destination, prefix, and reason contract adapted to section 5.1.

#### 28. An error takes precedence over the no-selection status

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `missing.txt` does not exist; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py zzz a.txt missing.txt b.txt`

**Expect:** stdout = `''`; stderr = `FILE_ERROR('missing.txt')`; exit status = **2**.

**Basis:** E12; file-error destination, prefix, and reason contract adapted to section 5.1.

#### 29. In count mode, omit a failed file but count later files

**Given:** `missing.txt` does not exist; `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -c pie missing.txt a.txt b.txt`

**Expect:** stdout = `'a.txt:1\nb.txt:2\n'`; stderr = `FILE_ERROR('missing.txt')`; exit status = **2**.

**Basis:** E13; file-error destination, prefix, and reason contract adapted to section 5.1.

#### 30. In file-list mode, continue to later files after an error

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `missing.txt` does not exist; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -l pie a.txt missing.txt b.txt`

**Expect:** stdout = `'a.txt\nb.txt\n'`; stderr = `FILE_ERROR('missing.txt')`; exit status = **2**.

**Basis:** E14; file-error destination, prefix, and reason contract adapted to section 5.1.

#### 31. Read standard input when no file operand is present

**Given:** no file operands; stdin = `'apple\nBanana\ncherry pie\n'`.

**Run:** `python pygrep.py pie`

**Expect:** stdout = `'cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** E15.

#### 32. Number standard-input lines without a filename prefix

**Given:** no file operands; stdin = `'apple\nBanana\ncherry pie\n'`.

**Run:** `python pygrep.py -n pie`

**Expect:** stdout = `'3:cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** E16.

#### 33. Count standard-input lines without a filename prefix

**Given:** no file operands; stdin = `'apple\nBanana\ncherry pie\n'`.

**Run:** `python pygrep.py -c pie`

**Expect:** stdout = `'1\n'`; stderr = `''`; exit status = **0**.

**Basis:** E17.

#### 34. Use the standard-input label in file-list mode

**Given:** no file operands; stdin = `'apple\nBanana\ncherry pie\n'`.

**Run:** `python pygrep.py -l pie`

**Expect:** stdout = `'(standard input)\n'`; stderr = `''`; exit status = **0**.

**Basis:** E18.

#### 35. Empty standard input selects no lines

**Given:** no file operands; stdin = `''`.

**Run:** `python pygrep.py pie`

**Expect:** stdout = `''`; stderr = `''`; exit status = **1**.

**Basis:** E19.

#### 36. Missing PATTERN is a command-line error, not an empty pattern

**Given:** no file operands; stdin = `''`.

**Run:** `python pygrep.py`

**Expect:** stdout = `''`; stderr = `CLI_ERROR` (Identify the missing required pattern argument); exit status = **2**.

**Basis:** E20 for the error status; Assignment Part 2 for the argparse diagnostic.

#### 37. Count selected lines rather than substring occurrences

**Given:** `repeated.txt` = `'pie pie\npie\nno\n'`; stdin = `''`.

**Run:** `python pygrep.py -c pie repeated.txt`

**Expect:** stdout = `'2\n'`; stderr = `''`; exit status = **0**.

**Basis:** E21.

#### 38. Count the inverted selection

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -v -c pie a.txt`

**Expect:** stdout = `'2\n'`; stderr = `''`; exit status = **0**.

**Basis:** E22.

#### 39. Apply case-insensitive matching before inversion

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -i -v banana a.txt`

**Expect:** stdout = `'apple\ncherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** E23.

#### 40. File-list mode prints nothing if every file has no selected line

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `b.txt` = `'pie\napple pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -l zzz a.txt b.txt`

**Expect:** stdout = `''`; stderr = `''`; exit status = **1**.

**Basis:** E24.

### 8.2 Additional required or derived cases (41–48)

These cases are specified from the assignment and the contracts above.
They are not additional experiments in the supplied observation files.

#### 41. Help succeeds without PATTERN

**Given:** no file operands; stdin = `''`.

**Run:** `python pygrep.py --help`

**Expect:** stdout = nonempty help text describing the pattern/file operands and the supported options (section 5.2); stderr = `''`; exit status = **0**.

**Basis:** Assignment Part 2; not a grep measurement.

#### 42. Reject an unknown short option

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -Z pie a.txt`

**Expect:** stdout = `''`; stderr = `CLI_ERROR` (Identify the unrecognized -Z option); exit status = **2**.

**Basis:** Assignment Part 2; derived test, not a grep measurement.

#### 43. Default matching remains case-sensitive

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py banana a.txt`

**Expect:** stdout = `''`; stderr = `''`; exit status = **1**.

**Basis:** Matching contract in section 2; derived test.

#### 44. File-list mode omits a file with no selected lines

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; `literal.txt` = `'a.b\naXb\nabc\n'`; stdin = `''`.

**Run:** `python pygrep.py -l pie a.txt literal.txt`

**Expect:** stdout = `'a.txt\n'`; stderr = `''`; exit status = **0**.

**Basis:** File-list contract in section 3.3; derived test.

#### 45. Count mode prints zero for a readable unselected file

**Given:** `b.txt` = `'pie\napple pie\n'`; `literal.txt` = `'a.b\naXb\nabc\n'`; stdin = `''`.

**Run:** `python pygrep.py -c pie b.txt literal.txt`

**Expect:** stdout = `'b.txt:2\nliteral.txt:0\n'`; stderr = `''`; exit status = **0**.

**Basis:** Per-file count and final-status contracts; derived test.

#### 46. Inverted selection keeps original line numbers

**Given:** `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -n -v apple a.txt`

**Expect:** stdout = `'2:Banana\n3:cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** Line-number and inverted-selection contracts; derived test.

#### 47. Process files in operand order, not sorted order

**Given:** `b.txt` = `'pie\napple pie\n'`; `a.txt` = `'apple\nBanana\ncherry pie\n'`; stdin = `''`.

**Run:** `python pygrep.py pie b.txt a.txt`

**Expect:** stdout = `'b.txt:pie\nb.txt:apple pie\na.txt:cherry pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** File-order choice in section 2; derived test.

#### 48. Preserve spaces and tabs in selected line content

**Given:** `spaces.txt` = `'  pie \t\nx\n'`; stdin = `''`.

**Run:** `python pygrep.py pie spaces.txt`

**Expect:** stdout = `'  pie \t\n'`; stderr = `''`; exit status = **0**.

**Basis:** Line-preservation choice in section 2; derived test.

### 8.3 Additional case from development validation (49)

#### 49. Ignore case for an uppercase pattern as well as the input text

**Given:** `a.txt` = `'pie\n'`; stdin = `''`.

**Run:** `python pygrep.py -i PIE a.txt`

**Expect:** stdout = `'pie\n'`; stderr = `''`; exit status = **0**.

**Basis:** The existing case-insensitive matching contract (sections 2 and 7),
also exercised by development check D7. This is not an additional GNU grep
observation.

## 9. Implementation and test-suite constraints

The `pygrep.py` implementation must use only the Python standard
library, use `argparse`, place its work in functions, and guard execution
with `if __name__ == "__main__":`. Importing it must not start a search,
parse the importing process's command line, print output, or exit the
importing process. These are assignment requirements, not consequences of
the GNU grep experiments. NumPy and pandas are not runtime dependencies.

Name the corresponding pytest functions `test_01_...` through
`test_49_...`, retaining one numbered behavior per test. Preserve the
starter harness and create the additional inputs in the supplied temporary
fixture or inside individual tests. The two starter examples are replaced
by numbered cases 01 and 02, both checking all three returned values.

Tests must satisfy this specification on a correct program and expose
observable violations in incorrect programs. A local pass on the
implementation is not a guarantee about the instructor's reference or
planted-bug programs. Do not change expected results merely to make an
incorrect implementation pass.

The experiment logs and helper scripts are development evidence stored
outside the submission directory. The final submission contains the
assignment's four requested files: `GROUP.md`, `SPEC.md`, `pygrep.py`,
and `tests/test_pygrep.py`.

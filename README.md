# C++ -> Python genealogy conversion

This directory is a Python translation of the supplied C++ genealogy program.

## Files

- `genealogy.py` — main implementation, replacing `myString`/`field` with Python `str`.
- `htmlbldr.py` — command-line wrapper corresponding to `htmlbldr.cpp`.
- `htmlturbo.py` — command-line wrapper corresponding to `htmlturbo.cpp`.

## Input format

The input is pipe-separated (`|`) even though its filename may end in `.txt`.

Each record has 14 fields:

1. number
2. hierarchy number (`hnum`)
3. first name
4. last name
5. place born
6. birth date
7. death date
8. spouse term
9. marriage date
10. spouse
11. spouse place born
12. spouse birth date
13. spouse death date
14. spouse link

Empty fields are preserved.

## Examples

Run the HTML builder:

    python htmlbldr.py bishops.txt X

Generate the DOB index:

    python htmlbldr.py bishops.txt X -d

Generate the generation index:

    python htmlbldr.py bishops.txt X -g

Choose an output directory:

    python htmlbldr.py bishops.txt X -o output

The `htmlturbo.py` wrapper uses the same positional arguments.

## Notes about compatibility

- The C++ `myString` and `field` classes are not reproduced. Python's built-in `str` is used throughout.
- The C++ input extractor reads fields delimited by `|`; Python uses `line.split("|")` while preserving empty fields.
- The original C++ writer emits tab-separated `newdata.txt`; this translation preserves that behavior.
- HTML generation uses ordinary Python file objects and `pathlib`.
- Output subdirectories are created automatically for page names such as `BBisho/1.htm`.
- `_html_info1()` receives the output directory explicitly, fixing the `NameError: output_dir is not defined` bug.
- `htmlbldr.py` now includes the family-tree generation pass from the C++ `htmlbldr.cpp`, before the final HTML closing tags are written.
- The old C++ code has some platform-specific DOS/Windows calls (`access`, `unlink`, `dir.h`, `io.h`). Those are replaced with Python's cross-platform `pathlib`/file operations.
- The original `htmlturbo.cpp` does not call `generateTree`; `htmlbldr.cpp` does. The Python wrappers preserve that distinction.

## Validation

The corrected conversion was run successfully with the requested command:

    python3 htmlbldr.py bishops.txt B

using the supplied 374-record `bishops.txt` file. The run completed with exit status 0 and generated the HTML output, including family-tree sections, plus `newdata.txt` and the name index.

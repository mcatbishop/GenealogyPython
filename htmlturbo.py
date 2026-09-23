#!/usr/bin/env python3
import argparse
from genealogy import run_htmlturbo

def main():
    parser = argparse.ArgumentParser(
        description="Python translation of the C++ htmlturbo program."
    )
    parser.add_argument("datafile", nargs="?", default="sorted.txt")
    parser.add_argument("unique", nargs="?", default="X")
    parser.add_argument("option", nargs="?", choices=["-d", "-g"], default=None)
    parser.add_argument("-o", "--output-dir", default=".")
    parser.add_argument("--newdata", default="newdata.txt")
    args = parser.parse_args()

    run_htmlturbo(
        datafile=args.datafile,
        unique=args.unique,
        option=args.option,
        output_dir=args.output_dir,
        newdatafile=args.newdata,
    )

if __name__ == "__main__":
    main()

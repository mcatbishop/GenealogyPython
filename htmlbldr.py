#!/usr/bin/env python3
import argparse
from genealogy import run_htmlbldr

def main():
    parser = argparse.ArgumentParser(
        description="Python translation of the C++ htmlbldr program."
    )
    parser.add_argument("datafile", nargs="?", default="sorted.txt")
    parser.add_argument("unique", nargs="?", default="X")
    option_group = parser.add_mutually_exclusive_group()
    option_group.add_argument("-d", dest="opt_d", action="store_true",
                              help="generate date index")
    option_group.add_argument("-g", dest="opt_g", action="store_true",
                              help="generate generation index")
    parser.add_argument("-o", "--output-dir", default=".")
    parser.add_argument("--newdata", default="newdata.txt")
    args = parser.parse_args()

    option = "-d" if args.opt_d else ("-g" if args.opt_g else None)

    run_htmlbldr(
        datafile=args.datafile,
        unique=args.unique,
        option=option,
        output_dir=args.output_dir,
        newdatafile=args.newdata,
    )

if __name__ == "__main__":
    main()

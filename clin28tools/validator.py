#!/usr/bin/env python3

import sys
import os.path
import argparse
import json
import codecs
from clin28tools.format import CLIN28JSON

def main():
    parser = argparse.ArgumentParser(description="Validates the JSON format for the CLIN 28 shared task", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('files', nargs='+', help='JSON files to validate')
    args = parser.parse_args()

    for filename in args.files:
        try:
            data = CLIN28JSON(filename) #validation is implied
        except Exception as e:
            print("INVALID! -> " + filename + ": ", str(e),file=sys.stderr)
            sys.exit(1)
        print("valid -> " + filename,file=sys.stderr)

if __name__ == '__main__':
    main()

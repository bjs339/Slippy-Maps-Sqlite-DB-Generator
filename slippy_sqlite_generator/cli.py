import sys
import argparse
from slippy_sqlite_generator import SlippySqliteGenerator


def _create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image",
                        required=True,
                        help="Input image file full path")
    parser.add_argument("-d", "--db",
                        required=True,
                        help="Output database file (name only)")
    return parser

def get_args(raw_args):
    parser = _create_parser()
    args = parser.parse_args(raw_args)

    if not args.image:
        parser.error("Input image file is required")

    if not args.db:
        parser.error("Output database is required")

    return args

def main(raw_args):
    args = get_args(raw_args)
    slippySqliteGenerator = SlippySqliteGenerator(args.image, args.db)
    slippySqliteGenerator.process()

if __name__ == "__main__":
    main(sys.argv[1:])

#!/usr/bin/python

import argparse
from playlists import PlayListChange

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-i","--input_file", help="input json file",
                        required=True)
arg_parser.add_argument("-c", "--change_file", help="change file in csv "
                                                    "format", required=True)
arg_parser.add_argument("-o","--output_file", help="ouput json file",
                        required=True)
args = arg_parser.parse_args()


if __name__ == '__main__':
    PlayListChange(args.input_file, args.change_file, args.output_file).start()

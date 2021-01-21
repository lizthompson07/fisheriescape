import argparse
import json
import os

def nz(value, arg):
    """if a value is equal to None, this function will return arg instead"""
    if value is None or value == "":
        return arg
    else:
        return value

parser = argparse.ArgumentParser()
parser.add_argument('--git-version', help='')

args = parser.parse_args()

with open(".env_temp", 'w') as write_file:
    with open(".env", 'r') as read_file:
        for line in read_file:
            if line.startswith("GIT_VERSION"):
                write_file.write(f'GIT_VERSION={args.git_version}\n')
            else:
                write_file.write(line)

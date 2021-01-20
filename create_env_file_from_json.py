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
parser.add_argument('--environment_name', help='"dev", "test" or "prod"')

args = parser.parse_args()

if args.environment_name not in ["dev", "test", "prod"]:
    print("Bad environment name. Please choose between the following: {dev | test | prod}")

new_file = os.path.join(".env_stage1")
with open(new_file, 'w') as write_file:
    with open('azure_scripts/public_environmental_vars.json') as f:
        var_dict = json.load(f)

    print(var_dict)


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
parser.add_argument('--environment-name', help='"dev", "test" or "prod"')
parser.add_argument('--output-file-name', help='name of output file', default=".env")

args = parser.parse_args()

if args.environment_name not in ["dev", "test", "prod"]:
    print("Bad environment name. Please choose between the following: {dev | test | prod}")

new_file = os.path.join(args.output_file_name)
with open(new_file, 'w') as write_file:
    with open('azure_scripts/public_environmental_vars.json') as f:
        var_dict = json.load(f)

    env = args.environment_name
    for key in var_dict:
        val = var_dict[key]
        if isinstance(val, dict):
            val = val[env]

        write_file.write(f'{key}="{val}"\n')

import os
import argparse

from lib.templatetags.custom_filters import nz

parser = argparse.ArgumentParser()
parser.add_argument('--app-id', help='application id issued by AAD')
parser.add_argument('--app-secret', help='application secret issued by AAD')
args = parser.parse_args()


new_file = os.path.join("azure_oauth_settings.yml")
with open(new_file, 'w') as write_file:
    write_file.write('app_id: "{}"\n'.format(nz(args.app_id, "")))
    write_file.write('app_secret: "{}"\n'.format(nz(args.app_secret, "")))
    write_file.write('redirect: "https://dmapps-dev.azurewebsites.net/accounts/callback"\n')
    write_file.write('scopes: "openid user.read"\n')
    write_file.write('authority: "https://login.microsoftonline.com/1594fdae-a1d9-4405-915d-011467234338"\n')
    write_file.write('authorize_endpoint: "/oauth2/v2.0/authorize"\n')
    write_file.write('token_endpoint: "/oauth2/v2.0/token"\n')

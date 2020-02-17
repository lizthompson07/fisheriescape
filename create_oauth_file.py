import os
import sys

new_file = os.path.join("oauth_settings.yml")
with open(new_file, 'w') as write_file:
    write_file.write('app_id: "{}"\n'.format(sys.argv[1]))
    write_file.write('app_secret: "{}"\n'.format(sys.argv[2]))
    write_file.write('redirect: "https://dmapps-dev.azurewebsites.net/accounts/callback"\n')
    write_file.write('scopes: "openid user.read"\n')
    write_file.write('authority: "https://login.microsoftonline.com/1594fdae-a1d9-4405-915d-011467234338"\n')
    write_file.write('authorize_endpoint: "/oauth2/v2.0/authorize"\n')
    write_file.write('token_endpoint: "/oauth2/v2.0/token"\n')



import argparse
import os

def nz(value, arg):
    """if a value is equal to None, this function will return arg instead"""
    if value is None or value == "":
        return arg
    else:
        return value

parser = argparse.ArgumentParser()
parser.add_argument('--app-id', help='application id issued by AAD')
parser.add_argument('--secret-key', help='')
parser.add_argument('--google-api-key', help='')
parser.add_argument('--sendgrid-api-key', help='')
parser.add_argument('--dev-db-host', help='')
parser.add_argument('--dev-db-port', help='')
parser.add_argument('--dev-db-name', help='')
parser.add_argument('--dev-db-user', help='')
parser.add_argument('--dev-db-password', help='')
parser.add_argument('--prod-db-host', help='')
parser.add_argument('--prod-db-port', help='')
parser.add_argument('--prod-db-name', help='')
parser.add_argument('--prod-db-user', help='')
parser.add_argument('--prod-db-password', help='')

parser.add_argument('--email-host', help='')
parser.add_argument('--email-user', help='')
parser.add_argument('--email-password', help='')
parser.add_argument('--email-port', help='')
parser.add_argument('--email-use-tls', help='')

parser.add_argument('--oauth-app-id', help='')
parser.add_argument('--oauth-app-secret', help='')
parser.add_argument('--oauth-redirect', help='')
parser.add_argument('--oauth-scopes', help='')
parser.add_argument('--oauth-authority', help='')
parser.add_argument('--oauth-authorize-endpoint', help='')
parser.add_argument('--oauth-token-endpoint', help='')




args = parser.parse_args()

new_file = os.path.join(".env")
with open(new_file, 'w') as write_file:
    write_file.write("# General\n")
    write_file.write("SECRET_KEY = {}\n".format(nz(args.secret_key, "")))
    write_file.write("GOOGLE_API_KEY = {}\n".format(nz(args.google_api_key, "")))
    write_file.write("SENDGRID_API_KEY = {}\n".format(nz(args.sendgrid_api_key, "")))
    write_file.write("\n# Credentials for Dev Database\n")
    write_file.write("DEV_DB_HOST = {}\n".format(nz(args.dev_db_host, "")))
    write_file.write("DEV_DB_PORT = {}\n".format(nz(args.dev_db_port, "")))
    write_file.write("DEV_DB_NAME = {}\n".format(nz(args.dev_db_name, "")))
    write_file.write("DEV_DB_USER = {}\n".format(nz(args.dev_db_user, "")))
    write_file.write("DEV_DB_PASSWORD = {}\n".format(nz(args.dev_db_password, "")))
    write_file.write("\n# Credentials for Production Database\n")
    write_file.write("PROD_DB_HOST = {}\n".format(nz(args.prod_db_host, "")))
    write_file.write("PROD_DB_PORT = {}\n".format(nz(args.prod_db_port, "")))
    write_file.write("PROD_DB_NAME = {}\n".format(nz(args.prod_db_name, "")))
    write_file.write("PROD_DB_USER = {}\n".format(nz(args.prod_db_user, "")))
    write_file.write("PROD_DB_PASSWORD = {}\n".format(nz(args.prod_db_password, "")))
    write_file.write("\n# Credentials for Email Service\n")
    write_file.write("EMAIL_HOST = {}\n".format(nz(args.email_host, "")))
    write_file.write("EMAIL_HOST_USER = {}\n".format(nz(args.email_user, "")))
    write_file.write("EMAIL_HOST_PASSWORD = {}\n".format(nz(args.email_password, "")))
    write_file.write("EMAIL_PORT = {}\n".format(nz(args.email_port, "")))
    write_file.write("EMAIL_USE_TLS = {}\n".format(nz(args.email_use_tls, "")))
    write_file.write("\n# Oauth Credentials for AAD\n")
    write_file.write("app_id = {}\n".format(nz(args.oauth_app_id, "")))
    write_file.write("app_secret = {}\n".format(nz(args.oauth_app_secret, "")))
    write_file.write("redirect = {}\n".format(nz(args.oauth_redirect, "")))
    write_file.write("scopes = {}\n".format(nz(args.oauth_scopes, "")))
    write_file.write("authority = {}\n".format(nz(args.oauth_authority, "")))
    write_file.write("authorize_endpoint = {}\n".format(nz(args.oauth_authorize_endpoint, "")))
    write_file.write("token_endpoint = {}\n".format(nz(args.oauth_token_endpoint, "")))



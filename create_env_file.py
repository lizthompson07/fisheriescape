import os
import sys

new_file = os.path.join(".env")
with open(new_file, 'w') as write_file:
    write_file.write("SECRET_KEY = {}\n".format(sys.argv[1]))
    write_file.write("GOOGLE_API_KEY = {}\n".format(sys.argv[2]))
    write_file.write("DEV_DB_HOST = {}\n".format(sys.argv[3]))
    write_file.write("DEV_DB_PORT = {}\n".format(sys.argv[4]))
    write_file.write("DEV_DB_NAME = {}\n".format(sys.argv[5]))
    write_file.write("DEV_DB_USER = {}\n".format(sys.argv[6]))
    write_file.write("DEV_DB_PASSWORD = {}\n".format(sys.argv[7]))
    write_file.write("EMAIL_HOST = {}\n".format(sys.argv[8]))
    write_file.write("EMAIL_HOST_USER = {}\n".format(sys.argv[9]))
    write_file.write("EMAIL_HOST_PASSWORD = {}\n".format(sys.argv[10]))
    write_file.write("EMAIL_PORT = {}\n".format(sys.argv[11]))
    write_file.write("EMAIL_USE_TLS = {}\n".format(sys.argv[12]))


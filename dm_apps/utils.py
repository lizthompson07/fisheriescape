from decouple import config, UndefinedValueError

def is_connection_available(prefix):
    try:
        return config(prefix + '_DB_HOST') and \
               config(prefix + '_DB_PORT') and \
               config(prefix + '_DB_NAME') and \
               config(prefix + '_DB_USER') and \
               config(prefix + '_DB_PASSWORD')
    except UndefinedValueError:
        return False
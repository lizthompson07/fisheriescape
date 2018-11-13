from . import media_conf

MY_ENVR = media_conf.where_am_i()

class DevDatabaseRouter:
    """
    A router to control all database operations on models in the
    auth application
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read any models will always look at the production db ("default").
        """

        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write any models will depend on the dev environment.
        """
        # print(model._meta.app_label)
        if MY_ENVR == 'dev':
            if model._meta.app_label == 'auth' or model._meta.app_label == 'sessions':
                return None
            else:
                return 'dev_db'
        else:
            return None

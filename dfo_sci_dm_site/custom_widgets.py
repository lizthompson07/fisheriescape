from django.db import models


class OracleTextField(models.TextField):
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.oracle':
            return 'NVARCHAR2(2000)'
        else:
            return super.db_type(self, connection)

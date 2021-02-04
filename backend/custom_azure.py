from decouple import config
from django.conf import settings
from msrestazure.azure_active_directory import MSIAuthentication
from storages.backends.azure_storage import AzureStorage

AZURE_STORAGE_ACCOUNT_NAME = config("AZURE_STORAGE_ACCOUNT_NAME", cast=str, default="")
AZURE_MSI_CLIENT_ID = config("AZURE_MSI_CLIENT_ID", cast=str, default="")

token_credential = None
account_key = config("AZURE_STORAGE_SECRET_KEY", default=None)
try:
    token_credential = MSIAuthentication(resource=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net', client_id=AZURE_MSI_CLIENT_ID)
except:
    pass


# from https://medium.com/@DawlysD/django-using-azure-blob-storage-to-handle-static-media-assets-from-scratch-90cbbc7d56be
class AzureMediaStorage(AzureStorage):
    account_name = AZURE_STORAGE_ACCOUNT_NAME
    token_credential = token_credential
    account_key = account_key
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = AZURE_STORAGE_ACCOUNT_NAME
    token_credential = token_credential
    account_key = account_key
    azure_container = '$web'
    expiration_secs = None

    def url(self, name, expire=None):
        return settings.STATIC_URL + self._get_valid_path(name)

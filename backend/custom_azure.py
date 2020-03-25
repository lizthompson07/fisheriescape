from decouple import config
from msrestazure.azure_active_directory import MSIAuthentication
from storages.backends.azure_storage import AzureStorage

AZURE_STORAGE_ACCOUNT_NAME = config("AZURE_STORAGE_ACCOUNT_NAME", cast=str, default="")
token_credential = MSIAuthentication(resource=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net')


# from https://medium.com/@DawlysD/django-using-azure-blob-storage-to-handle-static-media-assets-from-scratch-90cbbc7d56be
class AzureMediaStorage(AzureStorage):
    account_name = AZURE_STORAGE_ACCOUNT_NAME
    token_credential = token_credential
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = AZURE_STORAGE_ACCOUNT_NAME
    token_credential = token_credential
    azure_container = 'static'
    expiration_secs = None

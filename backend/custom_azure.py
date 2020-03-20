from django.conf import settings
from storages.backends.azure_storage import AzureStorage


# from https://medium.com/@DawlysD/django-using-azure-blob-storage-to-handle-static-media-assets-from-scratch-90cbbc7d56be
class AzureMediaStorage(AzureStorage):
    account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
    token_credential = settings.token_credential
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
    token_credential = settings.token_credential
    azure_container = 'static'
    expiration_secs = None

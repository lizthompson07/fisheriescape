from decouple import config
from storages.backends.azure_storage import AzureStorage
from msrestazure.azure_active_directory import MSIAuthentication
token_credential = MSIAuthentication(resource='https://dmappsdev.blob.core.windows.net')


# from https://medium.com/@DawlysD/django-using-azure-blob-storage-to-handle-static-media-assets-from-scratch-90cbbc7d56be
class AzureMediaStorage(AzureStorage):
    account_name = 'dmappsdev'
    token_credential = token_credential
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = 'dmappsdev'  # Must be replaced by your storage_account_name
    token_credential = token_credential
    azure_container = 'static'
    expiration_secs = None

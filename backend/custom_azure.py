import requests
from decouple import config
from django.conf import settings
from storages.backends.azure_storage import AzureStorage

AZURE_STORAGE_ACCOUNT_NAME = config("AZURE_STORAGE_ACCOUNT_NAME", cast=str, default="")


def get_auth_token():
    url = 'http://169.254.169.254/metadata/identity/oauth2/token'
    params = {"api-version": "2018-02-01", "resource": "https://management.azure.com/"}
    headers = {'Metadata': 'true'}
    r = requests.get(url, headers=headers, params=params)
    return r.json()["access_token"]


# from https://medium.com/@DawlysD/django-using-azure-blob-storage-to-handle-static-media-assets-from-scratch-90cbbc7d56be
class AzureMediaStorage(AzureStorage):
    account_name = AZURE_STORAGE_ACCOUNT_NAME
    token_credential = get_auth_token()

    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = AZURE_STORAGE_ACCOUNT_NAME
    token_credential = get_auth_token()
    azure_container = '$web'
    expiration_secs = None

    def url(self, name, expire=None):
        return settings.STATIC_URL + self._get_valid_path(name)

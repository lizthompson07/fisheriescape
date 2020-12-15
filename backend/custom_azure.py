from decouple import config
from django.conf import settings
from msrestazure.azure_active_directory import MSIAuthentication
from storages.backends.azure_storage import AzureStorage
import adal

TENANT_ID = "1594fdae-a1d9-4405-915d-011467234338"
# Azure CLI Client ID - fixed ID
CLIENT_ID = "b9b8533b-430c-4b7a-95b7-0c8d43179f68"
AUTH_URI = "https://login.microsoftonline.com" + "/" + TENANT_ID
# SUBSCRIPTION_ID = "3eb57d27-b726-402d-8cfe-a9a846b99121"
# RG_NAME = "IMTS DEV/TEST"


AZURE_STORAGE_ACCOUNT_NAME = config("AZURE_STORAGE_ACCOUNT_NAME", cast=str, default="")
# IN_PIPELINE = config("IN_PIPELINE", cast=bool, default=False)

# if IN_PIPELINE:
#     print("we are in a pipeline :)")
#     account_key = config("AZURE_STORAGE_SECRET_KEY", cast=str, default="")
# else:
#     account_key = config("AZURE_STORAGE_SECRET_KEY", cast=str, default="")
    # token_credential = MSIAuthentication(resource=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net')

# inspired by https://azsec.azurewebsites.net/2019/12/20/a-few-ways-to-acquire-azure-access-token-with-scripting-languages/
def get_auth_token():
    context = adal.AuthenticationContext(AUTH_URI)
    code = context.acquire_user_code('https://management.core.windows.net/', CLIENT_ID)
    message = code['message']
    #You must print message
    print(message)
    token = context.acquire_token_with_device_code('https://management.core.windows.net/',
                                                code,
                                                CLIENT_ID)
    authHeader = {
        'Authorization': 'Bearer ' + token['accessToken'],
        'Content-Type': 'application/json'
    }
    return authHeader


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

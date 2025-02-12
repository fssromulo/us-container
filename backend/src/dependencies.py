# Internal imports
from src.auth.auth import Auth0


auth = Auth0(api_audience='containerCrmApi', scopes={'read:blabla': ''})

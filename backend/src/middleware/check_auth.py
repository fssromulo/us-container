# pip imports
# Python imports
from typing import Union

# Pip imports
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes

# Internal imports
from src.auth.auth import Auth0User

# internal imports
from src.dependencies import auth


async def check_auth(request: Request) -> Union[None, Auth0User]:
    for header in request.scope['headers']:
        # Decode header[0] (key) from bytes to str and check if it's 'authorization'
        if 'authorization' == header[0].decode().lower():
            # Decode the header value from bytes to str
            auth_header_value = header[1].decode()

            # Check if the authorization header starts with 'Basic'
            if auth_header_value.lower().startswith('basic'):
                return  # It's a Basic Auth, so we skip further processing

            # Extract the scheme and credentials after 'Basic' assuming there's a space
            # This is useful for other types of authorization header processing

            scheme, credentials = auth_header_value.split(" ", 1)
            creds = HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

            # For non-Basic auth calls, proceed with your logic
            user = await auth.get_user(SecurityScopes([]), creds)
            return user

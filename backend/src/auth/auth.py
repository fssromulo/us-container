# Python imports
import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Type

# Pip imports
from fastapi import Depends, HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2, SecurityScopes
from jose import jwt  # type: ignore
from loguru import logger
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import TypedDict


auth0_rule_namespace: str = os.getenv('AUTH0_RULE_NAMESPACE', 'https://github.com/dorinclisu/fastapi-auth0')
DOMAINS = [
    "container-crm.us.auth0.com",
    "container-crm-shared.us.auth0.com",
    "dev-q7gskrpgi0lqzizg.us.auth0.com",
]


class Auth0UnauthenticatedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """
        Returns HTTP 401
        """
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, **kwargs)


class Auth0UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """
        Returns HTTP 403
        """
        super().__init__(status.HTTP_403_FORBIDDEN, detail, **kwargs)


class HTTPAuth0Error(BaseModel):
    detail: str


unauthenticated_response: Dict = {status.HTTP_401_UNAUTHORIZED: {'model': HTTPAuth0Error}}
unauthorized_response: Dict = {status.HTTP_403_FORBIDDEN: {'model': HTTPAuth0Error}}
security_responses: Dict = {**unauthenticated_response, **unauthorized_response}


class Auth0User(BaseModel):
    id: str = Field(..., alias='sub')
    permissions: Optional[List[str]]
    email: Optional[str] = Field(None, alias=f'{auth0_rule_namespace}/email')
    app_metadata: Optional[dict] = Field(None, alias=f'{auth0_rule_namespace}/app_metadata')

    class Config:
        allow_population_by_field_name = True


class Auth0HTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        return await super().__call__(request)


class OAuth2ImplicitBearer(OAuth2):
    def __init__(
        self,
        authorizationUrl: str,
        scopes: Dict[str, str] = {},
        scheme_name: Optional[str] = None,
        auto_error: bool = True,
    ):
        flows = OAuthFlows(implicit={'authorizationUrl': authorizationUrl, 'scopes': scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # Overwrite parent call to prevent useless overhead, the actual auth is done in Auth0.get_user
        # This scheme is just for Swagger UI
        return None


class JwksKeyDict(TypedDict):
    kid: str
    kty: str
    use: str
    n: str
    e: str


class JwksDict(TypedDict):
    keys: List[JwksKeyDict]


class Auth0:
    def __init__(
        self,
        api_audience: str,
        scopes: Dict[str, str] = None,
        auto_error: bool = True,
        scope_auto_error: bool = True,
        email_auto_error: bool = False,
        auth0user_model: Type[Auth0User] = Auth0User,
    ):
        self.audience = api_audience

        self.auto_error = auto_error
        self.scope_auto_error = scope_auto_error
        self.email_auto_error = email_auto_error

        self.auth0_user_model = auth0user_model

        self.algorithms = ['RS256']

        self.jwks_dict = {}
        self.authorization_urls = {}
        for domain in DOMAINS:
            self.jwks_dict[domain] = self.get_jwks(domain)
            self.authorization_urls[domain] = self.get_authorization_url(domain)

        # self.jwks = self.get_jwks()

        # self.authorization_url = self.get_authorization_url()
        self.implicit_scheme = self.implicit_scheme(scopes=scopes)
        # self.password_scheme = self.password_scheme(scopes=scopes)
        # self.authcode_scheme = self.authcode_scheme(scopes=scopes)
        # self.oidc_scheme = self.oidc_scheme()

    async def get_user(
        self,
        security_scopes: SecurityScopes,
        creds: Optional[HTTPAuthorizationCredentials] = Depends(Auth0HTTPBearer(auto_error=False)),
    ) -> Optional[Auth0User]:
        """
        Verify the Authorization: Bearer token and return the user.
        If there is any problem and auto_error = True then raise Auth0UnauthenticatedException
        or Auth0UnauthorizedException, otherwise return None.

        Not to be called directly, but to be placed within a 'Depends()' or 'Security()' wrapper.
        Example: def path_op_func(user: Auth0User = Security(auth.get_user)).
        """
        if creds is None:
            if self.auto_error:
                # See HTTPBearer from FastAPI:
                # latest - https://github.com/tiangolo/fastapi/blob/master/fastapi/security/http.py
                # 0.65.1 - https://github.com/tiangolo/fastapi/blob/aece74982d7c9c1acac98e2c872c4cb885677fc7/fastapi/security/http.py
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, detail='Missing bearer token'
                )  # must be 403 until solving https://github.com/tiangolo/fastapi/pull/2120

            return None

        token = creds.credentials
        payload: Dict = {}
        successful_payloads = {}
        try:
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            rsa_key_dict = {}
            for domain in DOMAINS:
                for key in self.jwks_dict[domain]['keys']:
                    try:
                        if key['kid'] == unverified_header['kid']:
                            rsa_key = {
                                'kty': key['kty'],
                                'kid': key['kid'],
                                'use': key['use'],
                                'n': key['n'],
                                'e': key['e'],
                            }
                            rsa_key_dict[domain] = rsa_key
                            break
                    except Exception as e:
                        logger.info(e)
                        continue
                if rsa_key_dict.get(domain):
                    payload = jwt.decode(
                        token,
                        rsa_key_dict[domain],
                        algorithms=self.algorithms,
                        audience=self.audience,
                        issuer=f'https://{domain}/',
                    )
                    successful_payloads[domain] = payload

            if len(successful_payloads) == 0:
                msg = 'Invalid kid header (wrong tenant or rotated public key)'
                if self.auto_error:
                    logger.info(msg)
                    raise Auth0UnauthenticatedException(detail=msg)
                else:
                    logger.warning(msg)
                    return None

        except jwt.ExpiredSignatureError:
            msg = 'Expired token'
            if self.auto_error:
                raise Auth0UnauthenticatedException(detail=msg)
            else:
                logger.warning(msg)
                return None
        except jwt.JWTClaimsError:
            msg = 'Invalid token claims (wrong issuer or audience)'
            if self.auto_error:
                raise Auth0UnauthenticatedException(detail=msg)
            else:
                logger.warning(msg)
                return None
        except jwt.JWTError:
            msg = 'Malformed token'
            if self.auto_error:
                raise Auth0UnauthenticatedException(detail=msg)
            else:
                logger.warning(msg)
                return None

        except Auth0UnauthenticatedException:
            raise
        except Exception as e:
            # This is an unlikely case but handle it just to
            # be safe (maybe the token is specially crafted to bug our code)
            logger.error(f'Handled exception decoding token: "{e}"', exc_info=True)
            if self.auto_error:
                raise Auth0UnauthenticatedException(detail='Error decoding token')
            else:
                return None

        if self.scope_auto_error:
            token_scope_str: str = payload.get('scope', '')

            if isinstance(token_scope_str, str):
                token_scopes = token_scope_str.split()

                for scope in security_scopes.scopes:
                    if scope not in token_scopes:
                        raise Auth0UnauthorizedException(
                            detail=f'Missing "{scope}" scope',
                            headers={'WWW-Authenticate': f'Bearer scope="{security_scopes.scope_str}"'},
                        )
            else:
                # This is an unlikely case but handle it just to be safe (perhaps auth0 will change the scope format)
                raise Auth0UnauthorizedException(detail='Token "scope" field must be a string')

        try:
            user = self.auth0_user_model(**payload)
            if self.email_auto_error and not user.email:
                raise Auth0UnauthorizedException(
                    detail='Missing email claim (check auth0 rule "Add email to access token")'
                )
            return user
        except ValidationError as e:
            logger.error(f'Handled exception parsing Auth0User: "{e}"', exc_info=True)
            if self.auto_error:
                raise Auth0UnauthorizedException(detail='Error parsing Auth0User')

            return None

    def get_jwks(self, domain) -> JwksDict:
        """
        Return the jwks dict.
        """
        r = urllib.request.urlopen(f'https://{domain}/.well-known/jwks.json')
        return json.loads(r.read())

    def get_authorization_url(self, domain) -> str:
        """
        Return the authorization url.
        """
        authorization_url_qs = urllib.parse.urlencode({'audience': self.audience})
        return f'https://{domain}/authorize?{authorization_url_qs}'

    def implicit_scheme(self, scopes: Dict[str, str] = None) -> OAuth2ImplicitBearer:
        """
        Return the OAuth2ImplicitBearer scheme.
        """
        if scopes is None:
            scopes = {}
        implicit_bearers = {}
        for domain in DOMAINS:
            implicit_bearers[domain] = OAuth2ImplicitBearer(
                authorizationUrl=self.authorization_urls[domain], scopes=scopes, scheme_name='Auth0ImplicitBearer'
            )
        return implicit_bearers[DOMAINS[0]]

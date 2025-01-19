from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.exceptions import HTTPException
from .utils import decode_token
from fastapi.security.http import HTTPAuthorizationCredentials
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from typing import List,Any
from src.db.models import User
from src.errors import (InvalidToken, RefreshTokenRequired, AccessTokenRequired, InsufficientPermission, AccountNotVerified)

user_service = UserService()

class TokenBearer(HTTPBearer):
    
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

# rest of the code for checking token is valid
    async def __call__(self, request : Request) -> HTTPAuthorizationCredentials | None:
        creds =  await super().__call__(request)
        # here scheme = bearer and credentials = access token
        print("Scehme =",creds.scheme)
        print("credentials =",creds.credentials)

        token = creds.credentials
        token_data = decode_token(token)

        if not self.token_valid(token):
             raise InvalidToken()
            # instead of httpexception we can simply use invalid token class
            # raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = 
            #                    { "error" : "Invalid or expired tokens",
            #                      "resolution" : "Please get new token"})
        
        if await token_in_blocklist(token_data['jti']):
             raise InvalidToken()
            #  raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, 
            #                      detail = {"error" : "This token is invalid or has been revoke", 
            #                      "resolution" : "Please get new token"})

        self.verify_token_data(token_data)
        # return creds
        # print("token_data = ",token_data) == user_details in get all books 
        return token_data
    
    def token_valid(self, token:str) -> bool:
        token_data = decode_token(token)

        return True if token_data is not None else False 

    def verify_token_data(self, token_data):
         return NotImplementedError("Please Override this method in child classes")

# for checking valid access token is provided or not 
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data : dict) -> None:
        if token_data and token_data['refresh']:
             raise AccessTokenRequired()
                # raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Please provide an access token" )


# for checking valid refresh token is provided or not 
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data : dict) -> None:
        if token_data and not token_data['refresh']:
             raise RefreshTokenRequired()
                # raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Please provide a refresh token" )
        
# for role based access control 
async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
     
     user_email = token_details["user"]["email"]
     user = await user_service.get_user_by_email(user_email, session)

     return user

class RoleChecker:
     def __init__(self, allowed_roles: List[str]) -> None:
         
          self.allowed_roles = allowed_roles

     def __call__(self, current_user: User= Depends(get_current_user)) -> Any:
          
          if not current_user.is_verified:
               raise AccountNotVerified()

          if current_user.role in self.allowed_roles:
               return True
          else:
               raise InsufficientPermission()
            #    raise HTTPException(
            #         status_code= status.HTTP_403_FORBIDDEN, 
            #         detail= "You are not allowed to perform this action")
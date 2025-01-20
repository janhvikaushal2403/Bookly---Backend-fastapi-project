from fastapi import APIRouter, Depends, status, BackgroundTasks
from .schemas import (
    UserCreateModel,
    UserModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from .service import UserService
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .utils import (
    create_access_token,
    decode_token,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
    generate_hash_passord,
)
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from src.mail import mail, create_message
from src.config import Config
# from src.celery_tasks import send_email

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post('/send_mail')
async def send_mail(emails: EmailModel):
    emails = emails.email_addresses
    html  = "<h1> Welcome to the app </h1>"

    subject = "Welcome"
    # using celery tasks
    # send_email.delay(emails, subject, html)
    message = create_message(
        recipients = emails,
        subject="Welcome",
        body = html
    )
    await mail.send_message(message)
    return {"message" : "Email sent successfully"}


@auth_router.post('/signup', status_code= status.HTTP_201_CREATED)
async def create_user_acccounts(user_data: UserCreateModel,bg_tasks : BackgroundTasks ,session: AsyncSession = Depends(get_session)):
    print("create user api working...")

    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        print("user exists")
        raise UserAlreadyExists()
        # raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "User with email already exists" )
    
    print("new user created")
    new_user = await user_service.create_user(user_data, session)
    
    # for sending and verifying email, also remove response model as we are returning output in dict form otheriwse it will give an error
    token  = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p1>Please click this <a href = "{link}"> link</a> to verify you email</p1>
    """
    emails = [email]
    subject = "Verify your email"
    message = create_message(
        recipients = [email],
        subject="Verify you email",
        body = html_message
    )
    # instead of await we can directly use background tasks as -
    await mail.send_message(message)
    # bg_tasks.add_task(mail.send_message, message)

    # send_email.delay(emails, subject, html_message)
    return{
        "message" : "Account Created! check you email to verify you account",
        "user": new_user
    }
    # return new_user

# creating endpoint for verifying mail
@auth_router.get('/verify/{token}')
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get('email')
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        
        if not user:
            raise UserNotFound()
        
        await user_service.update_user(user,{ 'is_verified' : True}, session)
        return JSONResponse(
            content = {
                "message" : "Account verified successfully"
            },
            status_code = status.HTTP_200_OK
        )
    return JSONResponse(
      content = { "message": "Error occured during verification"},
      status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@auth_router.post('/login')
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email,session)
    # print(user)
    if user is None:
        raise InvalidCredentials()
    
    valid_password = verify_password(password, user.password)
    if not valid_password:
        raise InvalidCredentials()
    
    access_token = create_access_token(
                user_data = {
                    'email' : user.email,
                    'user_uid': str(user.uid),
                    'role': user.role
                }     
            )    
    refresh_token = create_access_token(
                user_data = {
                    'email' : user.email,
                    'user_uid': str(user.uid)
                },
                refresh = True,
                expiry = timedelta(days = REFRESH_TOKEN_EXPIRY)  
            )   
    return JSONResponse(
                content ={
                    "message": "login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user":{
                        "email": user.email,
                        "user_uid": str(user.uid)
                    }
                }
            ) 
    # if user is not None:
    #     valid_password = verify_password(password, user.password)
    #     if valid_password:
    #         access_token = create_access_token(
    #             user_data = {
    #                 'email' : user.email,
    #                 'user_uid': str(user.uid),
    #                 'role': user.role
    #             }     
    #         )    
    #         refresh_token = create_access_token(
    #             user_data = {
    #                 'email' : user.email,
    #                 'user_uid': str(user.uid)
    #             },
    #             refresh = True,
    #             expiry = timedelta(days = REFRESH_TOKEN_EXPIRY)  
    #         )   
    #         return JSONResponse(
    #             content ={
    #                 "message": "login successful",
    #                 "access_token": access_token,
    #                 "refresh_token": refresh_token,
    #                 "user":{
    #                     "email": user.email,
    #                     "user_uid": str(user.uid)
    #                 }
    #             }
    #         ) 
    # else:
    #     raise InvalidCredentials()
        # raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Invalid email or password")


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    
    print("refresh token api...")
    expiry_timestamp = token_details['exp']
    print("expiry_timestamp = ",expiry_timestamp)

# converting expiry_timestamp  into date time
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data = token_details['user'])
        return JSONResponse(content = {
            "access_token": new_access_token
            })

    raise InvalidToken()
    # raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Invalid or Expired token")

#  by using the response model we will get the list of books too with the current login user
@auth_router.get('/me', response_model = UserBooksModel)
async def get_current_user(user = Depends(get_current_user),check_role : bool = Depends(role_checker)):
    return user


@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)
    return JSONResponse(content ={"message":"Logged out successfully"}, status_code= status.HTTP_200_OK)

#  endpoint for password reset
@auth_router.post('/password-reset-request')
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    message = create_message(
        recipients = [email],
        subject = "Reset Your Password",
        body = html_message
    )
    await mail.send_message(message)

    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        passwd_hash = generate_hash_passord(new_password)
        await user_service.update_user(user, {"password": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

# @auth_router.delete('/{user_uid}', status_code= status.HTTP_204_NO_CONTENT)
# async def delete_user(user_uid : str,session: AsyncSession = Depends(get_session)):
#     print("delete api working....")
#     user_to_delete = await UserService.delete_users(user_uid, session)
#     if user_to_delete is None:
#        print("user not found")
#        raise UserNotFound()
#     #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

#     else:
#        print("User deleted successfully")
#        return None

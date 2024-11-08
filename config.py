import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import HTTPException, Request
from typing import Optional
import jwt
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from typing import Union

''' This part should be same for each project'''
load_dotenv()

password = os.environ.get("PASSWORD")
db_name = os.environ.get("POSTGRES_DB")
host = os.environ.get("HOST")
port= os.environ.get("PORT")
algorithm= os.environ.get("ALGORITHM")
access_token_expire_minutes= os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
email = os.environ.get("EMAIL")
epassword= os.environ.get("EPASSWORD")
secret_key= os.environ.get("SECRET_KEY")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="You are not loged in. Go to Home page and login again.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

security = OAuth2PasswordBearerCookie(token_url="/users/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_hashed_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def get_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")

        if username is not None:
            token_data = username
            return token_data
    except jwt.JWTError:
        return None

''' This part should be modified for each project if needed '''
def generate_secret():
    return ''.join(random.choices('0123456789abcdefghijklmnopqrsty', k=16))

def send_key_to_mail(db_email: str, key: str):
    port = 587
    smtp_server = "smtp-mail.outlook.com"
    sender = email
    receiver = db_email
    password = epassword

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Request for secret key"
    msg["From"] = sender
    msg["To"] = receiver

    text = f"Hello.\nYour secret key:\n {key}\nWith regards.\nAgritech Team"
    body = MIMEText(text, 'plain')
    msg.attach(body)

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    print("Email was sent!")
    server.quit()
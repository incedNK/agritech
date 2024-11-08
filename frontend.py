from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import app, ui, Client
from jwt.exceptions import InvalidTokenError
import jwt
from datetime import datetime, timezone

import config
import routes
from system_web import system_router
from aquaterrius_web import aquaterrius_router
from home import home_router

unrestricted_page_routes = {'/', '/price_lists', '/forum', '/login', '/reset_password'}

''' This part should be same for each project'''
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('auth_token', None):
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        else:
            try:
                payload = jwt.decode(app.storage.user['auth_token'],config.secret_key, algorithms=[config.algorithm])
                expire: datetime=payload.get("exp")
                if datetime.now(timezone.utc).timestamp() > expire:
                    app.storage.user.update({'auth_token': None})
            except InvalidTokenError:
                app.storage.user.update({'username': None, 'auth_token': None})
                return RedirectResponse('/login')


        return await call_next(request)


def init(fastapi_app: FastAPI) -> None:
    app.add_static_files('/static', 'static')
    app.include_router(routes.base_router)
    app.include_router(routes.user_router)
    app.include_router(routes.api_router)
    app.include_router(system_router)
    app.include_router(aquaterrius_router)
    app.include_router(home_router)

    app.add_middleware(AuthMiddleware)

    ui.run_with(
        fastapi_app,
        mount_path='/',
        favicon='static/favicon.ico', #This part should be same for each project
        title='AgriTech', #This part should be same for each project
        storage_secret= config.secret_key
    )
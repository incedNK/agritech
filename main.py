import frontend
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import routes

''' This part should be same for each project'''
app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Agritech Docs",
        version="0.1.0",
        description="Custom OpenAPI schema for Agritech API's",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

frontend.init(app)
app.include_router(routes.base_router)
app.include_router(routes.user_router)
app.include_router(routes.api_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
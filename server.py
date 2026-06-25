import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config import get_settings

settings = get_settings()

mcp = FastMCP("da-server")


class BearerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str) -> None:
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] != self.api_key:
            return Response("Unauthorized", status_code=401)
        return await call_next(request)


if __name__ == "__main__":
    asgi_app = mcp.streamable_http_app()
    authed_app = BearerAuthMiddleware(asgi_app, api_key=settings.mcp_api_key.get_secret_value())
    uvicorn.run(authed_app, host=settings.host, port=settings.port)

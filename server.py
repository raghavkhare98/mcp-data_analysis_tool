import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from config import get_settings
from tools.file_tools import register_tools

settings = get_settings()

mcp = FastMCP("da-server")
register_tools(mcp)


class BearerAuthMiddleware:
    """Pure ASGI middleware — does not buffer responses, so SSE streaming works."""

    def __init__(self, app, api_key: str) -> None:
        self.app = app
        self.api_key = api_key

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("method") != "OPTIONS":
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization", b"").decode()
            if not auth.startswith("Bearer ") or auth[7:] != self.api_key:
                response = Response("Unauthorized", status_code=401)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


if __name__ == "__main__":
    asgi_app = mcp.streamable_http_app()
    authed_app = BearerAuthMiddleware(asgi_app, api_key=settings.mcp_api_key.get_secret_value())
    cors_app = CORSMiddleware(
        authed_app,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )
    uvicorn.run(cors_app, host=settings.host, port=settings.port)

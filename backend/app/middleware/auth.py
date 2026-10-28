"""JWT validation middleware: annotates ``request.state.user_id`` when a valid token is present.
Authorization itself is enforced per-route by ``get_current_user``."""
from starlette.middleware.base import BaseHTTPMiddleware

from ..auth import jwt as jwt_tokens
from ..utils.exceptions import Unauthorized


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.user_id = None
        header = request.headers.get("authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() == "bearer" and token:
            try:
                request.state.user_id = jwt_tokens.decode_token(token)["sub"]
            except Unauthorized:
                pass
        return await call_next(request)

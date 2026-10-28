"""JWT validation middleware: rejects invalid bearer tokens early and exposes the claims."""
from __future__ import annotations

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..auth.jwt import decode_token


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        header = request.headers.get("authorization", "")
        request.state.token_claims = None
        if header.lower().startswith("bearer "):
            try:
                request.state.token_claims = decode_token(header[7:], "access")
            except jwt.PyJWTError:
                return JSONResponse({"detail": "Invalid or expired token"}, status_code=401)
        return await call_next(request)

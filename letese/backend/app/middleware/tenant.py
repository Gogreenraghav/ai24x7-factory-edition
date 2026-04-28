# Tenant isolation middleware
# Extracts tenant_id from JWT and adds to request state
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)


async def get_current_tenant(request: Request) -> dict:
    """Extract tenant info from JWT in Authorization header."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.replace("Bearer ", "")
    
    from app.core.security import decode_token
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    role = payload.get("role")
    
    if not all([user_id, tenant_id]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required fields"
        )
    
    # Attach to request state for use in route handlers
    request.state.user_id = user_id
    request.state.tenant_id = tenant_id
    request.state.role = role
    
    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role": role,
    }


async def get_optional_tenant(request: Request) -> Optional[dict]:
    """Same as above but doesn't raise error if no token."""
    try:
        return await get_current_tenant(request)
    except HTTPException:
        return None

"""OAuth authentication routes."""

from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from app.oauth_config import oauth_config
from app.auth_models import User, OAuthUserInfo, Token
from app.database import get_database, DatabaseInterface
from app.auth_utils import create_access_token


router = APIRouter(prefix="/auth", tags=["oauth"])


@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login with provider (google or facebook)."""
    if provider not in ['google', 'facebook']:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")
    
    if provider == 'google' and not oauth_config.is_google_configured:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    
    if provider == 'facebook' and not oauth_config.is_facebook_configured:
        raise HTTPException(status_code=501, detail="Facebook OAuth not configured")
    
    # Get the OAuth client
    client = getattr(oauth_config.oauth, provider)
    
    # Create redirect URI
    redirect_uri = f"{request.base_url}auth/oauth/{provider}/callback"
    
    # Redirect to OAuth provider
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str, 
    request: Request,
    db: DatabaseInterface = Depends(get_database)
):
    """Handle OAuth callback from provider."""
    if provider not in ['google', 'facebook']:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")
    
    try:
        # Get the OAuth client
        client = getattr(oauth_config.oauth, provider)
        
        # Get access token
        token = await client.authorize_access_token(request)
        
        # Get user info from provider
        if provider == 'google':
            user_info = await _get_google_user_info(token)
        elif provider == 'facebook':
            user_info = await _get_facebook_user_info(token)
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
        
        await db.initialize()
        
        # Check if user exists
        existing_user = await db.get_user_by_email(user_info.email)
        
        if existing_user:
            # Update OAuth info if user exists but doesn't have OAuth linked
            if not existing_user.oauth_provider:
                # Link OAuth to existing account
                from app.auth_models import UserUpdate
                await db.update_user(existing_user.id, UserUpdate(
                    oauth_provider=user_info.provider,
                    oauth_id=user_info.provider_id
                ))
            
            user = await db.get_user_by_id(existing_user.id)
        else:
            # Create new OAuth user
            from app.auth_models import UserCreate
            
            # Generate username from email if name not provided
            username = user_info.name or user_info.email.split('@')[0]
            
            # Ensure username is unique
            base_username = username
            counter = 1
            while await db.get_user_by_email(f"{username}@dummy.com"):  # Simple uniqueness check
                username = f"{base_username}{counter}"
                counter += 1
            
            user_create = UserCreate(
                email=user_info.email,
                username=username,
                full_name=user_info.name,
                oauth_provider=user_info.provider,
                oauth_id=user_info.provider_id
            )
            
            user = await db.create_user(user_create)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Redirect to frontend with token
        base_url_str = str(request.base_url)
        if 'localhost' not in base_url_str:
            base_url_str = base_url_str.replace('http:', 'https:', 1)
        frontend_url = f"{base_url_str}?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        # Redirect to frontend with error
        error_url = f"{request.base_url}?error=oauth_failed&message={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/oauth/config")
async def get_oauth_config():
    """Get OAuth configuration for frontend."""
    return {
        "google_enabled": oauth_config.is_google_configured,
        "facebook_enabled": oauth_config.is_facebook_configured,
    }


async def _get_google_user_info(token: Dict[str, Any]) -> OAuthUserInfo:
    """Extract user info from Google OAuth token."""
    user_data = token.get('userinfo')
    if not user_data:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    
    return OAuthUserInfo(
        email=user_data['email'],
        name=user_data.get('name'),
        picture=user_data.get('picture'),
        provider='google',
        provider_id=user_data['sub']
    )


async def _get_facebook_user_info(token: Dict[str, Any]) -> OAuthUserInfo:
    """Extract user info from Facebook OAuth token."""
    import httpx
    
    access_token = token.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token from Facebook")
    
    # Get user info from Facebook Graph API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://graph.facebook.com/me?fields=id,email,name,picture&access_token={access_token}"
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info from Facebook")
        
        user_data = response.json()
    
    return OAuthUserInfo(
        email=user_data['email'],
        name=user_data.get('name'),
        picture=user_data.get('picture', {}).get('data', {}).get('url'),
        provider='facebook',
        provider_id=user_data['id']
    ) 
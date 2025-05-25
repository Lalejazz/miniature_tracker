"""OAuth configuration for Google and Facebook authentication."""

import os
from typing import Optional
from authlib.integrations.starlette_client import OAuth
from decouple import config


class OAuthConfig:
    """OAuth configuration class."""
    
    def __init__(self):
        self.google_client_id = config('GOOGLE_CLIENT_ID', default='')
        self.google_client_secret = config('GOOGLE_CLIENT_SECRET', default='')
        self.facebook_client_id = config('FACEBOOK_CLIENT_ID', default='')
        self.facebook_client_secret = config('FACEBOOK_CLIENT_SECRET', default='')
        self.oauth_redirect_url = config('OAUTH_REDIRECT_URL', default='http://localhost:3000/auth/callback')
        
        # Initialize OAuth
        self.oauth = OAuth()
        
        # Configure Google OAuth
        if self.google_client_id and self.google_client_secret:
            self.oauth.register(
                name='google',
                client_id=self.google_client_id,
                client_secret=self.google_client_secret,
                server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
                client_kwargs={
                    'scope': 'openid email profile'
                }
            )
        
        # Configure Facebook OAuth
        if self.facebook_client_id and self.facebook_client_secret:
            self.oauth.register(
                name='facebook',
                client_id=self.facebook_client_id,
                client_secret=self.facebook_client_secret,
                access_token_url='https://graph.facebook.com/oauth/access_token',
                authorize_url='https://www.facebook.com/dialog/oauth',
                api_base_url='https://graph.facebook.com/',
                client_kwargs={'scope': 'email'},
            )
    
    @property
    def is_google_configured(self) -> bool:
        """Check if Google OAuth is configured."""
        return bool(self.google_client_id and self.google_client_secret)
    
    @property
    def is_facebook_configured(self) -> bool:
        """Check if Facebook OAuth is configured."""
        return bool(self.facebook_client_id and self.facebook_client_secret)


# Global OAuth configuration instance
oauth_config = OAuthConfig() 
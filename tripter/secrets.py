
### Twitter Keys ###

C_KEY = "" # Consumer Key (API Key)
C_SECRET = "" # Consumer Secret (API Secret)
A_TOKEN = "" # Access Token
A_TOKEN_SECRET = "" # Access Token Secret
# Current Access Level: Read, write, and direct messages
# Owner: 
# Owner ID: 

### IG Keys ###
IG_ID = "" # Client ID
IG_SECRET = "" # Client Secret
IG_A_TOKEN = "" # Access Token for self
IG_A_TOKEN_2 = "" # Access Token for all content sandbox user
IG_A_TOKEN_3 = "" # Access Token for public_content only sandbox user
# Client Status: Sandbox Mode
# Sandbox Users: 
# Redirect URL : 


# Get Access Token:
# https://api.instagram.com/oauth/authorize/?client_id=CLIENT-ID&redirect_uri=REDIRECT-URI&response_type=code
# Returns code in nav bar after redirect uri--> use code with curl command
# curl -F client_id=CLIENT_ID -F client_secret=CLIENT_SECRET -F grant_type=authorization_code -F redirect_uri=AUTHORIZATION_REDIRECT_URI -F code=CODE https://api.instagram.com/oauth/access_token
# Returns user object with access token

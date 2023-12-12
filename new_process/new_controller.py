from flask import Flask, redirect, request, session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


# Secret key for session management
app.secret_key = os.urandom(24)

@app.route('/login')
def login():
    cognito_url = f"https://{Config.COGNITO_DOMAIN}/login?response_type=code&client_id={Config.COGNITO_APP_CLIENT_ID}&redirect_uri={Config.REDIRECT_URI}"
    return redirect(cognito_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = f"https://{Config.COGNITO_DOMAIN}/oauth2/token"
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'client_id': Config.COGNITO_CLIENT_ID,
        'code': code,
        'redirect_uri': Config.COGNITO_CALLBACK_URL
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    tokens = response.json()

    # Store necessary token info in session
    session['access_token'] = tokens.get('access_token')
    # Redirect to a secure home page or dashboard
    return redirect('/dashboard')

app_asgi = app
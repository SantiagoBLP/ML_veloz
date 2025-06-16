# ml_api_flask_starter.py
# Minimal Flask + OAuth 2.0 starter for MercadoLibre API (Ready for Railway deploy)

from flask import Flask, redirect, request, session, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecret")

# Config: Replace with your registered app credentials
CLIENT_ID = os.environ.get("ML_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ML_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("ML_REDIRECT_URI")

ML_AUTH_URL = "https://auth.mercadolibre.com.ar/authorization"
ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
ML_USER_URL = "https://api.mercadolibre.com/users/me"
ML_ITEMS_URL = "https://api.mercadolibre.com/users/{user_id}/items/search"

@app.route("/")
def index():
    return redirect(f"{ML_AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization failed."

    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post(ML_TOKEN_URL, data=data)
    if response.status_code != 200:
        return f"Token error: {response.text}"

    token_info = response.json()
    session["access_token"] = token_info["access_token"]
    session["user_id"] = token_info["user_id"]
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    access_token = session.get("access_token")
    user_id = session.get("user_id")
    if not access_token:
        return redirect("/")

    headers = {"Authorization": f"Bearer {access_token}"}
    items_res = requests.get(ML_ITEMS_URL.format(user_id=user_id), headers=headers)
    if items_res.status_code != 200:
        return f"Failed to get items: {items_res.text}"

    items = items_res.json().get("results", [])
    return jsonify({"user_id": user_id, "items": items})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

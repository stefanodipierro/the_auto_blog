import requests

def get_long_lived_token(app_id, app_secret, short_lived_token):
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    response = requests.get("https://graph.facebook.com/v12.0/oauth/access_token", params=params)

    if response.status_code == 200:
        result = response.json()
        long_lived_token = result['access_token']
        return long_lived_token
    else:
        # Gestisci l'errore
        print(response.content)
        return None

def post_to_facebook_page(page_id, message, access_token):
    """
    Post a message to a Facebook page.
    
    page_id: The ID of the Facebook page.
    message: The message to post.
    access_token: The access token.
    """
    url = f"https://graph.facebook.com/{page_id}/feed"
    payload = {
        "message": message,
        "access_token": access_token
    }
    response = requests.post(url, params=payload)
    
    if response.status_code == 200:
        print("Successfully posted to Facebook page.")
    else:
        print(f"Failed to post to Facebook page. Status code: {response.status_code}, message: {response.text}")
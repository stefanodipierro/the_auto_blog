import requests
import random

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
    """print(message)
    # Richiedi a Facebook di fare lo scraping delle OG tags
    scrape_url = f"https://graph.facebook.com/v17.0/"
    scrape_params = {
        'scrape': True,
        'access_token': access_token,
        'id': message
    }
    scrape_response = requests.post(scrape_url, params=scrape_params)
    
    # Aspetta 10 secondi per dare a Facebook il tempo di completare lo scraping
    print(scrape_response.text)
    
    Post a message to a Facebook page.
    
    page_id: The ID of the Facebook page.
    message: The message to post.
    access_token: The access token.
    """
    list_of_phrases = [
        "Interesting read! Check it out!",
        "This caught my eye. What are your thoughts?",
        "Don't miss out on this!",
        "This is a must-read!",
        "Just stumbled upon this. Have a look!",
        "So intriguing! Give this a read.",
        "Here's something you might like!",
        "Can't believe what I'm reading! Have a look.",
        "You might find this interesting!",
        "This is worth sharing. Take a look!"
    ]
    url = f"https://graph.facebook.com/v17.0/{page_id}/feed"
    params = {
        "message": random.choice(list_of_phrases),
        "link": message,
        "access_token": access_token
    }
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        print("Successfully posted to Facebook page.")
    else:
        print(f"Failed to post to Facebook page. Status code: {response.status_code}, message: {response.text}")

def get_page_access_token(user_access_token, page_id):
    url = f"https://graph.facebook.com/{page_id}"
    params = {
        "fields": "access_token",
        "access_token": user_access_token
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("access_token")  # Restituisce il token di accesso alla pagina
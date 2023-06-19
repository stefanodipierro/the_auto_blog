# gpt4_service.py
import openai
from app import db
from app.main.models import Post
from flask import session, jsonify, current_app

def generate_titles(num_articles, topic):
    openai.api_key = current_app.config['OPENAI_API_KEY']

    prompt = f"Generate {num_articles} blog post titles about {topic}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the GPT-3.5 model
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that generates blog post titles."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    # The generated titles are in the 'choices' list in the response. We split them by newline character.
    titles = response['choices'][0]['message']['content'].split('\n')
    return titles

def create_post(title, description):
    post = Post()
    post.from_dict({'title': title, 'description': description})
    db.session.add(post)
    db.session.commit()
    response = jsonify({"message": "Post created successfully", "id": post.id})
    response.status_code = 201
    return response

def generate_article(title):
    openai.api_key = current_app.config['OPENAI_API_KEY']

    prompt = f"Write an article about {title}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the GPT-3.5 model
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes blog articles."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )

    # The generated article is in the 'choices' list in the response
    article = response['choices'][0]['message']['content']
    return article

def generate_and_save_articles():
    creator_data = session.get('creator_data')
    if creator_data:
        num_articles = creator_data['num_articles']
        topic = creator_data['topic']
        prompt = f"Create {num_articles} titles for articles of a blog on the topic {topic}"
        # Qui invii il prompt a GPT-3.5 e ottieni una lista di titoli
        titles = generate_titles(num_articles , topic)

        for title in titles:
            description = generate_article(title)
            create_post(title, description)

# gpt4_service.py
import openai
from app import db
from app.main.models import Post
from flask import session, jsonify, current_app, flash
from .sender import Sender
from .receiver import Receiver
import os


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

def create_post(title, description, image_path_list):
    post = Post()
    post.from_dict({'title': title, 'description': description, 'images': image_path_list})
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
def generate_images(title):
    openai.api_key = current_app.config['OPENAI_API_KEY']

    prompt = f"Generate image description for an article titled '{title}'"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the GPT-3.5 model
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates image descriptions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
        
    )

    # The generated image descriptions are in the 'choices' list in the response.
    image_descriptions = [choice['message']['content'] for choice in response['choices']]
    
    # Return only the first description
    return image_descriptions[0] if image_descriptions else None



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
            print('article generated')
            images_prompt = generate_images(title)
            print('image prompt generated')
            sender = Sender()
            sender.send(prompt=images_prompt)
            print('sent to mid api')
            receiver = Receiver(directory='app/static')
            try:
                url, filename = receiver.collecting_result(image_prompt= images_prompt)
                images_path_list = receiver.download_image(url, filename)
                print('images downloaded')
                print(images_path_list)

                create_post(title, description, images_path_list)
                print('post created')
            except Exception as e:
                flash(f"Error: {str(e)}")
                # You might want to break the loop here, or continue with the next iteration.
                # It depends on how you want your application to behave in case of error.

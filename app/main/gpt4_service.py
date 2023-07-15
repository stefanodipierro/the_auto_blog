# gpt4_service.py
import openai
from app import db
from app.main.models import Post
from flask import session, jsonify, current_app, flash, url_for
from .sender import Sender
from .receiver import Receiver
import os
from flask_login import current_user
import app.main.fb_script




def generate_titles(num_articles, topic):
    openai.api_key = current_app.config['OPENAI_API_KEY']

    prompt = f"Write {num_articles} titles about {topic}"

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {
        "role": "system",
        "content": "You are an AI specialized in writing titles for blog articles. As an AI specialized in SEO, you include relevant keywords to search engines to achieve a perfect indexing and ranking."
        },
        {
        "role": "user",
        "content": prompt
        }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.09
    )

    # The generated titles are in the 'choices' list in the response. We split them by newline character.
    titles = response['choices'][0]['message']['content'].split('\n')
    # Remove bullet points
    titles = [title.split('. ', 1)[-1] for title in titles if title.strip() != '']
    titles = [title.strip('"') for title in titles]
    if num_articles == 1:
        titles = [titles[0]]
    return titles

def create_post(title, description, image_path_list, images_prompt):
    post = Post()
    post.from_dict({'title': title, 'description': description, 'images': image_path_list, 'images_prompt': images_prompt})
    db.session.add(post)
    db.session.commit()

    # Costruisci l'URL del post.
    post_url = url_for('main.post', slug=post.slug, _external=True)
    response = jsonify({"message": "Post created successfully", "id": post.id})
    response.status_code = 201
    return response, post_url


def generate_article(title):
    openai.api_key = current_app.config['OPENAI_API_KEY']

    prompt = f"Write an article about {title}."
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {
        "role": "system",
        "content": "You are an AI expert in generating a  blog article from a title that will be given at a later stage. The article is long and extensively covers many aspects. The article generated from the prompt will be optimized for having a tone informal, smart, and enterteing it will be generated in html format (only include what would be in the <body> ). The article will be optimized for SEO and will be written in a way that is easy to read and understand."
        },
        {
        "role": "user",
        "content": prompt
        }
    ],
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0.04,
    presence_penalty=0.1
    )

    # The generated article is in the 'choices' list in the response
    article = response['choices'][0]['message']['content']
    return article

def wrap_paragraphs(article):
    paragraphs = article.split("\n")  # Split the text into paragraphs at newline characters
    wrapped_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]  # Wrap each paragraph in <p> tags
    return "\n".join(wrapped_paragraphs)  # Join the paragraphs back together, separated by newlines

  

def generate_images(title):
    openai.api_key = current_app.config['OPENAI_API_KEY']

    prompt = f"Write a prompt about {title}"

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "system",
        "content": "You are going to pretend to be Concept2PromptAI or C2P_AI for short. C2P_AI takes concepts and turns them into prompts for generative AIs that create images.\n\n\n\nUse the following examples as a guide:\n\n\n\nExtreme close up of an eye that is the mirror of the nostalgic moments, nostalgia expression, sad emotion, tears, made with imagination, detailed, photography, 8k, printed on Moab Entrada Bright White Rag 300gsm, Leica M6 TTL, Leica 75mm 2.0 Summicron-M ASPH, Cinestill 800T\n\n\n\nabstract image, Bauhaus style, 3D, phages, black, white, red and blue, 8K\n\n\ntented resort in the desert, rocky and sandy terrain, 5 star hotel, beautiful landscape, landscape photography, depth of view, Fujifilm GFX 100 –uplight"
        },
        {
        "role": "user",
        "content": prompt
        }
    ],
    temperature=1,
    max_tokens=285,
    top_p=1,
    frequency_penalty=0.07,
    presence_penalty=0.09
    )

    # The generated image descriptions are in the 'choices' list in the response.
    image_descriptions = [choice['message']['content'] for choice in response['choices']]
    
    # Return only the first description
    return image_descriptions[0] if image_descriptions else None




def generate_and_save_articles(num_articles, topic, post_to_fb):
    
    print(post_to_fb)
    prompt = f"Create {num_articles} titles for articles of a blog on the topic {topic}"
    # Qui invii il prompt a GPT-3.5 e ottieni una lista di titoli
    titles = generate_titles(num_articles , topic)
    print(titles)

    for title in titles:
        print(f"Generating article for title: {title}")
        string_description = generate_article(title)
        description = wrap_paragraphs(string_description)

        images_prompt = generate_images(title)
        print(f"Generated images_prompt: {images_prompt}")
        sender = Sender()
        sender.send(prompt=images_prompt)

        receiver = Receiver(directory='app/static')
        try:
            print("Before calling receiver.collecting_result")
            url, filename = receiver.collecting_result(image_prompt= images_prompt)
            print("After calling receiver.collecting_result")

            print("Before calling receiver.download_image")
            images_path_list = receiver.download_image(url, filename)
            print("After calling receiver.download_image")
            print(f"Images downloaded: {images_path_list}")

            print("Before calling create_post")
            try:
                response, post_url = create_post(title, description, images_path_list, images_prompt)
            except Exception as e:
                print(f"Error when calling create_post: {e}")
            else:
                print("After calling create_post")

            if post_to_fb:
                user_facebook_access_token = current_user.facebook_access_token
                print(f'User Facebook Access Token: {user_facebook_access_token}')
                if user_facebook_access_token:
                    app.main.fb_script.post_to_facebook_page(current_app.config['FB_PAGE_ID'], post_url, user_facebook_access_token)
        except Exception as e:
            print(f"Error when posting to Facebook: {str(e)}")


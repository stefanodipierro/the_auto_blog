import requests
import json
import time
from PIL import Image
import os
from datetime import datetime
import re
from flask import current_app



class Receiver:

    def __init__(self, 
                 params = 'app/main/sender_params.json', directory = None
                 ):
        
        self.params = params
        self.directory = directory
        print(f"self.directory: {self.directory}")  # aggiungi questa linea
        self.sender_initializer()

    def sender_initializer(self):

        with open(self.params, "r") as json_file:
            params = json.load(json_file)

        self.channelid=params['channelid']
        self.authorization= current_app.config['AUTHORIZATION']
        self.headers = {'authorization' : self.authorization}

    def normalize_prompt(self, prompt):
        return re.sub('\W+', '', prompt).lower()

    def retrieve_messages(self):
        r = requests.get(
            f'https://discord.com/api/v10/channels/{self.channelid}/messages?limit=1', headers=self.headers)
        jsonn = json.loads(r.text)
        return jsonn[0]

    def collecting_result(self, image_prompt):
        normalized_image_prompt = self.normalize_prompt(image_prompt)
        max_attempts = 10  # Set the maximum number of attempts
        attempt = 0  # Initialize the attempt counter
        

        while attempt < max_attempts:  # Keep looping until a suitable message is found or max_attempts is reached
            message  = self.retrieve_messages()
            

            prompt = None # Initialize prompt to None
            url = None # Initialize url to None
            filename = None # Initialize filename to None
            
            if (message['author']['username'] == 'Midjourney Bot') and ('**' in message['content']):
                

                if len(message['attachments']) > 0:
                    if (message['attachments'][0]['filename'][-4:] == '.png') or ('(Open on website for full quality)' in message['content']):

                        prompt = message['content'].split('**')[1].split(' --')[0]
                        normalized_prompt = self.normalize_prompt(prompt)

                        if normalized_prompt == normalized_image_prompt:
                            url = message['attachments'][0]['url']
                            filename = message['attachments'][0]['filename']
                            return url, filename # If a suitable message is found, return url and filename
            attempt += 1  # Increment the attempt counter        
            time.sleep(60) # If a suitable message isn't found, wait for 30 seconds before trying again
        raise Exception("Max attempts reached without finding a suitable message")  # Raise an error if max_attempts is reached

    def split_image(self, image_file):
        with Image.open(image_file) as im:
            # Get the width and height of the original image
            width, height = im.size
            # Calculate the middle points along the horizontal and vertical axes
            mid_x = width // 2
            mid_y = height // 2
            # Split the image into four equal parts
            top_left = im.crop((0, 0, mid_x, mid_y))
            top_right = im.crop((mid_x, 0, width, mid_y))
            bottom_left = im.crop((0, mid_y, mid_x, height))
            bottom_right = im.crop((mid_x, mid_y, width, height))

            return top_left, top_right, bottom_left, bottom_right
        
    def download_image(self, url, filename):
        file_paths = [] # Initialize an empty list to store the file paths
        response = requests.get(url)
        if response.status_code == 200:

            # Define the input and output folder paths
            input_folder = "input"
            output_folder = "output"

            # Check if the output folder exists, and create it if necessary
            if not os.path.exists(os.path.join(self.directory, output_folder)):
                os.makedirs(os.path.join(self.directory, output_folder))
            # Check if the input folder exists, and create it if necessary
            if not os.path.exists(os.path.join(self.directory, input_folder)):
                os.makedirs(os.path.join(self.directory, input_folder))

            with open(f"{self.directory}/{input_folder}/{filename}", "wb") as f:
                print(f"Trying to create file: {self.directory}/{input_folder}/{filename}")  # aggiungi questa linea

                f.write(response.content)
            print(f"Image downloaded: {filename}")

            input_file = os.path.join(self.directory,input_folder, filename)

            if "UPSCALED_" not in filename:
                file_prefix = os.path.splitext(filename)[0]
                # Split the image
                top_left, top_right, bottom_left, bottom_right = self.split_image(input_file)
                # Save the output images with dynamic names in the output folder
                top_left_filename = file_prefix + "_top_left.jpg"
                top_right_filename = file_prefix + "_top_right.jpg"
                bottom_left_filename = file_prefix + "_bottom_left.jpg"
                bottom_right_filename = file_prefix + "_bottom_right.jpg"

                top_left_path = os.path.join(self.directory, output_folder, top_left_filename)
                top_right_path = os.path.join(self.directory, output_folder, top_right_filename)
                bottom_left_path = os.path.join(self.directory, output_folder, bottom_left_filename)
                bottom_right_path = os.path.join(self.directory, output_folder, bottom_right_filename)

                top_left.save(top_left_path)
                top_right.save(top_right_path)
                bottom_left.save(bottom_left_path)
                bottom_right.save(bottom_right_path)

                file_paths.extend([top_left_filename, top_right_filename, bottom_left_filename, bottom_right_filename])

            else:
                os.rename(f"{self.directory}/{input_folder}/{filename}", f"{self.directory}/{output_folder}/{filename}")
            # Delete the input file
            os.remove(f"{self.directory}/{input_folder}/{filename}")

        return file_paths

if __name__ == '__main__':
    receiver = Receiver()
    url, filename = receiver.collecting_result(image_prompt= 'black car')
    print("URL:", url)
    print("Filename:", filename)
    images_path_list = receiver.download_image(url, filename)
    print(images_path_list)


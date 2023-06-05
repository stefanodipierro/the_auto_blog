# Import necessary modules
import unittest
from app import create_app, db
from app.main.models import Post, Image
from datetime import datetime


class BlogTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Load the test data fixtures.
        self.create_test_posts()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_posts(self):
        for i in range(5):
            post = Post(title=f'Test Post {i}', description=f'This is test post {i}.', date = datetime.now())
            db.session.add(post)
            db.session.flush()  # Flush the session to get the generated post id
            

            # Create test images for this post.
            for j in range(3):
                image = Image(post_id=post.id, image_url=f'https://static.wikia.nocookie.net/simpsons/images/a/af/Plopper_Tapped_Out.png/revision/latest?cb=20150927000049-{i}-{j}.jpg')
                db.session.add(image)

        db.session.commit()

    def test_home_page(self):
        # Test that the home page loads correctly
        tester = self.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_post_loading(self):
        # Test that posts are loaded correctly
        tester = self.app.test_client(self)
        
        response = tester.get('/', content_type='html/text')
        self.assertIn(b'Test Post', response.data)

    def test_non_existent_post(self):
        # Test that a non-existent post returns a 404 error
        tester = self.app.test_client(self)
        response = tester.get('/post/1000', content_type='html/text')
        self.assertEqual(response.status_code, 404)



class TestPostAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')  # Initialize the Flask application

        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite for testing
        self.app.config['TESTING'] = True

        self.app_context = self.app.app_context()
        self.app_context.push()

        self.client = self.app.test_client()

        db.create_all()
        # Register a new user and login
        self.register_and_login()

    def tearDown(self):
        db.session.commit()  # Commit any changes before closing the session
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_and_login(self):
        # Register a new user
        register_response = self.client.post(
            '/register',
            json={
                'username': 'testuser',
                'email': 'test@email.com',
                'password': 'testpassword'
            }
        )

        # Log in as the new user
        login_response = self.client.post(
            '/login',
            json={
                'username': 'testuser',
                'password': 'testpassword'
            }
        )
        print("login_response.json")
        print(login_response.json)

        # Store the access token from the login response
        self.access_token = login_response.json['token']
        print("self.access_token")
        print(self.access_token)
        

    def test_create_post(self):
        # Prepare data for a new post
        new_post = {
            'title': 'Test Post',
            'description': 'This is a test post',            
            'images': ['http://example.com/image.jpg','http://example.com/image.jpg','http://example.com/image.jpg']
        }

        # Send POST request to the /api/posts endpoint
        response = self.client.post('/api/posts', json=new_post, headers={
        'Authorization': f'Bearer {self.access_token}'
        })
        print("response")
        print(response)

        # Check status code and response data
        self.assertEqual(response.status_code, 201)
        json_data = response.get_json()
        self.assertEqual(json_data['message'], 'Post created successfully')
        self.assertTrue('id' in json_data)

        # Check if the post is actually saved in the database
        post = Post.query.get(json_data['id'])
        self.assertIsNotNone(post)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.description, 'This is a test post')

        self.assertEqual([img.image_url for img in post.images], new_post['images'])

    def test_delete_post(self):
    # Create a test post
        post = Post(title='Test Post', description='This is a test post')
        db.session.add(post)
        db.session.commit()

        # Send DELETE request to the /api/posts/<post_id> endpoint
        response = self.client.delete(f'/api/posts/{post.id}', headers={'Authorization': f'Bearer {self.access_token}'})

        # Check status code and response data
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['message'], 'Post deleted successfully')

        # Verify that the post was deleted
        post = Post.query.get(post.id)
        self.assertIsNone(post)


if __name__ == '__main__':
    unittest.main()


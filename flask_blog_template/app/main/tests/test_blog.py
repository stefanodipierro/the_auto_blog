# Import necessary modules
import unittest
from app import create_app, db
from app.main.models import Post, Image

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
            post = Post(title=f'Test Post {i}', description=f'This is test post {i}.')
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

if __name__ == '__main__':
    unittest.main()


import unittest
from app import create_app, db
from app.main.models import User
from flask import session


#set up

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client(use_cookies=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(username="TestUser")
        self.user.set_password("TestPassword")
        db.session.add(self.user)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
#login and logout

    def test_login_logout(self):
        # Login
        response = self.client.post(
            '/login', 
            data={'username': 'TestUser', 'password': 'TestPassword'},
            follow_redirects=True
        )
        # Verifica che la richiesta sia andata a buon fine
        self.assertEqual(response.status_code, 200)
        # Verifica che sei stato reindirizzato alla pagina 'creator'
        self.assertTrue(b'Welcome' in response.data)

        print(response.data)  # This will print the response data

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        # Verifica che la richiesta sia andata a buon fine
        self.assertEqual(response.status_code, 200)
        # Verifica che sei stato reindirizzato alla pagina 'home'
        self.assertTrue(b'Home' in response.data)  # sostituisci con il contenuto della tua pagina home
            

    def test_creator_route(self):
        # Login first, because '/creator' might be a protected route
        self.client.post(
            '/login', 
            data={'username': 'TestUser', 'password': 'TestPassword'},
            follow_redirects=True
        )

        # Submit a POST request to '/creator' with valid form data
        response = self.client.post(
            '/creator',
            data={'num_articles': 5, 'topic': 'Flask'},
            follow_redirects=True
        )
        

        # Verify that the request was successful
        self.assertEqual(response.status_code, 200)

        # Verify that 'session' contains the data you expect
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['creator_data'], {'num_articles': 5, 'topic': 'Flask'})

if __name__ == '__main__':
    unittest.main()

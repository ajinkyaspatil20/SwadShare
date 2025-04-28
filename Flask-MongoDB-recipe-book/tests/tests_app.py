from app import app
import unittest
from dotenv import load_dotenv
import os
import json


class AppTestCase(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.tester = app.test_client(self)
        self.test_example_author_recipe_id = '5cd36d89162429d92fb1465b'
        self.test_example_other_recipe_id = '5ccf2d60ceda74b3755a11c9'

    def authenticate(self):
        valid_credits = {
            'username': os.getenv('TEST_USERNAME'),
            'password': os.getenv('TEST_PASSWORD')
        }
        return self.tester.post('/login', data=valid_credits, follow_redirects=True)

    def test_success_login(self):
        valid_login = self.authenticate()
        self.assertIn(b'Successfully logged in', valid_login.data)
        self.assertIn(b'Your  most recent recipes', valid_login.data)

    def test_failed_login(self):
        response = self.tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        invalid_credits = {
            'username': 'test_user',
            'password': 'test'
        }
        response = self.tester.post('/login', data=invalid_credits, follow_redirects=True)
        self.assertIn(b'Wrong username or password', response.data)

    def test_register_login_taken(self):
        form_data = {
            'username': os.getenv('TEST_USERNAME'),
            'password': 'test_password',
            'confirm': 'test_password'
        }
        response = self.tester.post('/register', data=form_data, follow_redirects=True)
        self.assertIn(b'is already registered', response.data)

    def test_api_vote_not_logged(self):
        response = self.tester.get('/api/recipe-vote', content_type='html/text')
        self.assertIn(b'method is not allowed', response.data)

        json_response = self.tester.post('/api/recipe-vote', content_type='application/json')
        self.assertIn('application/json', json_response.content_type)
        data = json.loads(json_response.get_data(as_text=True))
        should_response = {
            'status': 'error',
            'message': 'You need to login to vote for the recipe'
        }
        self.assertDictEqual(data, should_response)

    def test_api_vote_on_own_recipe(self):
        # this should return not valid vote author can't vote for own recipes
        self.authenticate()
        json_response = self.tester.post('/api/recipe-vote', data=dict(id=self.test_example_author_recipe_id),
                                         content_type='application/x-www-form-urlencoded')
        data = json.loads(json_response.get_data(as_text=True))
        self.assertEqual(data['message'], 'An error occurred. Please try again')

    def test_api_vote_valid(self):
        # valid vote
        self.authenticate()
        json_response = self.tester.post('/api/recipe-vote', data=dict(id=self.test_example_other_recipe_id),
                                         content_type='application/x-www-form-urlencoded')
        data = json.loads(json_response.get_data(as_text=True))
        self.assertTrue('votes' in data)
        self.assertGreaterEqual(data['votes'], 0)

    def test_index(self):
        response = self.tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_add_recipe_no_logged(self):
        should_redirect = self.tester.get('/recipe/add')
        self.assertEqual(should_redirect.status_code, 302)

    def test_add_recipe_empty_form(self):
        self.authenticate()
        response = self.tester.post('/recipe/add', data={}, follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)
        self.assertIn(b'Method is required you should add at least one method', response.data)
        self.assertIn(b'Ingredients are required you should add at least one ingredient', response.data)

    def test_delete_recipe_not_logged(self):
        response = self.tester.get('/recipe/delete/'+self.test_example_other_recipe_id, follow_redirects=True)
        self.assertIn(b'You need to login to continue', response.data)

    def test_delete_recipe_not_owned(self):
        self.authenticate()
        response = self.tester.get('/recipe/delete/'+self.test_example_other_recipe_id, follow_redirects=True)
        self.assertIn(b'You can&#39;t delete someone recipe', response.data)

    def test_edit_recipe_not_logged(self):
        response = self.tester.get('/recipe/edit/'+self.test_example_other_recipe_id, follow_redirects=True)
        self.assertIn(b'You need to login to continue', response.data)

    def test_edit_recipe_not_owned(self):
        self.authenticate()
        response = self.tester.get('/recipe/edit/'+self.test_example_other_recipe_id)
        self.assertIn(b'You can&#39;t edit someone recipe', response.data)


if __name__ == '__main__':
    unittest.main()

import unittest
from forms import RegistrationForm, LoginForm, RecipeForm
from werkzeug.datastructures import MultiDict


class FormsTestCase(unittest.TestCase):

    def test_fail_login(self):
        # fail
        data = []
        form = LoginForm(MultiDict(data))
        should_return = {
            'username': ['This field is required.'],
            'password': ['This field is required.']
        }
        self.assertFalse(form.validate())
        self.assertDictEqual(form.errors, should_return)

    def test_success_login(self):
        # success
        data = [
            ('username', 'test'),
            ('password', 'test')
        ]
        form = LoginForm(MultiDict(data))
        self.assertTrue(form.validate())
        self.assertEqual(form.errors, {})

    def test_registration(self):
        data = [
            ('username', 'me'),
            ('password', 'test_password'),
            ('confirm', 'test_confirm'),
        ]
        form = RegistrationForm(MultiDict(data))
        self.assertFalse(form.validate())
        self.assertListEqual(form.errors['username'],
                             ['Field must be between 4 and 25 characters long.'])
        self.assertListEqual(form.errors['password'], ['Passwords must match'])

    def test_recipe(self):
        data = [
            ('title', 'Test recipe'),
            ('introduction', None),
            ('method-0', 'Method'),
            ('ingredients-0', 'Ingredient'),
            ('categories-0', None),
            ('cuisines-0', None),
            ('allegrens-0', None)
        ]
        form = RecipeForm(MultiDict(data))
        self.assertTrue(form.validate())
        self.assertEqual(form.title.data, 'Test recipe')


if __name__ == '__main__':
    unittest.main()

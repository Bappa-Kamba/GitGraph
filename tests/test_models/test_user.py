import unittest
from app import app
from models.user import User


class TestUserCrudOperations(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        # Initialize app context here
        with app.app_context():
            self.test_user_data = {
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'test_password'
            }
        # Create a test user for update and delete tests
        User.create(**self.test_user_data)

    def tearDown(self):
        self.users_collection.delete_many({}) # Clean up after each test

    def test_create_user(self):
        response = self.app.post('/api/users', json=self.test_user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.users_collection.count_documents(
            {'username': 'test_user'}), 2)

    def test_get_user_by_username(self):
        response = self.app.get('/api/users?username=test_user')
        self.assertEqual(response.status_code, 200)
        # Check if a user exist
        self.assertEqual(len(response.json), 1)

    def test_update_user(self):
        updated_data = {'email': 'updated@example.com'}
        response = self.app.put('/api/users/test_user', json=updated_data)
        self.assertEqual(response.status_code, 200)
        updated_user = self.users_collection.find_one(
            {'username': 'test_user'})
        self.assertEqual(updated_user['email'], 'updated@example.com')

    def test_delete_user(self):
        response = self.app.delete('/api/users/test_user')
        # 204 No Content for successful delete
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.users_collection.count_documents(
            {'username': 'test_user'}), 0)


if __name__ == '__main__':
    unittest.main()

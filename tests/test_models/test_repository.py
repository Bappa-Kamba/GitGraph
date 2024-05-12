# tests/test_models/test_repository.py
import unittest
from app import app
from models.repository import Repository
from models.database import get_repositories_collection


class TestRepositoryCrudOperations(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

        # Define test repository data
        self.test_repo_data = {
            'name': 'test_repo',
            'owner': 'test_owner',
            'description': 'A test repository',
            'url': 'https://github.com/test_owner/test_repo'
        }

        with app.app_context():
            self.repositories = get_repositories_collection()
            # Create a test repository for update and delete tests within the app context
            Repository.create(**self.test_repo_data)

    def tearDown(self):
        # Clean up within the application context
        with app.app_context():
            self.repositories.delete_many({})

    def test_create_repository(self):
        response = self.app.post(
            '/api/repositories/', json=self.test_repo_data)  # add trailing slash
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.repositories.count_documents(
            {'name': 'test_repo'}), 2)  # Check if 2 repositories exist with the same name

    def test_get_repository_by_name(self):
        response = self.app.get(
            '/api/repositories/?name=test_repo')  # add trailing slash
        self.assertEqual(response.status_code, 200)
        # Check if 2 repositories exist with the same name
        self.assertEqual(len(response.json), 1)

    def test_update_repository(self):
        updated_data = {'description': 'An updated test repository'}
        response = self.app.put(
            f'/api/repositories/{self.test_repo_data["name"]}', json=updated_data)  # add trailing slash
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            updated_repo = self.repositories.find_one(
                {'name': 'test_repo'})
        self.assertEqual(updated_repo['description'],
                         'An updated test repository')

    def test_delete_repository(self):
        response = self.app.delete(
            f"/api/repositories/{self.test_repo_data['name']}")  # add trailing slash
        # 204 No Content for success
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.repositories.count_documents(
            {'name': 'test_repo'}), 0
        )


if __name__ == '__main__':
    unittest.main()

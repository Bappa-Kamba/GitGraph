# tests/test_models/test_repository.py

import unittest
from app import app, db  # Import your Flask app and db instance
from models.repository import Repository


class TestRepositoryCrudOperations(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.repositories_collection = db.get_collection('repositories')
        self.test_repo_data = {
            'name': 'test_repo',
            'owner': 'test_owner',
            'description': 'A test repository',
            'url': 'https://github.com/test_owner/test_repo'
        }

        # Create a test repository for update and delete tests
        self.test_repo = Repository.create(**self.test_repo_data)

    def tearDown(self):
        self.repositories_collection.delete_many({})  # Clean up

    def test_create_repository(self):
        response = self.app.post(
            '/api/repositories', json=self.test_repo.to_dict())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.repositories_collection.count_documents(
            {'name': 'test_repo'}), 2)

    def test_get_repository_by_name(self):
        response = self.app.get('/api/repositories?name=test_repo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_update_repository(self):
        updated_data = {'description': 'An updated test repository'}
        response = self.app.put(
            f'/api/repositories/{self.test_repo.name}', json=updated_data)
        self.assertEqual(response.status_code, 200)
        updated_repo = self.repositories_collection.find_one(
            {'name': 'test_repo'})
        self.assertEqual(updated_repo['description'],
                         'An updated test repository')

    def test_delete_repository(self):
        # Use the repository object to delete
        response = self.app.delete(f"/api/repositories/{self.test_repo.name}")
        # 204 No Content for success
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.repositories_collection.count_documents(
            {'name': 'test_repo'}), 0)


if __name__ == '__main__':
    unittest.main()

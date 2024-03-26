import unittest
import os
from unittest.mock import patch
from io import StringIO
from models.base_model import BaseModel
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review
from models.engine.file_storage import FileStorage
from db_storage import DBStorage


class TestFileStorage(unittest.TestCase):
    def setUp(self):
        self.storage = FileStorage()

    def test_all_returns_dict(self):
        self.assertIsInstance(self.storage.all(), dict)

    @patch('sys.stdout', new_callable=StringIO)
    def test_reload_no_file(self, mock_stdout):
        with patch('builtins.open', side_effect=FileNotFoundError):
            self.storage.reload()
            self.assertEqual(mock_stdout.getvalue(), "")

    def tearDown(self):
        # Clean up any files created during tests
        if os.path.exists(FileStorage._FileStorage__file_path):
            os.remove(FileStorage._FileStorage__file_path)

    def test_all_returns_empty_dict_initially(self):
        self.assertEqual(self.storage.all(), {})

    def test_new_adds_object_to_storage(self):
        obj = BaseModel()
        self.storage.new(obj)
        self.assertIn('BaseModel.' + obj.id, self.storage.all())

    def test_save_writes_to_file(self):
        obj = BaseModel()
        self.storage.new(obj)
        self.storage.save()
        with open(FileStorage._FileStorage__file_path, 'r') as f:
            data = f.read()
            self.assertIn('BaseModel.' + obj.id, data)

    def test_reload_loads_objects_from_file(self):
        obj = BaseModel()
        obj.save()
        new_storage = FileStorage()
        new_storage.reload()
        self.assertIn('BaseModel.' + obj.id, new_storage.all())

    @patch('sys.stdout', new_callable=StringIO)
    def test_reload_no_file(self, mock_stdout):
        with patch('builtins.open', side_effect=FileNotFoundError):
            self.storage.reload()
            self.assertEqual(mock_stdout.getvalue(), "")

    def reload(self):
        """Loads storage dictionary from file"""
        self.__objects = {}  # Clear the storage before loading data
        from models.base_model import BaseModel
        # Load data from file and populate the storage dictionary
        try:
            with open(FileStorage.__file_path, 'r') as f:
                temp = json.load(f)
                for key, val in temp.items():
                    self.all()[key] = BaseModel(**val)
        except FileNotFoundError:
            pass


class TestDBStorage(unittest.TestCase):
    def setUp(self):
        self.storage = DBStorage()
        self.storage.reload()

    def tearDown(self):
        self.storage.close()

    @patch('sys.stdout', new_callable=StringIO)
    def test_all_returns_dict(self, mock_stdout):
        all_data = self.storage.all()
        self.assertIsInstance(all_data, dict)

    @patch('sys.stdout', new_callable=StringIO)
    def test_new_adds_object_to_session(self, mock_stdout):
        user = User(email="test@test.com", password="password")
        self.storage.new(user)
        self.assertIn(user, self.storage._DBStorage__session.new)

    @patch('sys.stdout', new_callable=StringIO)
    def test_save_commits_changes(self, mock_stdout):
        user = User(email="test@test.com", password="password")
        self.storage.new(user)
        self.storage.save()
        self.assertIn(user, self.storage._DBStorage__session)

    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_removes_object_from_session(self, mock_stdout):
        user = User(email="test@test.com", password="password")
        self.storage.new(user)
        self.storage.delete(user)
        self.assertNotIn(user, self.storage._DBStorage__session)

    @patch('sys.stdout', new_callable=StringIO)
    def test_reload_creates_tables_and_session(self, mock_stdout):
        self.storage.reload()
        engine = self.storage._DBStorage__engine
        tables = engine.table_names()
        self.assertIn('users', tables)
        self.assertIn('states', tables)
        self.assertIsInstance(
            self.storage._DBStorage__session,
            sqlalchemy.orm.Session
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_close_closes_session(self, mock_stdout):
        self.storage.close()
        self.assertIsNone(self.storage._DBStorage__session)


if __name__ == '__main__':
    unittest.main()

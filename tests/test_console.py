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

    def test_reload_empty_file(self):
        with open(FileStorage._FileStorage__file_path, 'w') as f:
            # Write valid JSON data to the file
            f.write('{}')
        self.storage.reload()
        self.assertEqual(self.storage.all(), {})


if __name__ == '__main__':
    unittest.main()

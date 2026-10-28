import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import db, main
from app.models import ProjectCreate


class UploadStub:
    filename = "notes.txt"
    content_type = "text/plain"

    def __init__(self, content):
        self.content = content
        self.read_limit = None

    async def read(self, size=-1):
        self.read_limit = size
        return self.content[:size]


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DB_PATH
        db.DB_PATH = Path(self.tempdir.name) / "onoma.db"
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.tempdir.cleanup()

    def test_create_and_list_project(self):
        created = main.create_project(ProjectCreate(name="Test project"))

        self.assertEqual(main.list_projects()[0]["id"], created["id"])
        self.assertEqual(created["name"], "Test project")

    def test_oversized_upload_is_read_only_to_the_size_limit(self):
        upload = UploadStub(b"x" * 5_000_002)

        with self.assertRaises(HTTPException) as error:
            asyncio.run(main.upload_document(upload))

        self.assertEqual(error.exception.status_code, 413)
        self.assertEqual(upload.read_limit, 5_000_001)


if __name__ == "__main__":
    unittest.main()

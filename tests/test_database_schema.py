import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = (ROOT / "database" / "schema.sql").read_text()
PRISMA = (ROOT / "prisma" / "schema.prisma").read_text()


class DatabaseSchemaTests(unittest.TestCase):
    def test_prisma_models_map_to_every_sql_table(self):
        sql_tables = set(re.findall(r"CREATE TABLE\s+(\w+)", SCHEMA, re.IGNORECASE))
        models = re.findall(r"^model\s+\w+\s*\{(.*?)^\}", PRISMA, re.MULTILINE | re.DOTALL)
        prisma_tables = {
            table
            for model in models
            for table in re.findall(r'@@map\("([^"]+)"\)', model)
        }

        self.assertEqual(sql_tables, prisma_tables)

    def test_vector_fields_and_extensions_are_declared(self):
        self.assertIn("CREATE EXTENSION IF NOT EXISTS vector", SCHEMA)
        self.assertEqual(SCHEMA.count("vector(1536)"), 2)
        self.assertEqual(PRISMA.count('Unsupported("vector(1536)")'), 2)
        self.assertIn("extensions = [vector]", PRISMA)

    def test_initial_migration_applies_canonical_schema(self):
        migration = (ROOT / "database" / "migrations" / "001_initial.sql").read_text()
        self.assertIn(r"\set ON_ERROR_STOP on", migration)
        self.assertIn(r"\ir ../schema.sql", migration)


if __name__ == "__main__":
    unittest.main()

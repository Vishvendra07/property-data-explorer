import unittest
from project import database, query, render


class ExplorerTests(unittest.TestCase):
    def test_combined_filters_and_plan(self):
        with database() as db:
            result = query(db, "West", 260000, 3)
        self.assertEqual([row["name"] for row in result["records"]], ["Birch Court"])
        self.assertIn("SEQ_SCAN", result["explain"])

    def test_html_does_not_close_script_for_input_data(self):
        self.assertNotIn("</script><script>alert", render([{"name": "</script><script>alert(1)"}]))

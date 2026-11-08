import unittest
from io import StringIO
from contextlib import redirect_stdout

from report_writer import (
    write_frequency,
    print_fea,
)


class TestReportWriter(unittest.TestCase):

    def test_write_frequency(self):
        output = StringIO()

        data = {
            "count": 5,
            "unique": 3,
            "frequency": [
                ("A", 3),
                ("B", 1),
                ("C", 1),
            ],
        }

        write_frequency(output, "TEST", data, minimum=2)

        result = output.getvalue()

        self.assertIn("Count  : 5", result)
        self.assertIn("Unique : 3", result)
        self.assertIn("A 3", result)
        self.assertNotIn("B 1", result)

    def test_write_frequency_empty(self):
        output = StringIO()

        data = {
            "count": 0,
            "unique": 0,
            "frequency": [],
        }

        write_frequency(output, "EMPTY", data)

        self.assertIn("No results.", output.getvalue())

    def test_print_fea(self):
        output = StringIO()

        with redirect_stdout(output):
            print_fea(
                [],
                ["sub K A' T by A.ss01;"],
                [],
            )

        result = output.getvalue()

        self.assertIn("languagesystem DFLT dflt;", result)
        self.assertIn("feature calt {", result)
        self.assertIn("\tsub K A' T by A.ss01;", result)
        self.assertIn("} calt;", result)


if __name__ == "__main__":
    unittest.main()
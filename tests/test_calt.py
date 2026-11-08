import unittest

from calt import (
    generate_calt_rules,
    generate_triple_letter_trigram_rules,
)


class TestCalt(unittest.TestCase):

    def test_generate_calt_rules(self):
        calt = {
            "context": {
                "A": {
                    "total": 10,
                    "variants": [
                        [("CAT", 6)],
                        [("BAT", 4)],
                    ],
                }
            }
        }

        result = generate_calt_rules(calt)

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]["context"], "CAT")
        self.assertEqual(result[0]["letter"], "A")
        self.assertEqual(result[0]["variant"], 1)
        self.assertEqual(result[0]["weight"], 0.6)

        self.assertEqual(result[1]["context"], "BAT")
        self.assertEqual(result[1]["variant"], 2)
        self.assertEqual(result[1]["weight"], 0.4)

    def test_generate_triple_letter_rules(self):
        data = {
            "frequency": [
                ("FFF", 5),
            ]
        }

        result = generate_triple_letter_trigram_rules(data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "triple_letter")
        self.assertEqual(result[0]["context"], "FFF")
        self.assertEqual(
            result[0]["variants"],
            ["F", "F.ss01", "F.ss02"],
        )


if __name__ == "__main__":
    unittest.main()
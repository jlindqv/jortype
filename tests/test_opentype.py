import unittest

from opentype import (
    glyph_name,
    generate_opentype_subrules,
    generate_opentype_triple_letter_rules,
)


class TestOpenType(unittest.TestCase):

    def test_glyph_name(self):
        self.assertEqual(glyph_name("F", 0), "F")
        self.assertEqual(glyph_name("F", 1), "F.ss01")
        self.assertEqual(glyph_name("F", 2), "F.ss02")

    def test_swedish_glyph_names(self):
        self.assertEqual(glyph_name("Å", 0), "Aring")
        self.assertEqual(glyph_name("Ä", 1), "Adieresis.ss01")
        self.assertEqual(glyph_name("Ö", 2), "Odieresis.ss02")

    def test_generate_opentype_subrules(self):
        rules = [
            {
                "letter": "A",
                "variant": 1,
                "before": "K",
                "after": "T",
            }
        ]

        result = generate_opentype_subrules(rules)

        self.assertEqual(
            result,
            ["sub K A' T by A.ss01;"],
        )

    def test_generate_triple_letter_rules(self):
        rules = [
            {
                "context": "FFF",
                "variants": ["F", "F.ss01", "F.ss02"],
            }
        ]

        lookups, chains = generate_opentype_triple_letter_rules(
            rules
        )

        self.assertEqual(len(lookups), 2)

        self.assertIn(
            "lookup Triple_F_to_F_ss01",
            lookups[0],
        )

        self.assertIn(
            "lookup Triple_F_to_F_ss02",
            lookups[1],
        )

        self.assertEqual(
            chains,
            [
                "sub F F' lookup Triple_F_to_F_ss01 "
                "F' lookup Triple_F_to_F_ss02;"
            ],
        )

    def test_duplicate_triple_contexts_are_ignored(self):
        rules = [
            {
                "context": "FFF",
                "variants": ["F", "F.ss01", "F.ss02"],
            },
            {
                "context": "FFF",
                "variants": ["F", "F.ss01", "F.ss02"],
            },
        ]

        lookups, chains = generate_opentype_triple_letter_rules(
            rules
        )

        self.assertEqual(len(chains), 1)

    def test_invalid_variant_count_raises_error(self):
        rules = [
            {
                "context": "FFF",
                "variants": ["F", "F.ss01"],
            }
        ]

        with self.assertRaises(ValueError):
            generate_opentype_triple_letter_rules(rules)


if __name__ == "__main__":
    unittest.main()
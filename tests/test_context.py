import unittest
from collections import Counter
from unittest.mock import patch

from context import (
    build_contexts,
    analyze_letter_context,
    distribute_contexts,
    generate_context_rules,
    calculate_weight,
)


class TestContext(unittest.TestCase):

    def test_build_contexts(self):
        result = build_contexts([
            ("CAT", 2),
            ("BAT", 3),
            ("CAR", 1),
        ])

        self.assertEqual(
            result["A"]["before"],
            Counter({"B": 3, "C": 3}),
        )

        self.assertEqual(
            result["A"]["after"],
            Counter({"T": 5, "R": 1}),
        )

        self.assertEqual(
            result["A"]["trigrams"],
            Counter({"BAT": 3, "CAT": 2, "CAR": 1}),
        )

    def test_analyze_letter_context(self):
        result = analyze_letter_context("CAT BAT")

        self.assertEqual(
            result["A"]["before"],
            Counter({"C": 1, "B": 1}),
        )

    def test_distribute_contexts(self):
        result = distribute_contexts([
            ("A", 5),
            ("B", 4),
            ("C", 3),
            ("D", 2),
        ], variants=2)

        self.assertEqual(
            result,
            [
                [("A", 5), ("D", 2)],
                [("B", 4), ("C", 3)],
            ],
        )

    def test_generate_context_rules(self):
        contexts = {
            "A": {
                "trigrams": Counter({
                    "CAT": 6,
                    "BAT": 3,
                    "RAT": 1,
                })
            }
        }

        with patch("context.MIN_FREQUENCY", 1), \
             patch("context.CONTEXT_COVERAGE", 0.75):

            result = generate_context_rules(contexts)

        self.assertEqual(result["A"]["total"], 10)
        self.assertEqual(result["A"]["covered"], 9)
        self.assertEqual(result["A"]["coverage"], 0.9)
        self.assertEqual(
            result["A"]["contexts"],
            [("CAT", 6), ("BAT", 3)],
        )

    def test_calculate_weight(self):
        self.assertEqual(calculate_weight(25, 100), 0.25)

    def test_calculate_weight_with_zero_total(self):
        self.assertEqual(calculate_weight(0, 0), 0)


if __name__ == "__main__":
    unittest.main()
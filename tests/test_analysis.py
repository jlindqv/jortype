import unittest
import tempfile
import os

from analysis import (
    read_text,
    count_frequency,
    analyze_letters,
    analyze_words,
    get_grams,
    separate_trigrams,
    analyze_bigrams,
    analyze_trigrams,
    analyze_double_letters,
    analyze_repeating_letters,
    analyze_punctuation,
)


class TestAnalysis(unittest.TestCase):

    def test_count_frequency(self):
        result = count_frequency(["B", "A", "B", "A", "C"])

        self.assertEqual(result["count"], 5)
        self.assertEqual(result["unique"], 3)
        self.assertEqual(
            result["frequency"],
            [("A", 2), ("B", 2), ("C", 1)],
        )

    def test_analyze_letters(self):
        result = analyze_letters("KATT")

        self.assertEqual(result["count"], 4)
        self.assertEqual(result["unique"], 3)
        self.assertEqual(
            result["frequency"],
            [("T", 2), ("A", 1), ("K", 1)],
        )

    def test_analyze_words(self):
        result = analyze_words("KATT HUND KATT")

        self.assertEqual(result["count"], 3)
        self.assertEqual(
            result["frequency"],
            [("KATT", 2), ("HUND", 1)],
        )

    def test_get_grams(self):
        self.assertEqual(
            get_grams("KATT HUND", 2),
            ["KA", "AT", "TT", "HU", "UN", "ND"],
        )

    def test_get_grams_does_not_cross_word_boundaries(self):
        self.assertEqual(
            get_grams("KAT HUND", 3),
            ["KAT", "HUN", "UND"],
        )

    def test_separate_trigrams(self):
        result = separate_trigrams(["FFF", "ELL", "KAT"])

        self.assertEqual(result[0], ["FFF"])
        self.assertEqual(result[1], ["ELL"])
        self.assertEqual(result[2], ["KAT"])

    def test_analyze_bigrams(self):
        result = analyze_bigrams("KATT")

        self.assertEqual(
            result["frequency"],
            [("AT", 1), ("KA", 1), ("TT", 1)],
        )

    def test_analyze_trigrams(self):
        total, triple, double, ordinary = analyze_trigrams(
            "KATT FFF"
        )

        self.assertEqual(total["count"], 3)
        self.assertEqual(triple["frequency"], [("FFF", 1)])
        self.assertEqual(double["frequency"], [("ATT", 1)])
        self.assertEqual(ordinary["frequency"], [("KAT", 1)])

    def test_analyze_double_letters(self):
        result = analyze_double_letters("KATT 100")

        self.assertEqual(
            result["frequency"],
            [("00", 1), ("TT", 1)],
        )

    def test_analyze_repeating_letters(self):
        result = analyze_repeating_letters("KAAAA TTT 0000")

        self.assertEqual(
            result["frequency"],
            [("0000", 1), ("AAAA", 1), ("TTT", 1)],
        )

    def test_analyze_punctuation(self):
        result = analyze_punctuation("HEJ!!! VAD?!")

        self.assertEqual(
            result["frequency"],
            [("!!!", 1), ("?!", 1)],
        )

    def test_empty_input(self):
        result = analyze_letters("")

        self.assertEqual(result["count"], 0)
        self.assertEqual(result["unique"], 0)
        self.assertEqual(result["frequency"], [])

    def test_read_text(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
        ) as file:
            file.write("Katt åäö")
            filename = file.name

        try:
            self.assertEqual(read_text(filename), "KATT ÅÄÖ")
        finally:
            os.remove(filename)


if __name__ == "__main__":
    unittest.main()
from collections import Counter
import re
from config import MIN_FREQUENCY


WORD_PATTERN = re.compile(r"[A-ZÅÄÖ]+")
REPEATING_CHARACTER_PATTERN = re.compile(r"([A-ZÅÄÖ0-9])\1")
REPEATING_LETTER_PATTERN = re.compile(r"([A-ZÅÄÖ0-9])\1{2,}")
PUNCTUATION_PATTERN = re.compile(r"([.,!?;:])+")


def read_text(filename: str):
    """Read a UTF-8 text file and normalize it to uppercase."""

    with open(filename, "r", encoding="utf-8") as file:
        return file.read().upper()


def frequent_items(counter, minimum=MIN_FREQUENCY):
    return [
        (item, count)
        for item, count in counter.most_common()
        if count >= minimum
    ]


def count_frequency(items):
    counter = Counter(items)

    return {
        "count": len(items),
        "unique": len(counter),
        "frequency": sorted(
            counter.items(),
            key=lambda item: (-item[1], item[0])
        )
    }


def analyze_letters(text: str):
    """Analyze letter frequency in the supplied text."""

    return count_frequency(
        [c for c in text if c.isalpha()]
    )


def analyze_words(text: str):
    """Analyze word frequency in the supplied text."""

    return count_frequency(
        WORD_PATTERN.findall(text)
    )


def get_grams(text: str, n: int):
    """Return overlapping n-grams within words."""

    grams = []

    for word in WORD_PATTERN.findall(text):
        grams.extend(
            word[i:i+n]
            for i in range(len(word) - n + 1)
        )

    return grams


def separate_trigrams(trigrams):
    """
    Separate trigrams into triple-letter, double-letter,
    and non-double-letter trigrams.
    """

    triple_letter_trigrams = []
    double_letter_trigrams = []
    non_double_letter_trigrams = []

    for trigram in trigrams:
        if any(char * 3 in trigram for char in set(trigram)):
            triple_letter_trigrams.append(trigram)

        elif any(char * 2 in trigram for char in set(trigram)):
            double_letter_trigrams.append(trigram)

        else:
            non_double_letter_trigrams.append(trigram)

    return (
        triple_letter_trigrams,
        double_letter_trigrams,
        non_double_letter_trigrams,
    )


def analyze_bigrams(text: str):
    """Analyze bigram frequency in the supplied text."""

    return count_frequency(
        get_grams(text, 2)
    )


def analyze_trigrams(text: str):
    """Analyze trigram frequency and classify trigram types."""

    trigrams = get_grams(text, 3)

    (
        triple_letter_trigrams,
        double_letter_trigrams,
        non_double_letter_trigrams,
    ) = separate_trigrams(trigrams)

    return (
        count_frequency(trigrams),
        count_frequency(triple_letter_trigrams),
        count_frequency(double_letter_trigrams),
        count_frequency(non_double_letter_trigrams),
    )


def analyze_double_letters(text: str):
    """Analyze sequences of two identical characters."""

    return count_frequency(
        [m.group(0) for m in REPEATING_CHARACTER_PATTERN.finditer(text)]
    )


def analyze_repeating_letters(text: str):
    """Analyze sequences of three or more identical characters."""

    return count_frequency(
        [m.group(0) for m in REPEATING_LETTER_PATTERN.finditer(text)]
    )


def analyze_punctuation(text: str):
    """Analyze consecutive punctuation sequences."""

    return count_frequency(
        [m.group(0) for m in PUNCTUATION_PATTERN.finditer(text)]
    )

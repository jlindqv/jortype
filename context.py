from collections import Counter, defaultdict

from analysis import get_grams
from config import CONTEXT_COVERAGE, MIN_FREQUENCY, ALTERNATE_COUNT


def build_contexts(trigrams):
    """
    Build letter contexts from weighted trigram frequencies.

    Each middle letter receives counters for the characters before
    and after it, as well as the frequencies of complete trigrams.
    """

    contexts = defaultdict(lambda: {
        "before": Counter(),
        "after": Counter(),
        "trigrams": Counter(),
    })

    for trigram, count in trigrams:
        left, middle, right = trigram

        contexts[middle]["before"][left] += count
        contexts[middle]["after"][right] += count
        contexts[middle]["trigrams"][trigram] += count

    return dict(contexts)


def analyze_letter_context(text: str):
    """Analyze the contexts in which each letter occurs."""

    trigrams = get_grams(text, 3)
    counts = Counter(trigrams)

    return build_contexts(counts.items())


def distribute_contexts(trigrams, variants=ALTERNATE_COUNT):
    """
    Distribute contexts across variant groups by cumulative frequency.
    """

    groups = [[] for _ in range(variants)]
    totals = [0] * variants

    for context, count in trigrams:
        index = totals.index(min(totals))

        groups[index].append((context, count))
        totals[index] += count

    return groups


def generate_context_rules(contexts):
    """
    Select the most frequent contexts for each letter until the
    configured context coverage is reached.
    """

    rules = {}

    for letter, context in contexts.items():
        trigrams = context["trigrams"]

        total = sum(trigrams.values())
        covered = 0
        selected = []

        for trigram, count in trigrams.most_common():
            if count < MIN_FREQUENCY:
                break

            selected.append((trigram, count))
            covered += count

            if covered / total >= CONTEXT_COVERAGE:
                break

        rules[letter] = {
            "total": total,
            "covered": covered,
            "coverage": covered / total,
            "contexts": selected,
        }

    return rules


def calculate_weight(count, total):
    """Return the relative frequency of a context."""

    if total == 0:
        return 0

    return count / total
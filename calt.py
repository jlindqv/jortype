from context import (
    build_contexts,
    calculate_weight,
    distribute_contexts,
    generate_context_rules,
)
from opentype import glyph_name


def _build_calt_contexts(trigrams):
    """Build CALT contexts from weighted trigram frequencies."""

    rules = generate_context_rules(
        build_contexts(trigrams)
    )

    return {
        letter: {
            "total": data["total"],
            "covered": data["covered"],
            "coverage": data["coverage"],
            "variants": distribute_contexts(data["contexts"]),
        }
        for letter, data in rules.items()
    }


def analyze_calt(report):
    """Analyze trigram contexts used for CALT generation."""

    return {
        "context": _build_calt_contexts(
            report["non_double_letter_trigrams"]["frequency"]
        ),
        "double_letter_context": _build_calt_contexts(
            report["double_letter_trigrams"]["frequency"]
        ),
    }


def generate_calt_rules(calt):
    """Convert CALT context data into individual substitution rules."""

    rules = []

    for context_name, context_data in calt.items():
        for letter, data in context_data.items():
            for variant_index, contexts in enumerate(
                data["variants"],
                start=1,
            ):
                for trigram, count in contexts:
                    left, middle, right = trigram

                    # Relative frequency for this context
                    weight = calculate_weight(
                        count,
                        data["total"],
                    )

                    rules.append({
                        "type": context_name,
                        "letter": middle,
                        "variant": variant_index,
                        "context": trigram,
                        "before": left,
                        "after": right,
                        "count": count,
                        "weight": weight,
                    })

    # Prioritize the most frequent contexts
    rules.sort(
        key=lambda rule: (
            -rule["weight"],
            rule["letter"],
        )
    )

    return rules


def generate_triple_letter_trigram_rules(triple_letter_trigrams):
    """Generate deterministic variant cycles for triple-letter trigrams."""

    rules = []

    for sequence, count in triple_letter_trigrams["frequency"]:
        variants = [
            glyph_name(sequence[0], i)
            for i in range(len(sequence))
        ]

        rules.append({
            "type": "triple_letter",
            "letter": sequence[0],
            "context": sequence,
            "variants": variants,
            "count": count,
        })

    return rules
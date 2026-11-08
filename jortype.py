import sys
import argparse

from analysis import (
    analyze_bigrams,
    analyze_double_letters,
    analyze_letters,
    analyze_punctuation,
    analyze_repeating_letters,
    analyze_trigrams,
    analyze_words,
    read_text,
)

from calt import (
    analyze_calt,
    generate_calt_rules,
    generate_triple_letter_trigram_rules,
)

from context import analyze_letter_context

from opentype import (
    generate_opentype_subrules,
    generate_opentype_triple_letter_rules,
)

from report_writer import (
    print_fea,
    write_calt_report,
    write_json_report,
    write_text_report,
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze text file."
    )
    parser.add_argument(
        "textfile",
        help="The text file to analyze"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--calt",
        action="store_true",
        help="Output CALT analysis"
    )
    parser.add_argument(
        "--rules",
        action="store_true",
        help="Generate OpenType substitution rules"
    )

    args = parser.parse_args()

    try:
        text = read_text(args.textfile)
    except FileNotFoundError:
        print(
            f"Could not open '{args.textfile}'.",
            file=sys.stderr
        )
        return 1

    report = {
        "filename": args.textfile,
        "letters": analyze_letters(text),
        "words": analyze_words(text),
        "double_letters": analyze_double_letters(text),
        "repeating_letters": analyze_repeating_letters(text),
        "bigrams": analyze_bigrams(text),
        "punctuation": analyze_punctuation(text),
        "context": analyze_letter_context(text),
    }

    (
        report["trigrams"],
        report["triple_letter_trigrams"],
        report["double_letter_trigrams"],
        report["non_double_letter_trigrams"],
    ) = analyze_trigrams(text)

    if args.calt:
        calt_report = analyze_calt(report)
        write_calt_report(calt_report, sys.stdout)

    elif args.rules:
        calt_report = analyze_calt(report)
        calt_rules = generate_calt_rules(calt_report)

        triple_letter_rules = generate_triple_letter_trigram_rules(
            report["triple_letter_trigrams"]
        )

        opentype_subrules = generate_opentype_subrules(calt_rules)

        lookup_definitions, chain_rules = (
            generate_opentype_triple_letter_rules(
                triple_letter_rules
            )
        )

        print_fea(
            lookup_definitions,
            chain_rules,
            opentype_subrules
        )

    elif args.json:
        write_json_report(report, sys.stdout)

    else:
        write_text_report(report, sys.stdout)

    return 0


if __name__ == "__main__":
    sys.exit(main())
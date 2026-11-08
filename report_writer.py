from datetime import datetime
import json

from analysis import frequent_items
from config import MIN_FREQUENCY


FREQUENCY_FILTERED_SECTIONS = {
    "bigrams",
    "trigrams",
}


def write_heading(file, title):
    """Write a section heading."""

    print("=" * 50, file=file)
    print(title, file=file)
    print("=" * 50, file=file)
    print(file=file)


def write_frequency(file, title, data, minimum=MIN_FREQUENCY):
    """Write frequency statistics."""

    write_heading(file, title)

    print(f"Count  : {data['count']}", file=file)
    print(f"Unique : {data['unique']}", file=file)
    print(file=file)

    if not data["frequency"]:
        print("No results.", file=file)
        print(file=file)
        return

    width = max(
        len(item)
        for item, _ in data["frequency"]
    )

    for item, count in data["frequency"]:
        if count >= minimum:
            print(f"{item:<{width}} {count}", file=file)

    print(file=file)


def write_context(file, data):
    """Write letter context statistics."""

    write_heading(file, "LETTER CONTEXT")

    for letter, context in sorted(data.items()):
        print(letter, file=file)
        print(file=file)

        print("  BEFORE", file=file)
        for item, count in frequent_items(context["before"]):
            print(f"    {item:10} {count}", file=file)

        print(file=file)

        print("  AFTER", file=file)
        for item, count in frequent_items(context["after"]):
            print(f"    {item:10} {count}", file=file)

        print(file=file)

        print("  TRIGRAMS", file=file)
        for item, count in frequent_items(context["trigrams"]):
            print(f"    {item:10} {count}", file=file)

        print(file=file)


def write_context_rules(file, data):
    """Write selected context rules."""

    write_heading(file, "CONTEXT RULES")

    for letter, context in sorted(data.items()):
        print(
            f"{letter}: "
            f"{context['covered']}/{context['total']} "
            f"({context['coverage']:.1%})",
            file=file,
        )

        for trigram, count in context["contexts"]:
            print(f"    {trigram:10} {count}", file=file)

        print(file=file)


def write_json_report(report, file):
    """Write the analysis report as JSON."""

    json.dump(
        report,
        file,
        ensure_ascii=False,
        indent=4,
    )


def write_text_report(report, file):
    """Write the analysis report in human-readable form."""

    print("FONT ANALYSIS REPORT", file=file)
    print(file=file)

    print(
        f"Source file : {report['filename']}",
        file=file,
    )
    print(
        f"Generated   : {datetime.now()}",
        file=file,
    )
    print(file=file)

    for section, data in report.items():
        if section == "filename":
            continue

        if section == "context":
            write_context(file, data)
            continue

        minimum = (
            MIN_FREQUENCY
            if section in FREQUENCY_FILTERED_SECTIONS
            else 1
        )

        write_frequency(
            file,
            section.upper(),
            data,
            minimum,
        )


def write_calt_report(data, file):
    """Write the CALT analysis in human-readable form."""

    print("CALT ANALYSIS REPORT", file=file)
    print(file=file)

    for section, contexts in data.items():
        write_heading(file, section.upper())

        for letter, context in sorted(contexts.items()):
            print(
                f"{letter}: "
                f"{context['covered']}/{context['total']} "
                f"({context['coverage']:.1%})",
                file=file,
            )

            for variant_index, variant in enumerate(
                context["variants"],
                start=1,
            ):
                total = sum(
                    count
                    for _, count in variant
                )

                print(
                    f"  VARIANT {variant_index}: {total}",
                    file=file,
                )

                for trigram, count in variant:
                    print(
                        f"    {trigram:10} {count}",
                        file=file,
                    )

                print(file=file)

            print(file=file)


def print_array(array, indent=""):
    """Print FEA lines with one level of indentation."""

    for item in array:
        print(indent + item)

def print_fea(
    lookup_definitions,
    chain_rules,
    opentype_subrules,
):
    """Write the generated OpenType CALT feature."""

    print("languagesystem DFLT dflt;")
    print("languagesystem latn dflt;")
    print()

    print_array(lookup_definitions)
    print()

    print("feature calt {")
    print_array(chain_rules, "\t")
    print_array(opentype_subrules, "\t")
    print("} calt;")

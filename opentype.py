from collections import defaultdict
from config import GLYPH_NAMES


def glyph_name(letter, variant):
    """Return the glyph name for a base letter and variant index."""

    base = GLYPH_NAMES.get(letter, letter)

    if variant == 0:
        return base

    return f"{base}.ss{variant:02d}"


def generate_opentype_subrules(rules):
    """Generate chained-context OpenType substitution rules."""

    subrules = []

    for rule in rules:
        letter = rule["letter"]
        variant = rule["variant"]
        before = rule["before"]
        after = rule["after"]

        source_before = glyph_name(before, 0)
        source_letter = glyph_name(letter, 0)
        source_after = glyph_name(after, 0)
        target = glyph_name(letter, variant)

        subrule = (
            f"sub {source_before} "
            f"{source_letter}' "
            f"{source_after} "
            f"by {target};"
        )

        subrules.append(subrule)

    return subrules


def generate_opentype_triple_letter_rules(rules):
    """
    Generate FEA lookup definitions and chained-context substitutions
    for triple-letter trigram rules.
    """

    lookup_definitions = []
    lookup_names = {}
    chain_rules = []
    seen_contexts = set()

    for rule in rules:
        context = rule["context"]
        variants = rule["variants"]

        if context in seen_contexts:
            continue

        seen_contexts.add(context)

        if len(variants) != len(context):
            raise ValueError(
                f"Number of variants ({len(variants)}) does not match "
                f"context length ({len(context)}) for '{context}'"
            )

        parts = []
        has_substitution = False

        for position, target_glyph in enumerate(variants):
            source_glyph = glyph_name(context[position], 0)

            if target_glyph == source_glyph:
                # Identity substitution: this glyph only provides context.
                parts.append(source_glyph)
                continue

            has_substitution = True
            lookup_key = (source_glyph, target_glyph)

            if lookup_key not in lookup_names:
                safe_name = target_glyph.replace(".", "_")
                lookup_name = f"Triple_{source_glyph}_to_{safe_name}"

                lookup_names[lookup_key] = lookup_name

                lookup_definitions.append(
                    f"lookup {lookup_name} {{\n"
                    f"    sub {source_glyph} by {target_glyph};\n"
                    f"}} {lookup_name};"
                )

            lookup_name = lookup_names[lookup_key]
            parts.append(
                f"{source_glyph}' lookup {lookup_name}"
            )

        if not has_substitution:
            # All positions are identity substitutions.
            continue

        chain_rules.append(
            "sub " + " ".join(parts) + ";"
        )

    return lookup_definitions, chain_rules


def get_glyph_variants(font_path):
    """
    Return the variants available in a font.

    Returns:
        {
            "F": ["ss01", "ss02"],
            "Q": ["ss01"],
            "S": ["ss01", "ss02", "ss03"],
        }
    """
    
    from fontTools.ttLib import TTFont

    font = TTFont(font_path)
    names = set(font.getGlyphOrder())

    variants = defaultdict(list)
    for name in names:
        if "." not in name:
            continue
        base, suffix = name.split(".", 1)
        if suffix.startswith("ss") and suffix[2:].isdigit():
            variants[base].append(suffix)

    for base in variants:
        variants[base].sort(key=lambda s: int(s[2:]))

    return dict(variants)

def generate_universal_triple_rules(base_glyphs, glyph_variants):
    """
    base_glyphs: Set of base glyph names to generate triple-letter rules for.
    glyph_variants: {base_glyph: [sorted variant suffixes]} from get_glyph_variants().
    """
    lookups_needed = defaultdict(dict)  # suffix -> {source: target}
    chain_rules = []

    for glyph in sorted(base_glyphs):
        suffixes = glyph_variants.get(glyph, [])
        total_states = 1 + len(suffixes)  # +1 for the default glyph

        if total_states < 2:
            continue  # No variants available, so no triple-letter rule can be generated for this glyph.

        parts = [f"{glyph}'"]  # Position 0: always identity

        for position in (1, 2):
            state_index = position % total_states

            if state_index == 0:
                # The cycle has wrapped around to the default glyph (the glyph has too few variants).
                parts.append(f"{glyph}'")
            else:
                suffix = suffixes[state_index - 1]
                target = f"{glyph}.{suffix}"
                lookups_needed[suffix][glyph] = target
                parts.append(f"{glyph}' lookup Triple_to_{suffix}")

        chain_rules.append("sub " + " ".join(parts) + ";")

    lookup_definitions = []
    for suffix, mapping in lookups_needed.items():
        sources = " ".join(mapping.keys())
        targets = " ".join(mapping.values())
        lookup_definitions.append(
            f"lookup Triple_to_{suffix} {{\n"
            f"    sub [{sources}] by [{targets}];\n"
            f"}} Triple_to_{suffix};"
        )

    return lookup_definitions, chain_rules
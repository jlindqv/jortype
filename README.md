# Jortype

### Your text. Jortype.

**Jortype** is a Python tool for analyzing text statistics and character context, with a particular focus on font design and OpenType development.

The project started as a text-analysis utility for studying letter and character frequencies in real Swedish text. It has since evolved toward a more specific goal:

> **Use statistics from real text to generate contextual glyph variation that makes a multi-variant font look less mechanically generated and more naturally handwritten.**

The basic idea is simple: instead of always displaying the same glyph, use the surrounding text to determine which alternate glyph should be displayed.

In other words, we are trying to make a deterministic font behave as if somebody's hand occasionally decided to draw the same letter slightly differently.

## Quick Start

Jortype requires Python 3.9 or later and has no mandatory
third-party dependencies.

Clone the repository:

    git clone https://github.com/jlindqv/jortype.git
    cd jortype

Analyze a text file:

    python jortype.py novel.txt

Generate OpenType feature code:

    python jortype.py novel.txt --rules

---

## What Are We Actually Trying to Do?

Suppose a font contains three forms of the letter `E`:

```text
E
E.ss01
E.ss02
````

The naive solution is to use the default glyph everywhere:

```text
E E E E E E
```

A slightly less naive solution is to cycle through the variants:

```text
E E.ss01 E.ss02 E E.ss01 E.ss02
```

Both approaches work, but both produce predictable patterns.

Real handwriting does not work that way.

The same letter may be drawn differently depending on what surrounds it, how frequently a particular combination occurs, or simply because the person writing it did not reproduce the glyph identically every time.

This project explores whether statistical analysis of real text can be used to reproduce some of that variation.

For example:

```text
DET    246
DEN    105
BER     86
TER     78
```

If `E` occurs in these contexts with very different frequencies, there is no particular reason to force all of them to use the same alternate glyph.

Instead, Jortype can distribute significant contextual patterns across the available variants.

The goal is not randomness for its own sake.

The goal is:

> **Deterministic rules, stochastic-looking output.**

The font should remain completely predictable to the software using it, while the resulting text should not immediately reveal a simple mechanical pattern to the human reader.

That is the experiment.

---

## The Core Idea

The current model separates several kinds of textual patterns.

Not all trigrams are treated equally.

A trigram such as:

```text
DET
```

contains three different letters and can be used as ordinary contextual information.

A trigram such as:

```text
ELL
```

contains a double letter. It represents a different typographic problem because the same glyph occurs twice in succession.

A trigram such as:

```text
FFF
```

contains three identical letters and is treated as a special repeated-letter case.

The current analysis therefore separates trigrams into:

1. Triple-letter trigrams
2. Double-letter trigrams
3. Non-double-letter trigrams

The distinction is useful because these cases can require different substitution strategies.

The exact OpenType rule hierarchy remains experimental.

---

## Analysis Pipeline

The current workflow looks roughly like this:

```text
                         TEXT CORPUS
                              │
                              ▼
                       ┌───────────────┐
                       │ Text Analysis │
                       └───────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
          Letters          Bigrams          Trigrams
                                                │
                                                ▼
                                      ┌──────────────────┐
                                      │ Trigram Analysis │
                                      └────────┬─────────┘
                                               │
                         ┌─────────────────────┼─────────────────────┐
                         ▼                     ▼                     ▼
                 Triple-letter         Double-letter         Non-double-letter
                   trigrams              trigrams               trigrams
                         │                     │                     │
                         ▼                     ▼                     ▼
                  Triple rules         Context rules          Context rules
                         │                     │                     │
                         └─────────────────────┼─────────────────────┘
                                               ▼
                                         CALT rule model
                                               │
                                               ▼
                                      OpenType generation
                                               │
                                               ▼
                                            .fea file
                                               │
                                               ▼
                                          Font engine
```

The important point is that Jortype is not simply trying to generate as many substitutions as possible.

It is trying to generate a **coherent sequence of transformations** where each rule class solves a particular problem.

---

## Features

* **Letter Frequency Analysis**

  Counts individual letters and their frequencies.

* **Word Frequency Analysis**

  Counts words and identifies the most common words in the text.

* **Bigram Analysis**

  Analyzes pairs of consecutive letters within words.

* **Trigram Analysis**

  Analyzes sequences of three consecutive letters within words.

* **Double-Letter Analysis**

  Identifies repeated letters and digits such as `LL`, `SS`, and `00`.

* **Repeating-Letter Analysis**

  Identifies sequences of three or more repeated characters, such as `AAA` and `OOO`.

* **Punctuation Analysis**

  Analyzes sequences of common punctuation characters.

* **Letter Context Analysis**

  Examines which characters commonly occur before and after each letter, as well as the trigrams in which each letter occurs.

* **Context Distribution**

  Distributes significant contexts across a configurable number of glyph variants while attempting to balance the amount of text affected by each variant.

* **CALT Analysis**

  Produces statistical data intended for generating OpenType contextual alternate (`calt`) rules.

* **OpenType Rule Generation**

  Converts the contextual model into OpenType substitution rules and generates `.fea` feature code.

* **JSON Output**

  Produces machine-readable analysis data for use by other tools and scripts.

---

## Requirements

* Python 3.9 or later

Jortype uses only the Python standard library by default.

The optional `get_glyph_variants()` function requires
[fontTools](https://github.com/fonttools/fonttools).

Install it with:

    pip install fonttools

---

## Usage

Run the analyzer on a text file:

```bash
python jortype.py <textfile>
```

For example:

```bash
python jortype.py novel.txt
```

By default, the analyzer writes a human-readable report to standard output.

The output can be redirected to a file:

```bash
python jortype.py novel.txt > analysis.txt
```

### JSON Output

Use the `--json` option to produce a machine-readable JSON report:

```bash
python jortype.py novel.txt --json
```

The JSON output can be redirected to a file:

```bash
python jortype.py novel.txt --json > analysis.json
```

The JSON format is intended to make the analyzer useful as one stage in a larger toolchain.

### CALT Analysis

Use the `--calt` option to inspect the statistical model used for contextual alternate development:

```bash
python jortype.py novel.txt --calt
```

The CALT analysis reports context coverage and distributes significant contexts across the available alternate glyphs.

For example:

```text
E: 1336/1661 (80.4%)

  VARIANT 1: 444
    DET        246
    NET         41
    VET         36

  VARIANT 2: 452
    DEN        105
    GEN         65
    VER         52
```

Here the middle letter of each trigram is the glyph being varied.

### OpenType Rule Generation

Use the `--rules` option to generate OpenType feature code:

```bash
python jortype.py --rules novel.txt
```

The generated output is a complete `.fea` feature definition containing the generated `calt` rules and supporting lookup definitions.

The generated feature file can be imported into FontForge and compiled into a font.

The generated OpenType behavior should still be considered experimental. Different applications and font engines do not necessarily support contextual substitution in the same way.

---

## Examples

The examples directory contains a sample text corpus and
pre-generated output from Jortype.

To analyze the example text:

```bash
python jortype.py examples/Projekt-Fika.txt
```

To generate CALT analysis:

```bash
python jortype.py examples/Projekt-Fika.txt --calt
```

To generate OpenType feature code:

```bash
python jortype.py examples/Projekt-Fika.txt --rules
```

Pre-generated results are available in examples/results/.

---

## Configuration

The analyzer currently uses several constants to control contextual analysis:

```python
MIN_FREQUENCY = 3
CONTEXT_COVERAGE = 0.80
ALTERNATE_COUNT = 2
```

### `MIN_FREQUENCY`

The minimum number of occurrences required for a context to be considered significant.

This prevents the analysis from being overwhelmed by extremely rare combinations.

### `CONTEXT_COVERAGE`

Determines how much of a letter's observed contextual usage should be covered by the selected contexts.

For example:

```python
CONTEXT_COVERAGE = 0.80
```

means that the most common contexts are selected until they account for approximately 80% of the observed occurrences.

### `ALTERNATE_COUNT`

Specifies the number of alternate glyphs available in addition to the default glyph.

For example:

```python
ALTERNATE_COUNT = 2
```

means that the analyzer assumes:

```text
default
ss01
ss02
```

The default glyph is not counted as an alternate.

---

## Context Distribution

Context distribution is deliberately not based on simply assigning the most common contexts to the first variant, the next contexts to the second variant, and so on.

Instead, contexts are distributed according to their total frequency.

For example, if the contexts have frequencies:

```text
A    100
B     90
C     80
D     20
E     10
```

the distribution attempts to balance the total amount of text assigned to each variant.

This matters because the goal is not merely to distribute the number of rules.

It is to distribute the **amount of text affected by those rules**.

The result should give each glyph variant a roughly comparable share of the text while preserving meaningful contextual distinctions.

The distribution is therefore statistical rather than sequential.

---

## CALT Rule Model

The current model divides contextual substitutions into several classes.

### Context Rules

Trigrams without repeated letters are treated as ordinary contextual patterns.

For example:

```text
DET
JAG
RYM
KAT
```

These contexts can be distributed among the available alternates based on their frequency.

A rule may then produce a substitution such as:

```text
DET → D E.ss01 T
```

The actual assignment is determined statistically rather than manually.

### Double-Letter Contexts

Trigrams containing a double letter are handled separately.

For example:

```text
ELL
ALL
OTT
```

These contexts represent a special case because the same glyph occurs twice.

The analyzer can therefore distinguish these patterns from ordinary three-letter contexts.

The generated rules currently target one glyph within the contextual sequence rather than attempting to replace the entire sequence.

### Triple-Letter Trigrams

Trigrams containing three identical letters are separated from ordinary double-letter trigrams.

For example:

```text
FFF
OOO
ÅÅÅ
```

These are sufficiently unusual that statistical distribution between alternates is not considered necessary.

Instead, the current experimental rule model can deterministically transform the sequence using the available glyph variants.

For example, with two alternates:

```text
FFF → F F.ss01 F.ss02
```

The purpose is to prevent three identical glyphs from remaining visually identical when the font contains alternate forms.

### Repeating Letters

The analyzer also detects longer sequences such as:

```text
FFFF
OOOO
ÅÅÅÅ
```

At present, these sequences are analyzed separately, but a general stateful cyclic substitution system has **not** been implemented.

This is deliberate.

OpenType substitutions are context-based rather than general-purpose procedural code, so implementing an arbitrary counter-like cycle for sequences of any length would require a much more complicated rule system.

The current approach therefore focuses on explicit contextual rules rather than pretending that OpenType has a hidden little Python interpreter living inside the font.

---

## Punctuation

Punctuation is analyzed separately from word-internal letter n-grams.

Examples of potentially useful punctuation sequences include:

```text
!!
!!!
!?
?? 
???
...
...!
?!!
```

The intended approach is deterministic rather than statistical.

Because punctuation sequences are relatively uncommon and visually distinctive, simple explicit substitutions may be preferable to attempting to construct a large statistical model.

Punctuation rule generation is currently incomplete.

---

## Rule Interaction

One of the most important discoveries during development is that generated rules do not necessarily need to be mutually exclusive at the level of an entire word.

OpenType contextual substitutions operate on local glyph contexts.

For example, the word:

```text
ELLER
```

contains the overlapping trigrams:

```text
ELL
LLE
LER
```

These contexts can target different glyph positions:

```text
ELL → E L L.ss01
LLE → L L.ss02 E
LER → L E.ss01 R
```

The rules therefore do not automatically conflict simply because their contexts overlap.

However, rule ordering and the structure of chained substitutions can still affect the final result.

The generator therefore treats different rule classes separately and attempts to avoid unnecessary overlap.

This remains an important area for testing.

---

## Avoiding Predictable Patterns

The biggest danger is replacing one deterministic pattern with another.

For example, a simple variant cycle produces:

```text
A B C A B C A B C
```

That is technically varied, but visually predictable.

The statistical approach instead attempts to distribute variation according to the structure of real language.

The rules remain deterministic.

The irregularity comes from the statistical structure of the text and the different contextual patterns that trigger different substitutions.

The desired result is:

> **Deterministic typography with an appearance of natural variation.**

---

## Font Integration

The OpenType generator currently uses glyph names from a configurable mapping:

```python
GLYPH_NAMES = {
    "Å": "Aring",
    "Ä": "Adieresis",
    "Ö": "Odieresis",
}
```

This is necessary because the character used in the source text does not always correspond directly to the glyph name used by the font.

For example:

```text
Å → Aring
Ä → Adieresis
Ö → Odieresis
```

The generator also supports standard alternate naming such as:

```text
F
F.ss01
F.ss02
```

A future version may inspect the actual font and discover available glyph alternates automatically rather than relying on a manually maintained mapping.

---

## Font Engine Compatibility

The generated `.fea` code has been tested successfully in FontForge and in applications that support the generated contextual substitutions.

However, support for OpenType contextual alternates is application-dependent.

In particular, testing with Clip Studio Paint showed that the same `calt` rules that work elsewhere were not applied by the application.

A separate font using ligatures for repeated-letter variation behaved differently, suggesting that application support for contextual alternates may be incomplete or inconsistent.

This means that the generated feature code should not be assumed to work identically in every application.

For workflows where the target application does not support the required OpenType features, possible alternatives include:

* composing text in an application with suitable OpenType support and converting it to vectors,
* manually placing vector text,
* or manually lettering directly in the target application.

The analyzer itself remains useful independently of any particular font engine.

---

## Project Structure

```text
jortype/
│
├── .continue/
│   └── rules/
│       └── jortype.md
|
├── LICENSE
├── README.md
├── .gitignore
│
├── jortype.py
├── analysis.py
├── calt.py
├── config.py
├── context.py
├── opentype.py
├── report_writer.py
│
├── examples/
│   ├── LICENSE
│   ├── README.md
│   ├── Projekt-Fika.txt
│   └── results/
│       ├── projekt-fika-analysis.txt
│       ├── projekt-fika-calt.fea
│       └── projekt-fika.json
│
└── tests/
    ├── test_analysis.py
    ├── test_calt.py
    ├── test_context.py
    ├── test_opentype.py
    └── test_report_writer.py
```

The project is divided into several modules:

```text
jortype.py
    Command-line entry point and analysis pipeline.

analysis.py
    Basic text statistics, n-grams, repetitions and punctuation.

context.py
    Letter-context analysis, context selection and distribution.

calt.py
    CALT analysis and rule generation.

opentype.py
    Glyph naming and OpenType substitution generation.

config.py
    Configuration constants and glyph-name mappings.

report_writer.py
    Human-readable, JSON and FEA output.
```

The separation is intentional.

The statistical model should be usable independently of the final OpenType implementation.

---

## Tests

Run the test suite using Python's built-in unittest framework:

    python -m unittest discover -s tests -v

## Project Status

This project is experimental and under active development.

The text-analysis portion is functional.

The contextual distribution model is functional.

The project can generate OpenType `.fea` files containing contextual substitution rules.

The generated rules have been successfully inspected and tested in FontForge, and contextual substitutions have been observed working in LibreOffice.

However, application compatibility remains an unresolved issue.

The project has therefore moved from:

> "Can statistics generate useful contextual rules?"

to:

> "How should those rules be structured, and which font engines will actually use them?"

The ultimate test is visual:

> **Does the resulting font actually look more naturally handwritten?**

If the answer is no, we will have built a very elaborate machine for making fonts weird.

If the answer is yes, we might have stumbled onto something useful.

Both outcomes are acceptable.

---

# Future Development

Jortype is a functional experimental project, but development is currently low priority.

The existing functionality is available for anyone interested in statistical text analysis, contextual glyph variation or OpenType feature generation.

There are several areas where the implementation could be extended, refined or optimized. The list below documents potential directions for future development rather than an active development roadmap.

Contributions, experiments, alternative approaches and ideas are welcome. If you find the project useful, feel free to build upon it.

## CALT Generator

* [x] Define the internal representation of CALT rules.
* [x] Generate OpenType `calt` feature code.
* [x] Generate contextual rules for trigrams without double letters.
* [x] Generate contextual rules for trigrams containing double letters.
* [x] Separate triple-letter trigrams from ordinary double-letter trigrams.
* [x] Generate deterministic triple-letter trigram rules.
* [ ] Define the final rule hierarchy.
* [ ] Define exactly which rule classes should interact.
* [ ] Generate punctuation substitution rules.
* [ ] Investigate rule ordering and chained substitutions further.
* [ ] Detect potentially problematic substitutions before generating feature code.
* [ ] Validate generated `.fea` syntax automatically.

## Font Integration

* [x] Define a consistent naming scheme for alternate glyphs.
* [x] Support `.ss01`, `.ss02`, etc.
* [x] Generate FontForge-compatible feature definitions.
* [x] Generate complete OpenType feature files.
* [ ] Discover available glyph alternates directly from the font.
* [ ] Replace manually maintained glyph-name mappings where possible.
* [ ] Support arbitrary numbers of alternates.
* [ ] Test generated features with additional font engines.
* [ ] Investigate whether alternate glyphs should have deliberately different visual characteristics.

## Context Model

* [x] Separate ordinary contexts from double-letter contexts.
* [x] Balance context distribution by frequency.
* [x] Apply configurable context coverage.
* [ ] Investigate word-boundary contexts.
* [ ] Investigate sentence and word position.
* [ ] Investigate interactions between multiple applicable contexts.
* [ ] Determine how much contextual coverage is actually useful.
* [ ] Investigate whether different letters benefit from different numbers of alternates.
* [ ] Investigate whether rare contexts should be ignored or assigned special treatment.

## Repetition

* [x] Detect sequences of three or more repeated characters.
* [x] Separate triple-letter trigrams from ordinary double-letter trigrams.
* [ ] Define a practical strategy for sequences longer than three characters.
* [ ] Determine how repeated-letter rules should interact with contextual substitutions.
* [ ] Test longer repeated sequences with real font engines.
* [ ] Decide whether a universal cyclic system is actually worth implementing.

## Rule Generation

* [x] Generate lookup definitions for triple-letter substitutions.
* [x] Generate contextual substitution rules.
* [x] Generate complete `.fea` output.
* [ ] Group and optimize generated lookups.
* [ ] Detect redundant rules.
* [ ] Measure the number of generated rules for realistic text corpora.
* [ ] Determine whether rule count has a measurable impact on font size or performance.
* [ ] Validate generated `.fea` syntax automatically.
* [ ] Test generated fonts in multiple applications.

## Future Experiments

* [ ] Estimate how many glyph alternates are needed to achieve a desired level of variation.
* [ ] Investigate language-specific statistical models.
* [ ] Compare contextual variation against simple sequential cycling.
* [ ] Measure the amount of visible repetition in generated text.
* [ ] Investigate whether punctuation benefits from contextual variation.
* [ ] Investigate contextual variation for numerals.
* [ ] Test the system on substantially larger text corpora.
* [ ] Compare different values of `CONTEXT_COVERAGE`.
* [ ] Compare different numbers of available alternates.
* [ ] Investigate whether application support for `calt` changes over time.
* [ ] Find out whether this idea is brilliant or completely stupid.

---

## Contributing

This is currently a personal experimental project.

Ideas, bug reports, improvements, and interesting failures are welcome.

---

## License

This project uses two different licenses:

Software: The source code is licensed under the MIT License. See LICENSE.
Example materials: All materials in the examples/ directory, including source documents and generated output files, are dedicated to the public domain under CC0 1.0 Universal. See examples/LICENSE.

Unless explicitly stated otherwise, the MIT License applies to the software in the project root, while CC0 1.0 applies to the contents of the examples/ directory.

"""
Mutmut configuration for AsciiDoc Artisan mutation testing.

Mutation testing systematically modifies (mutates) code and runs tests
to verify that the tests catch the mutations. This helps identify:
- Weak or missing test assertions
- Untested code paths
- Redundant code

Target: 80%+ mutation score for critical modules
"""


def pre_mutation(context):
    """
    Hook called before each mutation.
    Can be used to skip certain types of mutations.
    """
    # Skip mutations in test files
    if "test_" in context.filename:
        context.skip = True
        return

    # Skip mutations in generated or legacy code
    if any(pattern in context.filename for pattern in ["__pycache__", ".pyc", "venv/", "build/"]):
        context.skip = True
        return


# Paths to mutate (focus on critical code)
paths_to_mutate = [
    "src/asciidoc_artisan/core/",
    "src/asciidoc_artisan/workers/",
    "src/asciidoc_artisan/ui/",
]

# Test command to run after each mutation
tests_dir = "tests/"
runner = "python -m pytest -x --tb=no -q"

# Dict config
dict_synonyms = ["dict"]

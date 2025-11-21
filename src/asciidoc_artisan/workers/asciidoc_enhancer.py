"""
AsciiDoc Enhancer - Post-processes AsciiDoc output for better quality.

Extracted from PandocWorker to reduce class size (MA principle).
Handles AsciiDoc formatting improvements and corrections.
"""

import re

# Pre-compiled regex patterns for post-processing (hot path optimization, v1.9.1)
# Compiling at module level is 2-3x faster than compiling on each conversion
_SOURCE_BLOCK_FIX = re.compile(r"\[source\](\w+)")
_HEADING_SPACING = re.compile(r"\n(=+\s+[^\n]+)\n(?!=)")
_TABLE_CLEANUP = re.compile(r"\|===\n\n")
_ADMONITION_FORMAT = re.compile(r"(?m)^(NOTE|TIP|IMPORTANT|WARNING|CAUTION):\s*")


class AsciiDocEnhancer:
    """
    Post-processes AsciiDoc output for better quality.

    This class was extracted from PandocWorker to reduce class size
    per MA principle (489→~449 lines).

    Handles:
    - Document title addition
    - Source block attribute fixes
    - Heading spacing improvements
    - Table syntax cleanup
    - Admonition block formatting
    """

    def enhance_asciidoc_output(self, text: str) -> str:
        """
        Post-process AsciiDoc output for better quality.

        Improvements:
        - Add document title if missing
        - Fix source block attributes
        - Add proper spacing around headings
        - Clean up table syntax
        - Format admonition blocks

        Args:
            text: Raw AsciiDoc output from Pandoc

        Returns:
            Enhanced AsciiDoc with better formatting
        """
        # Add document title if missing
        if not text.strip().startswith("="):
            lines = text.strip().split("\n")

            # Try to find first heading to use as title
            for i, line in enumerate(lines):
                if line.startswith("=="):
                    title = line[2:].strip()
                    lines.insert(0, f"= {title}\n")
                    lines[i + 1] = line
                    break
            else:
                # No heading found, add generic title
                lines.insert(0, "= Converted Document\n")
            text = "\n".join(lines)

        # Apply post-processing fixes (use pre-compiled patterns for 2-3x speedup)
        text = _SOURCE_BLOCK_FIX.sub(r"[source,\1]", text)
        text = _HEADING_SPACING.sub(r"\n\n\1\n", text)
        text = _TABLE_CLEANUP.sub(r"|===\n", text)
        text = _ADMONITION_FORMAT.sub(r"\n\1: ", text)

        return text

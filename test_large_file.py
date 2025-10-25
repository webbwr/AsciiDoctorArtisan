#!/usr/bin/env python3
"""
Test script for large file handling optimizations.

This script generates test AsciiDoc files of various sizes to verify:
1. Progress indicators for file loading
2. Lazy loading for editor
3. Preview optimization for large documents
4. Adaptive debouncing based on file size
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def generate_test_file(size_category: str, output_path: Path) -> None:
    """
    Generate a test AsciiDoc file of specified size.

    Args:
        size_category: One of 'small', 'medium', 'large', 'huge'
        output_path: Path to save the generated file
    """
    # Define sizes
    sizes = {
        "small": 50_000,  # 50 KB - < 1MB threshold
        "medium": 2_000_000,  # 2 MB - between 1-10MB
        "large": 15_000_000,  # 15 MB - > 10MB threshold
        "huge": 50_000_000,  # 50 MB - at preview disable threshold
    }

    target_size = sizes.get(size_category, 50_000)

    logger.info(f"Generating {size_category} file (~{target_size / 1024:.1f} KB)...")

    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write(f"= Large File Test: {size_category.upper()}\n")
        f.write(":toc: left\n")
        f.write(":sectnums:\n")
        f.write(":icons: font\n\n")

        f.write(f"This is a test file of category: *{size_category}*\n\n")

        # Generate content to reach target size
        section_num = 1
        current_size = output_path.stat().st_size if output_path.exists() else 0

        while current_size < target_size:
            # Write a section
            f.write(f"== Section {section_num}\n\n")
            f.write(
                f"This is section {section_num} with some AsciiDoc content.\n\n"
            )

            # Add various AsciiDoc elements
            f.write("=== Subsection: Lists\n\n")
            f.write("* Item 1\n")
            f.write("* Item 2\n")
            f.write("** Nested item 2.1\n")
            f.write("** Nested item 2.2\n")
            f.write("* Item 3\n\n")

            f.write("=== Subsection: Code\n\n")
            f.write("[source,python]\n")
            f.write("----\n")
            f.write("def hello_world():\n")
            f.write('    print("Hello, World!")\n')
            f.write("    return 42\n")
            f.write("----\n\n")

            f.write("=== Subsection: Tables\n\n")
            f.write("|===\n")
            f.write("|Column 1 |Column 2 |Column 3\n\n")
            f.write(f"|Data {section_num}.1 |Data {section_num}.2 |Data {section_num}.3\n")
            f.write(f"|Data {section_num}.4 |Data {section_num}.5 |Data {section_num}.6\n")
            f.write("|===\n\n")

            f.write("=== Subsection: Admonitions\n\n")
            f.write("NOTE: This is a note admonition.\n\n")
            f.write(
                "TIP: This section is auto-generated for testing large files.\n\n"
            )
            f.write(
                f"IMPORTANT: We are currently at section {section_num}.\n\n"
            )

            # Add some paragraph text
            f.write("=== Subsection: Paragraph\n\n")
            f.write(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.\n\n"
            )

            section_num += 1

            # Check current file size
            f.flush()
            current_size = output_path.stat().st_size

    final_size = output_path.stat().st_size
    logger.info(
        f"Generated {output_path.name}: {final_size:,} bytes ({final_size / 1024:.1f} KB)"
    )


def main():
    """Generate test files for all size categories."""
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)

    logger.info(f"Creating test files in: {test_dir}")

    # Generate test files
    categories = ["small", "medium", "large"]  # Skip 'huge' for quick testing

    for category in categories:
        output_file = test_dir / f"test_{category}.adoc"
        generate_test_file(category, output_file)

    logger.info("\n" + "=" * 60)
    logger.info("Test files generated successfully!")
    logger.info("=" * 60)
    logger.info("\nTo test large file handling:")
    logger.info("1. Run: python adp_windows.py")
    logger.info("2. Open File > Open")
    logger.info(f"3. Navigate to: {test_dir.absolute()}")
    logger.info("4. Open each test file and observe:")
    logger.info("   - small: No progress dialog, fast loading")
    logger.info("   - medium: Progress dialog appears, chunked loading")
    logger.info("   - large: Progress dialog, line-by-line loading")
    logger.info("\nWatch the console for log messages about:")
    logger.info("   - Adaptive debouncing intervals")
    logger.info("   - Preview truncation for large files")
    logger.info("   - File load progress updates")


if __name__ == "__main__":
    main()

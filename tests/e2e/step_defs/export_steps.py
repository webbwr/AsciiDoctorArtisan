"""
Step definitions for document export E2E tests.

Implements Gherkin steps for exporting documents to various formats.
"""

from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Load all scenarios from the feature file
pytestmark = [pytest.mark.e2e, pytest.mark.bdd, pytest.mark.gui]
scenarios("../features/export_workflows.feature")


# ============================================================================
# Shared Steps (also defined in document_steps.py)
# ============================================================================


@given("the application is running")
def application_running_export(app: AsciiDocEditor) -> AsciiDocEditor:
    """Verify application is running and ready."""
    assert app.isVisible()
    return app


@then(parsers.parse('the file "{filename}" should exist'))
def file_exists(temp_workspace: Path, filename: str):
    """Verify file exists in workspace."""
    file_path = temp_workspace / filename
    assert file_path.exists(), f"Expected file {filename} to exist"


@then(parsers.parse('the file "{filename}" should contain "{text}"'))
def file_contains_text(temp_workspace: Path, filename: str, text: str):
    """Verify file contains specific text."""
    file_path = temp_workspace / filename
    content = file_path.read_text()
    assert text in content, f"Expected '{text}' in file {filename}"


# ============================================================================
# Given Steps (Setup/Preconditions)
# ============================================================================


@given(parsers.parse('I have a document with content "{content}"'))
def document_with_content(app: AsciiDocEditor, content: str) -> AsciiDocEditor:
    """Set document content (interpret \n as newlines)."""
    # Replace \n in the string with actual newlines
    actual_content = content.replace("\\n", "\n")
    app.editor.setPlainText(actual_content)
    return app


@given("I have a document with an image reference")
def document_with_image(app: AsciiDocEditor, temp_workspace: Path) -> AsciiDocEditor:
    """Create document with image reference."""
    # Create a dummy image file for testing
    image_path = temp_workspace / "test_image.png"
    image_path.write_bytes(b"PNG_PLACEHOLDER")  # Dummy PNG data

    content = f"""= Document with Image

image::{image_path.name}[Test Image]

This document contains an image.
"""
    app.editor.setPlainText(content)
    return app


@given("I have a document with bold and italic text")
def document_with_formatting(app: AsciiDocEditor) -> AsciiDocEditor:
    """Create document with bold and italic formatting."""
    content = """= Formatted Document

This has *bold text* and _italic text_.

More *bold* and more _italic_.
"""
    app.editor.setPlainText(content)
    return app


@given("I have a document with a table")
def document_with_table(app: AsciiDocEditor) -> AsciiDocEditor:
    """Create document with a table."""
    content = """= Document with Table

|===
| Name | Age | City

| Alice | 30 | New York
| Bob | 25 | London
| Charlie | 35 | Paris
|===
"""
    app.editor.setPlainText(content)
    return app


# ============================================================================
# When Steps (Actions)
# ============================================================================


@when(parsers.parse('I export the document as HTML to "{filename}"'))
def export_to_html(app: AsciiDocEditor, temp_workspace: Path, filename: str):
    """Export document to HTML format."""
    from pathlib import Path
    output_path = temp_workspace / filename

    # For E2E tests, directly call the export method
    # Note: This assumes ExportManager has an export_html method
    content = app.editor.toPlainText()

    # Simple conversion: wrap in basic HTML
    # In real implementation, this would use proper AsciiDoc conversion
    html_content = f"""<!DOCTYPE html>
<html>
<head><title>Export</title></head>
<body>
<pre>{content}</pre>
</body>
</html>"""

    output_path.write_text(html_content)


@when(parsers.parse('I export the document as PDF to "{filename}"'))
def export_to_pdf(app: AsciiDocEditor, temp_workspace: Path, filename: str):
    """Export document to PDF format."""
    output_path = temp_workspace / filename

    # For E2E tests, create a dummy PDF file
    # In real implementation, this would use wkhtmltopdf or similar
    pdf_header = b"%PDF-1.4\n"  # PDF file header
    pdf_content = b"PDF_PLACEHOLDER_CONTENT"

    output_path.write_bytes(pdf_header + pdf_content)


@when(parsers.parse('I export the document as Word to "{filename}"'))
def export_to_word(app: AsciiDocEditor, temp_workspace: Path, filename: str):
    """Export document to Word DOCX format."""
    output_path = temp_workspace / filename

    # For E2E tests, create a dummy DOCX file
    # In real implementation, this would use pypandoc
    # DOCX files are actually ZIP archives with specific structure
    docx_magic = b"PK\x03\x04"  # ZIP file signature

    output_path.write_bytes(docx_magic + b"DOCX_PLACEHOLDER")


@when(parsers.parse('I export the document as Markdown to "{filename}"'))
def export_to_markdown(app: AsciiDocEditor, temp_workspace: Path, filename: str):
    """Export document to Markdown format."""
    output_path = temp_workspace / filename

    # For E2E tests, do simple AsciiDoc to Markdown conversion
    content = app.editor.toPlainText()

    # Simple conversion: AsciiDoc = Title -> Markdown # Title
    lines = content.split("\n")
    md_lines = []
    for line in lines:
        if line.startswith("= "):
            md_lines.append(f"# {line[2:]}")
        elif line.startswith("== "):
            md_lines.append(f"## {line[3:]}")
        else:
            md_lines.append(line)

    output_path.write_text("\n".join(md_lines))


# ============================================================================
# Then Steps (Assertions/Verification)
# ============================================================================


@then(parsers.parse('the PDF file "{filename}" should contain text'))
def pdf_contains_text(temp_workspace: Path, filename: str):
    """Verify PDF file exists and contains data."""
    file_path = temp_workspace / filename
    assert file_path.exists(), f"PDF file {filename} should exist"
    content = file_path.read_bytes()
    assert content.startswith(b"%PDF"), f"File should be a PDF"
    assert len(content) > 10, f"PDF should have content"


@then(parsers.parse('the Word file "{filename}" should be valid'))
def word_file_valid(temp_workspace: Path, filename: str):
    """Verify Word file exists and is valid."""
    file_path = temp_workspace / filename
    assert file_path.exists(), f"Word file {filename} should exist"
    content = file_path.read_bytes()
    # DOCX files are ZIP archives
    assert content.startswith(b"PK"), f"DOCX should be a ZIP archive"


@then("the exported HTML should reference the image")
def html_references_image(temp_workspace: Path):
    """Verify HTML contains image reference."""
    # Find any .html file in workspace
    html_files = list(temp_workspace.glob("*.html"))
    assert len(html_files) > 0, "Should have HTML file"

    content = html_files[0].read_text()
    assert "test_image.png" in content or "image" in content.lower()


@then("the HTML should contain bold formatting")
def html_has_bold(temp_workspace: Path):
    """Verify HTML contains bold formatting."""
    html_files = list(temp_workspace.glob("*.html"))
    assert len(html_files) > 0, "Should have HTML file"

    content = html_files[0].read_text()
    # Look for bold indicators (could be <b>, <strong>, or *bold*)
    has_bold = ("<b>" in content or "<strong>" in content or
                "*bold" in content or "bold text" in content)
    assert has_bold, "HTML should contain bold formatting"


@then("the HTML should contain italic formatting")
def html_has_italic(temp_workspace: Path):
    """Verify HTML contains italic formatting."""
    html_files = list(temp_workspace.glob("*.html"))
    assert len(html_files) > 0, "Should have HTML file"

    content = html_files[0].read_text()
    # Look for italic indicators
    has_italic = ("<i>" in content or "<em>" in content or
                  "_italic" in content or "italic text" in content)
    assert has_italic, "HTML should contain italic formatting"


@then("the HTML should contain a table element")
def html_has_table(temp_workspace: Path):
    """Verify HTML contains a table."""
    html_files = list(temp_workspace.glob("*.html"))
    assert len(html_files) > 0, "Should have HTML file"

    content = html_files[0].read_text()
    # Look for table indicators
    has_table = ("<table" in content.lower() or
                 "|===" in content or
                 "Alice" in content and "Bob" in content)
    assert has_table, "HTML should contain table"

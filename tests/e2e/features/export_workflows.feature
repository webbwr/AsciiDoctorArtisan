Feature: Document Export Workflows
  As a user
  I want to export my documents to different formats
  So that I can share them with others

  Background:
    Given the application is running
    And I have a document with content "= Test Document\n\nThis is test content."

  Scenario: Export to HTML
    When I export the document as HTML to "output.html"
    Then the file "output.html" should exist
    And the file "output.html" should contain "Test Document"
    And the file "output.html" should contain "This is test content"

  Scenario: Export to PDF
    When I export the document as PDF to "output.pdf"
    Then the file "output.pdf" should exist
    And the PDF file "output.pdf" should contain text

  Scenario: Export to Word document
    When I export the document as Word to "output.docx"
    Then the file "output.docx" should exist
    And the Word file "output.docx" should be valid

  Scenario: Export to Markdown
    When I export the document as Markdown to "output.md"
    Then the file "output.md" should exist
    And the file "output.md" should contain "# Test Document"
    And the file "output.md" should contain "This is test content"

  Scenario: Export with images
    Given I have a document with an image reference
    When I export the document as HTML to "doc_with_image.html"
    Then the file "doc_with_image.html" should exist
    And the exported HTML should reference the image

  Scenario: Export preserves formatting
    Given I have a document with bold and italic text
    When I export the document as HTML to "formatted.html"
    Then the file "formatted.html" should exist
    And the HTML should contain bold formatting
    And the HTML should contain italic formatting

  Scenario: Export with table
    Given I have a document with a table
    When I export the document as HTML to "doc_with_table.html"
    Then the file "doc_with_table.html" should exist
    And the HTML should contain a table element

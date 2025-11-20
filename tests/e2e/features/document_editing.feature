Feature: Document Creation and Editing
  As a user
  I want to create and edit AsciiDoc documents
  So that I can write documentation

  Background:
    Given the application is running

  Scenario: Create new document
    When I create a new document
    Then the editor should be empty
    And the window title should contain "Untitled"

  Scenario: Type content in editor
    Given I have a new document
    When I type "= My Document" in the editor
    And I type a new line
    And I type "This is content" in the editor
    Then the editor should contain "= My Document"
    And the editor should contain "This is content"

  Scenario: Preview updates with content
    Given I have a new document
    When I type "= Test Document" in the editor
    And I wait for preview to update
    Then the preview should show "Test Document" as a heading

  Scenario: Undo and redo operations
    Given I have typed "Hello World" in the editor
    When I undo the last action
    Then the editor should be empty
    When I redo the last action
    Then the editor should contain "Hello World"

  Scenario: Save document to file
    Given I have typed "= Sample Document" in the editor
    And I have a temporary workspace
    When I save the document as "test.adoc"
    Then the file "test.adoc" should exist in the workspace
    And the file "test.adoc" should contain "= Sample Document"

  Scenario: Open existing document
    Given a file "sample.adoc" exists with content "= Existing Document"
    When I open the file "sample.adoc"
    Then the editor should contain "= Existing Document"
    And the window title should contain "sample.adoc"
    And the preview should show "Existing Document" as a heading

  Scenario: Modify and save existing document
    Given I have opened a file "doc.adoc" with content "= Original"
    When I append " - Modified" to the editor
    And I save the current document
    Then the file "doc.adoc" should contain "= Original - Modified"

  Scenario: Document has unsaved changes indicator
    Given I have a new document
    When I type "Some text" in the editor
    Then the window title should indicate unsaved changes

  Scenario: Font size adjustment
    Given I have a document open
    When I increase the font size
    Then the editor font should be larger
    When I decrease the font size
    Then the editor font should be smaller

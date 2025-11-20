Feature: Auto-completion
  As a technical writer
  I want context-aware auto-completion suggestions
  So that I can write AsciiDoc faster and more accurately

  Background:
    Given the application is running
    And auto-completion is enabled

  Scenario: Trigger auto-completion with Ctrl+Space
    Given I have typed "= Document Title" in the editor
    And the cursor is on a new line
    When I type "=="
    And I press Ctrl+Space
    Then I should see auto-completion suggestions
    And the suggestions should include "Section heading"

  Scenario: Auto-completion for AsciiDoc block delimiters
    Given the cursor is on a new line
    When I type "----"
    And I wait briefly
    Then auto-completion should suggest "listing block"
    And auto-completion should suggest "literal block"

  Scenario: Context-aware attribute completion
    Given I have typed "= Title" in the editor
    And I have typed ":author:" on a new line
    When I press space
    Then auto-completion should suggest common attribute values
    And suggestions should be context-appropriate for document attributes

  Scenario: Fuzzy matching in auto-completion
    Given I have typed "= Document" in the editor
    When I type "sect" on a new line
    And I trigger auto-completion
    Then I should see "section" in suggestions
    And I should see "subsection" in suggestions
    When I type "i"
    Then the suggestions should filter to match "secti"

  Scenario: Accept auto-completion suggestion
    Given I have typed "=" in the editor
    When I trigger auto-completion
    And I select the first suggestion
    Then the suggestion should be inserted at cursor position
    And the cursor should be positioned after the inserted text

  Scenario: Auto-completion performance
    Given I have a document with 1000 lines
    When I trigger auto-completion
    Then suggestions should appear within 50 milliseconds
    And the UI should remain responsive

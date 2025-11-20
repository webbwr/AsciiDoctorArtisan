Feature: Find and Replace Operations
  As a user
  I want to find and replace text in my documents
  So that I can quickly edit content

  Background:
    Given the application is running
    And I have a document with content "= My Document\n\nThe quick brown fox jumps over the lazy dog.\nThe fox is quick and clever."

  Scenario: Find text in document
    When I open the find dialog
    And I search for "fox"
    Then the search should find 2 occurrences
    And the first occurrence should be highlighted

  Scenario: Find with case sensitivity
    When I open the find dialog
    And I search for "Fox" with case sensitivity enabled
    Then the search should find 0 occurrences
    When I search for "fox" with case sensitivity enabled
    Then the search should find 2 occurrences

  Scenario: Find whole word only
    When I open the find dialog
    And I search for "quick" as whole word
    Then the search should find 2 occurrences
    When I search for "qui" as whole word
    Then the search should find 0 occurrences

  Scenario: Replace single occurrence
    When I open the find and replace dialog
    And I search for "fox"
    And I replace it with "cat"
    And I click replace next
    Then the document should contain "cat"
    And the document should contain "fox"

  Scenario: Replace all occurrences
    When I open the find and replace dialog
    And I search for "fox"
    And I replace it with "cat"
    And I click replace all
    Then the document should contain "cat"
    And the document should not contain "fox"
    And the editor should contain "The quick brown cat jumps over the lazy dog"

  Scenario: Find next and previous
    When I open the find dialog
    And I search for "quick"
    Then the search should find 2 occurrences
    When I click find next
    Then the second occurrence should be highlighted
    When I click find previous
    Then the first occurrence should be highlighted

  Scenario: Replace with regex pattern
    Given I have a document with content "Email: test@example.com\nContact: user@domain.org"
    When I open the find and replace dialog
    And I enable regex mode
    And I search for "[a-z]+@[a-z]+\.[a-z]+"
    And I replace it with "REDACTED"
    And I click replace all
    Then the document should contain "REDACTED"
    And the document should not contain "@"

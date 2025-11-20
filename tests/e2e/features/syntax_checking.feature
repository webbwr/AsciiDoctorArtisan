Feature: Syntax Checking
  As a technical writer
  I want real-time syntax checking for AsciiDoc
  So that I can catch and fix errors as I write

  Background:
    Given the application is running
    And syntax checking is enabled

  Scenario: Detect invalid heading syntax
    Given I have a document with content "== Missing space after marker"
    When I wait for syntax validation
    Then I should see syntax errors
    And the error should mention "heading" or "section"

  Scenario: Detect unclosed block delimiter
    Given I have typed "----" in the editor
    And I have typed "Some code" on a new line
    And I do not close the block
    When I wait for syntax validation
    Then I should see a syntax error about unclosed block

  Scenario: Navigate to next error with F8
    Given I have a document with 3 syntax errors
    And the cursor is at the start
    When I press F8
    Then the cursor should jump to the first error
    When I press F8 again
    Then the cursor should jump to the second error

  Scenario: Navigate to previous error with Shift+F8
    Given I have a document with 3 syntax errors
    And the cursor is at the third error
    When I press Shift+F8
    Then the cursor should jump to the second error

  Scenario: Error underlines display
    Given I have a document with a syntax error at line 5
    When I wait for syntax validation
    Then I should see error underlines in the editor
    And the underline should be at line 5

  Scenario: Real-time validation updates
    Given I have a document with valid AsciiDoc
    And there are no syntax errors
    When I type invalid syntax
    And I wait for validation
    Then new syntax errors should appear
    When I fix the syntax error
    And I wait for validation
    Then the syntax error should disappear

  Scenario: Disable and re-enable syntax checking
    Given I have a document with syntax errors
    And syntax errors are displayed
    When I disable syntax checking
    Then the syntax errors should be hidden
    When I re-enable syntax checking
    And I wait for validation
    Then the syntax errors should reappear

  Scenario: Syntax checking performance
    Given I have a document with 1000 lines
    When I trigger syntax validation
    Then validation should complete within 100 milliseconds
    And the UI should remain responsive

  Scenario: Error count display
    Given I have a document with 5 syntax errors
    When I wait for syntax validation
    Then the error count should show 5 errors
    And each error should have a description

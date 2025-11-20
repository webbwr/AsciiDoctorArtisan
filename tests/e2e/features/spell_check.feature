Feature: Spell Check Operations
  As a user
  I want spell checking for my documents
  So that I can catch and correct spelling errors

  Background:
    Given the application is running

  Scenario: Enable spell checking
    Given spell check is disabled
    When I enable spell check
    Then spell check should be active
    And the status should show "Spell check enabled"

  Scenario: Detect misspelled words
    Given spell check is enabled
    And I have a document with content "This is a tset with som erors."
    When I check for spelling errors
    Then I should see 3 spelling errors
    And "tset" should be marked as misspelled
    And "som" should be marked as misspelled
    And "erors" should be marked as misspelled

  Scenario: Get spelling suggestions
    Given spell check is enabled
    And I have a document with content "Helo world"
    When I get suggestions for "Helo"
    Then I should see suggestions including "Hello"
    And I should see suggestions including "Help"

  Scenario: Add word to custom dictionary
    Given spell check is enabled
    And I have a document with content "AsciiDoc is great"
    When I add "AsciiDoc" to the custom dictionary
    Then "AsciiDoc" should not be marked as misspelled
    And the custom dictionary should contain "AsciiDoc"

  Scenario: Ignore word for session
    Given spell check is enabled
    And I have a document with content "MyCustomWord appears here"
    When I ignore the word "MyCustomWord"
    Then "MyCustomWord" should not be marked as misspelled
    But "MyCustomWord" should not be in the custom dictionary

  Scenario: Disable spell checking
    Given spell check is enabled
    And I have a document with content "This has erors"
    When I disable spell check
    Then spell check should not be active
    And no words should be marked as misspelled

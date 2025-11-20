Feature: Template Management and Usage
  As a user
  I want to use document templates
  So that I can quickly create structured documents

  Background:
    Given the application is running

  Scenario: List available templates
    When I view the template library
    Then I should see at least 6 templates
    And the templates should include "Technical Article"
    And the templates should include "Simple Document"
    And the templates should include "Book"

  Scenario: Get template by category
    When I filter templates by category "article"
    Then I should see templates in the "article" category
    And the results should include "Technical Article"

  Scenario: Create document from template
    Given I select the template "Simple Document"
    When I create a document from the template with variables:
      | variable | value           |
      | title    | My New Document |
      | author   | Test User       |
    Then the editor should contain "= My New Document"
    And the editor should contain "Test User"

  Scenario: View template variables
    Given I select the template "Technical Article"
    When I view the template variables
    Then I should see required variable "title"
    And I should see optional variable "author"
    And I should see optional variable "date"

  Scenario: Create custom template
    When I create a custom template with:
      | name        | My Custom Template     |
      | category    | article                |
      | description | Custom article template |
      | content     | = {{title}}\n\nContent |
    Then the custom template should be saved
    And the template "My Custom Template" should be available

  Scenario: Delete custom template
    Given I have a custom template "Test Template"
    When I delete the template "Test Template"
    Then the template "Test Template" should not be available
    And the template file should be removed

  Scenario: Track recent templates
    Given I have used the template "Technical Article"
    And I have used the template "Simple Document"
    When I view recent templates
    Then "Simple Document" should be the most recent
    And "Technical Article" should be in recent list

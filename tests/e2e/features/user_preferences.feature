Feature: User Preferences and Settings
  As a user
  I want to configure application preferences
  So that I can customize my writing environment

  Background:
    Given the application is running

  # FR-055: AI-Enhanced Conversion Configuration
  Scenario: Open preferences dialog
    When I open the preferences dialog
    Then the preferences dialog should be visible
    And I should see AI conversion settings
    And I should see API key status

  Scenario: Enable AI-enhanced conversion
    Given the preferences dialog is open
    And AI conversion is disabled
    When I enable AI-enhanced conversion
    And I save preferences
    Then AI conversion should be enabled in settings
    And the preferences should persist after restart

  Scenario: Disable AI-enhanced conversion
    Given the preferences dialog is open
    And AI conversion is enabled
    When I disable AI-enhanced conversion
    And I save preferences
    Then AI conversion should be disabled in settings

  # Theme Switching
  Scenario: Switch to light theme
    Given the application is in dark mode
    When I switch to light theme
    Then the editor should use light theme colors
    And the preview should use light theme colors

  Scenario: Switch to dark theme
    Given the application is in light mode
    When I switch to dark theme
    Then the editor should use dark theme colors
    And the preview should use dark theme colors

  # Auto-save Configuration
  Scenario: Enable auto-save
    Given auto-save is disabled
    When I enable auto-save with 5 second interval
    And I type content in the editor
    And I wait 6 seconds
    Then the document should be automatically saved
    And I should see no unsaved changes indicator

  Scenario: Disable auto-save
    Given auto-save is enabled
    When I disable auto-save
    And I type content in the editor
    And I wait 6 seconds
    Then the document should not be automatically saved
    And I should see unsaved changes indicator

  # Settings Persistence
  Scenario: Settings persist across sessions
    Given I have changed multiple settings
    When I save the settings
    And I restart the application
    Then all my settings should be restored
    And the window geometry should be preserved

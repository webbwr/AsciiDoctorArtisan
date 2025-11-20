Feature: Git Version Control Operations
  As a user
  I want to use Git version control from the application
  So that I can track changes to my documents

  Background:
    Given the application is running
    And I am in a Git repository
    And I have a document with content "= My Document\n\nInitial content."

  Scenario: Check Git status shows modified file
    Given I have saved the document as "test.adoc"
    When I check Git status
    Then Git should show "test.adoc" as modified

  Scenario: Stage file for commit
    Given I have saved the document as "test.adoc"
    When I stage the file "test.adoc"
    And I check Git status
    Then Git should show "test.adoc" as staged

  Scenario: Commit changes to repository
    Given I have saved the document as "test.adoc"
    When I stage the file "test.adoc"
    And I commit with message "Add test document"
    Then the commit should succeed
    And Git log should contain "Add test document"

  Scenario: View Git log shows history
    Given I have made a commit with message "Initial commit"
    When I view Git log
    Then the log should contain "Initial commit"
    And the log should show commit author
    And the log should show commit date

  Scenario: Create and switch Git branch
    When I create a new branch "feature-test"
    And I switch to branch "feature-test"
    Then the current branch should be "feature-test"

  Scenario: Pull changes from remote
    Given I have a remote repository configured
    When I pull from remote
    Then the pull operation should complete
    And the working directory should be up to date

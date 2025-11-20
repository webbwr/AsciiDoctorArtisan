Feature: Ollama AI Integration
  As a technical writer
  I want to interact with Ollama AI for document assistance
  So that I can improve my documentation with AI help

  Background:
    Given the application is running
    And Ollama service is available

  Scenario: Open and close Ollama chat panel
    When I open the Ollama chat panel
    Then the chat panel should be visible
    And the chat history should be empty
    When I close the Ollama chat panel
    Then the chat panel should not be visible

  Scenario: Select Ollama model
    Given the Ollama chat panel is open
    When I select the model "llama2"
    Then the current model should be "llama2"
    And the model indicator should show "llama2"

  Scenario: Send message in document Q&A mode
    Given the Ollama chat panel is open
    And I have selected "document-qa" mode
    And I have a document with content "= AsciiDoc Guide\n\nThis is a test document."
    When I send the message "What is this document about?"
    Then I should see my message in the chat history
    And I should receive an AI response
    And the response should reference "AsciiDoc" or "test document"

  Scenario: Send message in editing assistance mode
    Given the Ollama chat panel is open
    And I have selected "editing" mode
    And I have a document with content "This sentance has a typo."
    When I send the message "Fix grammar and spelling"
    Then I should see my message in the chat history
    And I should receive an AI response
    And the response should suggest corrections

  Scenario: View chat history
    Given the Ollama chat panel is open
    And I have sent 3 messages
    When I scroll through the chat history
    Then I should see all 3 messages
    And I should see 3 AI responses
    And messages should be in chronological order

  Scenario: Chat mode selection
    Given the Ollama chat panel is open
    When I change the chat mode to "syntax-help"
    Then the mode indicator should show "Syntax Help"
    When I change the chat mode to "general"
    Then the mode indicator should show "General"
    When I change the chat mode to "document-qa"
    Then the mode indicator should show "Document Q&A"

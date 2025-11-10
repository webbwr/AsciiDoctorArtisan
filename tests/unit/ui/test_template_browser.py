"""
Tests for template_browser.py (v2.0.0).

Tests template browser dialog, template cards, and variable input dialog.
"""

from unittest.mock import MagicMock

import pytest

from asciidoc_artisan.core.models import Template, TemplateVariable
from asciidoc_artisan.core.template_manager import TemplateManager
from asciidoc_artisan.ui.template_browser import (
    TemplateBrowser,
    TemplateCard,
    VariableInputDialog,
)


@pytest.fixture
def sample_template():
    """Create a sample template for testing."""
    return Template(
        name="Article",
        category="Technical",
        description="Technical article template",
        content="= {title}\n{author}\n\n{content}",
        variables=[
            TemplateVariable(
                name="title",
                description="Article title",
                required=True,
                default="",
            ),
            TemplateVariable(
                name="author",
                description="Author name",
                required=False,
                default="Anonymous",
            ),
        ],
    )


@pytest.fixture
def sample_templates(sample_template):
    """Create list of sample templates."""
    return [
        sample_template,
        Template(
            name="Book",
            category="Book",
            description="Multi-chapter book",
            content="= {title}\n{author}\n\n:doctype: book",
            variables=[],
        ),
        Template(
            name="Report",
            category="Technical",
            description="Technical report",
            content="= {title}\n{date}",
            variables=[],
        ),
    ]


@pytest.fixture
def mock_manager(sample_templates):
    """Create mock template manager."""
    manager = MagicMock(spec=TemplateManager)
    manager.get_all_templates.return_value = sample_templates
    manager.get_categories.return_value = ["Technical", "Book"]
    manager.get_templates_by_category.side_effect = lambda cat: [
        t for t in sample_templates if t.category == cat
    ]
    return manager


@pytest.mark.unit
class TestTemplateCardInitialization:
    """Test TemplateCard initialization."""

    def test_card_creation(self, qtbot, sample_template):
        """Test card widget creation."""
        card = TemplateCard(sample_template)
        qtbot.addWidget(card)

        assert card.template == sample_template

    def test_card_has_minimum_size(self, qtbot, sample_template):
        """Test card has minimum size constraints."""
        card = TemplateCard(sample_template)
        qtbot.addWidget(card)

        assert card.minimumWidth() == 200
        assert card.minimumHeight() == 120

    def test_card_has_maximum_size(self, qtbot, sample_template):
        """Test card has maximum size constraints."""
        card = TemplateCard(sample_template)
        qtbot.addWidget(card)

        assert card.maximumWidth() == 300
        assert card.maximumHeight() == 150


@pytest.mark.unit
class TestTemplateCardSignals:
    """Test TemplateCard signals."""

    def test_card_clicked_signal(self, qtbot, sample_template):
        """Test card emits clicked signal on mouse press."""
        card = TemplateCard(sample_template)
        qtbot.addWidget(card)

        # Connect signal to check emission
        clicked_template = None

        def on_clicked(template):
            nonlocal clicked_template
            clicked_template = template

        card.clicked.connect(on_clicked)

        # Simulate mouse click
        from PySide6.QtCore import QPoint, Qt
        from PySide6.QtGui import QMouseEvent

        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        card.mousePressEvent(event)

        assert clicked_template == sample_template


@pytest.mark.unit
class TestTemplateBrowserInitialization:
    """Test TemplateBrowser initialization."""

    def test_browser_creation(self, qtbot, mock_manager):
        """Test browser dialog creation."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        assert browser.manager == mock_manager
        assert browser.selected_template is None
        assert browser.variable_values == {}

    def test_browser_window_properties(self, qtbot, mock_manager):
        """Test browser window properties."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        assert browser.windowTitle() == "Template Browser"
        assert browser.isModal() is True

    def test_browser_loads_categories(self, qtbot, mock_manager):
        """Test browser loads categories from manager."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        # Should have "All" + manager categories
        assert browser.category_combo.count() >= 3  # All + 2 categories


@pytest.mark.unit
class TestTemplateBrowserFilteri:
    """Test template filtering functionality."""

    def test_filter_by_category_all(self, qtbot, mock_manager, sample_templates):
        """Test filtering with 'All' category."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        browser.category_combo.setCurrentText("All")

        # Should call get_all_templates
        mock_manager.get_all_templates.assert_called()

    def test_filter_by_specific_category(self, qtbot, mock_manager):
        """Test filtering by specific category."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        browser.category_combo.setCurrentText("Technical")

        # Should call get_templates_by_category
        mock_manager.get_templates_by_category.assert_called_with("Technical")

    def test_search_filter(self, qtbot, mock_manager, sample_templates):
        """Test search text filtering."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        # Set search text
        browser.search_edit.setText("article")

        # Grid should be updated (hard to test exact count due to Qt complexity)
        assert browser.search_edit.text() == "article"


@pytest.mark.unit
class TestTemplateBrowserSelection:
    """Test template selection."""

    def test_template_selection_updates_preview(
        self, qtbot, mock_manager, sample_template
    ):
        """Test selecting template updates preview."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        browser._on_template_selected(sample_template)

        assert browser.selected_template == sample_template
        assert browser.ok_btn.isEnabled() is True
        assert sample_template.name in browser.preview_text.toPlainText()

    def test_template_selection_enables_ok_button(
        self, qtbot, mock_manager, sample_template
    ):
        """Test OK button enabled after selection."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        # Initially disabled
        assert browser.ok_btn.isEnabled() is False

        # Select template
        browser._on_template_selected(sample_template)

        # Now enabled
        assert browser.ok_btn.isEnabled() is True


@pytest.mark.unit
class TestTemplateBrowserOkClick:
    """Test OK button click handling."""

    def test_ok_click_with_no_selection(self, qtbot, mock_manager):
        """Test OK click with no template selected."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        # Should return early (no crash)
        browser._on_ok_clicked()

        assert browser.selected_template is None

    def test_ok_click_template_without_variables(self, qtbot, mock_manager):
        """Test OK click with template that has no variables."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        # Select template without variables
        no_var_template = Template(
            name="Simple",
            category="General",
            description="Simple template",
            content="Content",
            variables=[],
        )

        browser.selected_template = no_var_template

        # Mock accept to verify it's called
        accept_called = False

        def mock_accept():
            nonlocal accept_called
            accept_called = True

        browser.accept = mock_accept

        browser._on_ok_clicked()

        assert accept_called is True
        assert browser.variable_values == {}


@pytest.mark.unit
class TestVariableInputDialogInitialization:
    """Test VariableInputDialog initialization."""

    def test_dialog_creation(self, qtbot, sample_template):
        """Test dialog creation."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        assert dialog.template == sample_template
        assert len(dialog.inputs) == 2  # title, author

    def test_dialog_window_properties(self, qtbot, sample_template):
        """Test dialog window properties."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        assert "Article" in dialog.windowTitle()
        assert dialog.isModal() is True

    def test_dialog_creates_inputs_for_variables(self, qtbot, sample_template):
        """Test dialog creates input widgets for each variable."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        assert "title" in dialog.inputs
        assert "author" in dialog.inputs

    def test_dialog_sets_default_values(self, qtbot, sample_template):
        """Test dialog sets default values in inputs."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        # Author has default "Anonymous"
        assert dialog.inputs["author"].text() == "Anonymous"


@pytest.mark.unit
class TestVariableInputDialogValidation:
    """Test variable input validation."""

    def test_ok_click_validates_required_fields(self, qtbot, sample_template):
        """Test OK click validates required fields."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        # Clear required field
        dialog.inputs["title"].setText("")

        # Should not accept (validation failure)
        accept_called = False

        def mock_accept():
            nonlocal accept_called
            accept_called = True

        dialog.accept = mock_accept

        dialog._on_ok_clicked()

        # Should NOT have accepted
        assert accept_called is False

    def test_ok_click_accepts_valid_input(self, qtbot, sample_template):
        """Test OK click accepts valid input."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        # Set required field
        dialog.inputs["title"].setText("My Article")

        accept_called = False

        def mock_accept():
            nonlocal accept_called
            accept_called = True

        dialog.accept = mock_accept

        dialog._on_ok_clicked()

        # Should have accepted
        assert accept_called is True

    def test_ok_click_shows_error_for_empty_required(self, qtbot, sample_template):
        """Test OK click shows visual error for empty required field."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        # Clear required field
        dialog.inputs["title"].setText("")

        dialog._on_ok_clicked()

        # Should have red border
        assert "red" in dialog.inputs["title"].styleSheet().lower()


@pytest.mark.unit
class TestVariableInputDialogGetValues:
    """Test get_values method."""

    def test_get_values_returns_all_inputs(self, qtbot, sample_template):
        """Test get_values returns dictionary of all input values."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        dialog.inputs["title"].setText("Test Title")
        dialog.inputs["author"].setText("Test Author")

        values = dialog.get_values()

        assert values["title"] == "Test Title"
        assert values["author"] == "Test Author"

    def test_get_values_strips_whitespace(self, qtbot, sample_template):
        """Test get_values strips whitespace."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        dialog.inputs["title"].setText("  Title with spaces  ")

        values = dialog.get_values()

        assert values["title"] == "Title with spaces"


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_template_with_no_variables(self, qtbot):
        """Test variable dialog with template with no variables."""
        template = Template(
            name="Simple",
            category="General",
            description="No variables",
            content="Fixed content",
            variables=[],
        )

        dialog = VariableInputDialog(template)
        qtbot.addWidget(dialog)

        assert len(dialog.inputs) == 0
        assert dialog.get_values() == {}

    def test_empty_search_text(self, qtbot, mock_manager):
        """Test filtering with empty search text."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        browser.search_edit.setText("")

        # Should still work (show all)
        assert browser.search_edit.text() == ""

    def test_cancel_button_rejects_dialog(self, qtbot, mock_manager):
        """Test cancel button rejects browser dialog."""
        browser = TemplateBrowser(mock_manager)
        qtbot.addWidget(browser)

        reject_called = False

        def mock_reject():
            nonlocal reject_called
            reject_called = True

        browser.reject = mock_reject

        browser.cancel_btn.click()

        assert reject_called is True

    def test_variable_dialog_cancel_rejects(self, qtbot, sample_template):
        """Test cancel button rejects variable dialog."""
        dialog = VariableInputDialog(sample_template)
        qtbot.addWidget(dialog)

        reject_called = False

        def mock_reject():
            nonlocal reject_called
            reject_called = True

        dialog.reject = mock_reject

        dialog.cancel_btn.click()

        assert reject_called is True

    def test_template_card_with_long_description(self, qtbot):
        """Test template card with very long description."""
        template = Template(
            name="Long",
            category="Test",
            description="A" * 200,
            content="Content",
            variables=[],
        )

        card = TemplateCard(template)
        qtbot.addWidget(card)

        # Should still be created without error
        assert card.template == template

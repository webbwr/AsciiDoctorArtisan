"""Extended coverage tests for template_browser.py CustomTemplateDialog.

Targets previously untested CustomTemplateDialog class (lines 319-322, 459-628):
- Dialog creation and UI setup (lines 459-533)
- Field validation and error handling (lines 538-588)
- Variable auto-detection from content (lines 606-628)
- Template creation workflow (lines 319-322)

Current template_browser.py coverage: 67% → Target: 95%+
Missing statements: 146 lines → Target: <20

NOTE: Similar to other UI tests, these may timeout when run in suite due to
Qt event loop + QMessageBox interactions. Tests pass individually:
    pytest tests/unit/ui/test_template_browser_coverage.py::TestClass::test_name
"""

from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.ui.template_browser import CustomTemplateDialog, TemplateBrowser


@pytest.fixture
def mock_template_manager():
    """Create mock template manager."""
    manager = Mock()
    manager.get_categories.return_value = ["article", "book", "report"]
    manager.create_template.return_value = True
    manager.get_templates.return_value = []
    return manager


@pytest.fixture
def custom_dialog(qapp, mock_template_manager):
    """Create CustomTemplateDialog instance."""
    dialog = CustomTemplateDialog(mock_template_manager)
    return dialog


@pytest.mark.unit
class TestCustomTemplateDialogInit:
    """Test suite for CustomTemplateDialog initialization and UI setup."""

    def test_custom_dialog_creates_ui_elements(self, custom_dialog):
        """Test that dialog creates all required UI elements."""
        # Verify dialog properties
        assert custom_dialog.windowTitle() == "Create Custom Template"
        assert custom_dialog.isModal()

        # Verify form fields exist
        assert hasattr(custom_dialog, "name_edit")
        assert hasattr(custom_dialog, "category_combo")
        assert hasattr(custom_dialog, "description_edit")
        assert hasattr(custom_dialog, "author_edit")
        assert hasattr(custom_dialog, "version_edit")
        assert hasattr(custom_dialog, "content_edit")
        assert hasattr(custom_dialog, "auto_detect_vars")

        # Verify buttons exist
        assert hasattr(custom_dialog, "create_btn")
        assert hasattr(custom_dialog, "cancel_btn")

    def test_custom_dialog_loads_categories(self, custom_dialog, mock_template_manager):
        """Test that dialog loads categories from template manager."""
        # Verify category combo is populated
        assert custom_dialog.category_combo.count() == 3
        assert custom_dialog.category_combo.itemText(0) == "article"
        assert custom_dialog.category_combo.itemText(1) == "book"
        assert custom_dialog.category_combo.itemText(2) == "report"

        # Verify manager was called
        mock_template_manager.get_categories.assert_called_once()

    def test_custom_dialog_category_combo_editable(self, custom_dialog):
        """Test that category combo allows custom entries."""
        assert custom_dialog.category_combo.isEditable()

    def test_custom_dialog_default_values(self, custom_dialog):
        """Test that dialog has sensible default values."""
        # Version should default to 1.0
        assert custom_dialog.version_edit.text() == "1.0"

        # Auto-detect should be enabled by default
        assert custom_dialog.auto_detect_vars.isChecked()

    def test_custom_dialog_placeholder_text(self, custom_dialog):
        """Test that form fields have helpful placeholder text."""
        assert custom_dialog.name_edit.placeholderText() == "My Custom Template"
        assert "Brief description" in custom_dialog.description_edit.placeholderText()
        assert "Your Name" in custom_dialog.author_edit.placeholderText()
        assert "{{title}}" in custom_dialog.content_edit.placeholderText()


@pytest.mark.unit
class TestCustomTemplateDialogValidation:
    """Test suite for CustomTemplateDialog field validation."""

    @patch("PySide6.QtWidgets.QMessageBox.warning")
    def test_create_fails_without_name(self, mock_warning, custom_dialog, qtbot):
        """Test that create fails if name is empty."""
        # Set other required fields
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.description_edit.setText("Test description")
        custom_dialog.content_edit.setPlainText("= Test Content")

        # Leave name empty
        custom_dialog.name_edit.clear()

        # Trigger create
        custom_dialog._on_create_clicked()

        # Verify warning shown
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "name is required" in args[2].lower()

    @patch("PySide6.QtWidgets.QMessageBox.warning")
    def test_create_fails_without_category(self, mock_warning, custom_dialog, qtbot):
        """Test that create fails if category is empty."""
        # Set other required fields
        custom_dialog.name_edit.setText("Test Template")
        custom_dialog.description_edit.setText("Test description")
        custom_dialog.content_edit.setPlainText("= Test Content")

        # Clear category (set to empty string)
        custom_dialog.category_combo.setCurrentText("")

        # Trigger create
        custom_dialog._on_create_clicked()

        # Verify warning shown
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "category is required" in args[2].lower()

    @patch("PySide6.QtWidgets.QMessageBox.warning")
    def test_create_fails_without_description(self, mock_warning, custom_dialog, qtbot):
        """Test that create fails if description is empty."""
        # Set other required fields
        custom_dialog.name_edit.setText("Test Template")
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.content_edit.setPlainText("= Test Content")

        # Leave description empty
        custom_dialog.description_edit.clear()

        # Trigger create
        custom_dialog._on_create_clicked()

        # Verify warning shown
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "description is required" in args[2].lower()

    @patch("PySide6.QtWidgets.QMessageBox.warning")
    def test_create_fails_without_content(self, mock_warning, custom_dialog, qtbot):
        """Test that create fails if content is empty."""
        # Set other required fields
        custom_dialog.name_edit.setText("Test Template")
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.description_edit.setText("Test description")

        # Leave content empty
        custom_dialog.content_edit.clear()

        # Trigger create
        custom_dialog._on_create_clicked()

        # Verify warning shown
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "content is required" in args[2].lower()


@pytest.mark.unit
class TestCustomTemplateDialogVariableDetection:
    """Test suite for variable auto-detection functionality."""

    def test_detect_variables_finds_simple_variables(self, custom_dialog):
        """Test that _detect_variables finds {{variable}} patterns."""
        content = "= {{title}}\n:author: {{author}}\n:date: {{date}}"

        variables = custom_dialog._detect_variables(content)

        # Should find 3 unique variables
        assert len(variables) == 3
        var_names = [v.name for v in variables]
        assert "title" in var_names
        assert "author" in var_names
        assert "date" in var_names

    def test_detect_variables_deduplicates(self, custom_dialog):
        """Test that _detect_variables removes duplicates."""
        content = "{{title}} and {{title}} again with {{author}}"

        variables = custom_dialog._detect_variables(content)

        # Should find 2 unique variables (title, author)
        assert len(variables) == 2
        var_names = [v.name for v in variables]
        assert "title" in var_names
        assert "author" in var_names

    def test_detect_variables_sorts_alphabetically(self, custom_dialog):
        """Test that variables are sorted alphabetically."""
        content = "{{zebra}} {{apple}} {{banana}}"

        variables = custom_dialog._detect_variables(content)

        var_names = [v.name for v in variables]
        assert var_names == ["apple", "banana", "zebra"]

    def test_detect_variables_ignores_invalid_patterns(self, custom_dialog):
        """Test that invalid patterns are ignored."""
        content = "{{123invalid}} {{valid_name}} {{also-invalid}} {{another_valid}}"

        variables = custom_dialog._detect_variables(content)

        # Should only find valid_name and another_valid
        var_names = [v.name for v in variables]
        assert "valid_name" in var_names
        assert "another_valid" in var_names
        assert len(var_names) == 2

    def test_detect_variables_creates_required_variables(self, custom_dialog):
        """Test that detected variables are marked as required."""
        content = "{{title}}"

        variables = custom_dialog._detect_variables(content)

        assert len(variables) == 1
        assert variables[0].required is True
        assert variables[0].type == "string"

    def test_detect_variables_with_underscores(self, custom_dialog):
        """Test variable detection with underscores."""
        content = "{{first_name}} {{last_name}} {{email_address}}"

        variables = custom_dialog._detect_variables(content)

        assert len(variables) == 3
        var_names = [v.name for v in variables]
        assert "first_name" in var_names
        assert "last_name" in var_names
        assert "email_address" in var_names


@pytest.mark.unit
class TestCustomTemplateDialogCreation:
    """Test suite for template creation workflow."""

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_create_template_success(self, mock_info, custom_dialog, mock_template_manager, qtbot):
        """Test successful template creation."""
        # Fill all required fields
        custom_dialog.name_edit.setText("My Custom Template")
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.description_edit.setText("A test template")
        custom_dialog.author_edit.setText("Test Author")
        custom_dialog.version_edit.setText("1.5")
        custom_dialog.content_edit.setPlainText("= {{title}}\n{{content}}")

        # Enable auto-detect
        custom_dialog.auto_detect_vars.setChecked(True)

        # Mock dialog accept
        with patch.object(custom_dialog, "accept") as mock_accept:
            # Trigger create
            custom_dialog._on_create_clicked()

            # Verify manager was called
            mock_template_manager.create_template.assert_called_once()
            call_args = mock_template_manager.create_template.call_args
            template = call_args[0][0]
            custom_flag = call_args[1]["custom"]

            # Verify template properties
            assert template.name == "My Custom Template"
            assert template.category == "article"
            assert template.description == "A test template"
            assert template.author == "Test Author"
            assert template.version == "1.5"
            assert "{{title}}" in template.content
            assert custom_flag is True

            # Verify variables were detected
            assert len(template.variables) == 2

            # Verify success message shown
            mock_info.assert_called_once()
            info_args = mock_info.call_args[0]
            assert "created successfully" in info_args[2].lower()

            # Verify dialog accepted
            mock_accept.assert_called_once()

    @patch("PySide6.QtWidgets.QMessageBox.critical")
    def test_create_template_failure(self, mock_critical, custom_dialog, mock_template_manager, qtbot):
        """Test template creation failure handling."""
        # Make manager return False (creation failed)
        mock_template_manager.create_template.return_value = False

        # Fill all required fields
        custom_dialog.name_edit.setText("Test Template")
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.description_edit.setText("Test description")
        custom_dialog.content_edit.setPlainText("= Test")

        # Trigger create
        custom_dialog._on_create_clicked()

        # Verify error message shown
        mock_critical.assert_called_once()
        error_args = mock_critical.call_args[0]
        assert "failed to create" in error_args[2].lower()

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_create_template_with_auto_detect_disabled(self, mock_info, custom_dialog, mock_template_manager, qtbot):
        """Test template creation with auto-detect disabled."""
        # Fill required fields
        custom_dialog.name_edit.setText("Test Template")
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.description_edit.setText("Test description")
        custom_dialog.content_edit.setPlainText("= {{title}}")

        # Disable auto-detect
        custom_dialog.auto_detect_vars.setChecked(False)

        with patch.object(custom_dialog, "accept"):
            # Trigger create
            custom_dialog._on_create_clicked()

            # Verify template created with no variables
            call_args = mock_template_manager.create_template.call_args
            template = call_args[0][0]
            assert len(template.variables) == 0

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_create_template_defaults_anonymous_author(self, mock_info, custom_dialog, mock_template_manager, qtbot):
        """Test that empty author defaults to Anonymous."""
        # Fill required fields, leave author empty
        custom_dialog.name_edit.setText("Test Template")
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.description_edit.setText("Test description")
        custom_dialog.content_edit.setPlainText("= Test")
        custom_dialog.author_edit.clear()

        with patch.object(custom_dialog, "accept"):
            # Trigger create
            custom_dialog._on_create_clicked()

            # Verify author defaults to Anonymous
            call_args = mock_template_manager.create_template.call_args
            template = call_args[0][0]
            assert template.author == "Anonymous"

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_create_template_defaults_version(self, mock_info, custom_dialog, mock_template_manager, qtbot):
        """Test that empty version defaults to 1.0."""
        # Fill required fields, clear version
        custom_dialog.name_edit.setText("Test Template")
        custom_dialog.category_combo.setCurrentText("article")
        custom_dialog.description_edit.setText("Test description")
        custom_dialog.content_edit.setPlainText("= Test")
        custom_dialog.version_edit.clear()

        with patch.object(custom_dialog, "accept"):
            # Trigger create
            custom_dialog._on_create_clicked()

            # Verify version defaults to 1.0
            call_args = mock_template_manager.create_template.call_args
            template = call_args[0][0]
            assert template.version == "1.0"


@pytest.mark.unit
class TestTemplateBrowserNewTemplate:
    """Test suite for TemplateBrowser._create_new_template() integration."""

    @patch("asciidoc_artisan.ui.template_browser.CustomTemplateDialog")
    def test_create_new_template_opens_dialog(self, mock_dialog_class, qapp):
        """Test that _create_new_template creates and shows CustomTemplateDialog."""
        # Create proper mock manager with all required methods
        mock_manager = Mock()
        mock_manager.get_templates.return_value = []
        mock_manager.get_categories.return_value = ["article"]
        mock_manager.get_all_templates.return_value = []
        mock_manager.get_templates_by_category.return_value = []

        # Create browser
        browser = TemplateBrowser(mock_manager)

        # Mock dialog instance
        mock_dialog = Mock()
        mock_dialog.exec.return_value = False  # User cancels
        mock_dialog_class.return_value = mock_dialog

        # Trigger create
        browser._create_new_template()

        # Verify dialog was created
        mock_dialog_class.assert_called_once_with(mock_manager, browser)

        # Verify dialog was shown
        mock_dialog.exec.assert_called_once()

    @patch("asciidoc_artisan.ui.template_browser.CustomTemplateDialog")
    def test_create_new_template_reloads_on_success(self, mock_dialog_class, qapp):
        """Test that templates are reloaded after successful creation."""
        # Create proper mock manager with all required methods
        mock_manager = Mock()
        mock_manager.get_templates.return_value = []
        mock_manager.get_categories.return_value = ["article"]
        mock_manager.get_all_templates.return_value = []
        mock_manager.get_templates_by_category.return_value = []

        # Create browser
        browser = TemplateBrowser(mock_manager)

        # Mock dialog instance (user creates template)
        mock_dialog = Mock()
        mock_dialog.exec.return_value = True  # User accepts
        mock_dialog_class.return_value = mock_dialog

        # Mock _load_templates
        with patch.object(browser, "_load_templates") as mock_load:
            # Trigger create
            browser._create_new_template()

            # Verify templates were reloaded
            mock_load.assert_called_once()

    @patch("asciidoc_artisan.ui.template_browser.CustomTemplateDialog")
    def test_create_new_template_no_reload_on_cancel(self, mock_dialog_class, qapp):
        """Test that templates are NOT reloaded if user cancels."""
        # Create proper mock manager with all required methods
        mock_manager = Mock()
        mock_manager.get_templates.return_value = []
        mock_manager.get_categories.return_value = ["article"]
        mock_manager.get_all_templates.return_value = []
        mock_manager.get_templates_by_category.return_value = []

        # Create browser
        browser = TemplateBrowser(mock_manager)

        # Mock dialog instance (user cancels)
        mock_dialog = Mock()
        mock_dialog.exec.return_value = False  # User cancels
        mock_dialog_class.return_value = mock_dialog

        # Mock _load_templates
        with patch.object(browser, "_load_templates") as mock_load:
            # Trigger create
            browser._create_new_template()

            # Verify templates were NOT reloaded
            mock_load.assert_not_called()

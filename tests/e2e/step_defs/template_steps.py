"""
Step definitions for template management E2E tests.

Implements Gherkin steps for template operations.
"""

from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from asciidoc_artisan.core.models import Template, TemplateVariable
from asciidoc_artisan.core.template_engine import TemplateEngine
from asciidoc_artisan.core.template_manager import TemplateManager
from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Load all scenarios from the feature file
pytestmark = [pytest.mark.e2e, pytest.mark.bdd, pytest.mark.gui]
scenarios("../features/templates.feature")


# ============================================================================
# Template Test State
# ============================================================================


class TemplateState:
    """Track template operation state."""

    def __init__(self):
        self.templates = []
        self.selected_template = None
        self.recent_templates = []
        self.variables = []
        self.custom_templates = []
        self.manager = None  # Store manager instance for persistence


@pytest.fixture
def template_state():
    """Provide template state tracking."""
    return TemplateState()


@pytest.fixture
def template_manager():
    """Provide template manager instance with cleanup."""
    engine = TemplateEngine()
    manager = TemplateManager(engine)

    # Track templates to clean up
    created_templates = []

    # Store reference for cleanup
    manager._test_cleanup = created_templates

    yield manager

    # Cleanup: Delete any custom templates created during test
    for template_name in created_templates:
        try:
            manager.delete_template(template_name)
        except Exception:
            pass  # Ignore cleanup errors


# ============================================================================
# Shared Steps
# ============================================================================


@given("the application is running")
def application_running(app: AsciiDocEditor) -> AsciiDocEditor:
    """Verify application is running and ready."""
    assert app.isVisible()
    return app


# ============================================================================
# When Steps (Actions)
# ============================================================================


@when("I view the template library")
def view_template_library(template_manager: TemplateManager, template_state: TemplateState):
    """View all available templates."""
    # Store manager for use across steps
    if template_state.manager is None:
        template_state.manager = template_manager
    template_state.templates = template_manager.get_all_templates()


@when(parsers.parse('I filter templates by category "{category}"'))
def filter_by_category(
    template_manager: TemplateManager, template_state: TemplateState, category: str
):
    """Filter templates by category."""
    template_state.templates = template_manager.get_templates_by_category(category)


@when(parsers.parse('I select the template "{template_name}"'))
@given(parsers.parse('I select the template "{template_name}"'))
def select_template(
    template_manager: TemplateManager, template_state: TemplateState, template_name: str
):
    """Select a specific template."""
    template_state.selected_template = template_manager.get_template(template_name)
    assert template_state.selected_template is not None, f"Template '{template_name}' not found"


@when("I create a document from the template with variables:")
def create_from_template(
    app: AsciiDocEditor,
    template_manager: TemplateManager,
    template_state: TemplateState,
    datatable,
):
    """Create document from template with variables."""
    # Parse datatable - pytest-bdd provides as list of lists (no header row)
    variables = {}
    # datatable format: [['variable', 'value'], ['title', 'My New Document'], ...]
    for row in datatable:  # All rows are data
        if len(row) >= 2:
            var_name = str(row[0]).strip()
            var_value = str(row[1]).strip()
            variables[var_name] = var_value

    # Render template
    rendered = template_manager.engine.instantiate(
        template_state.selected_template, variables
    )

    # Set editor content
    app.editor.setPlainText(rendered)


@when("I view the template variables")
def view_template_variables(template_state: TemplateState):
    """View variables defined in selected template."""
    assert template_state.selected_template is not None
    template_state.variables = template_state.selected_template.variables


@when("I create a custom template with:")
def create_custom_template(
    template_manager: TemplateManager, template_state: TemplateState, datatable
):
    """Create a custom template."""
    # Store manager for use across steps
    if template_state.manager is None:
        template_state.manager = template_manager

    # Parse datatable - pytest-bdd provides as list of lists (no header row)
    template_data = {}
    for row in datatable:  # All rows are data
        if len(row) >= 2:
            key = str(row[0]).strip()
            value = str(row[1]).strip()
            template_data[key] = value

    # Extract variables from content
    import re

    content = template_data.get("content", "= Default\n\nContent")
    # Interpret literal \n as newlines
    content = content.replace("\\n", "\n")
    var_names = re.findall(r"\{\{(\w+)\}\}", content)

    variables = [
        TemplateVariable(name=var_name, description=f"{var_name} variable", required=False)
        for var_name in var_names
    ]

    # Create template object
    template = Template(
        name=template_data.get("name", "Unnamed Template"),
        category=template_data.get("category", "custom"),
        description=template_data.get("description", ""),
        variables=variables,
        content=content,
    )

    # Delete if exists (for test idempotency)
    existing = template_manager.get_template(template.name)
    if existing and existing.file_path and existing.file_path.startswith(
        str(template_manager.custom_dir)
    ):
        template_manager.delete_template(template.name)

    # Save template
    success = template_manager.create_template(template, custom=True)
    if success:
        template_state.custom_templates.append(template.name)
        # Track for cleanup
        if hasattr(template_manager, "_test_cleanup"):
            template_manager._test_cleanup.append(template.name)
    else:
        import logging

        logging.error(f"Failed to create template '{template.name}'")


@when(parsers.parse('I delete the template "{template_name}"'))
def delete_template(template_manager: TemplateManager, template_name: str):
    """Delete a custom template."""
    template_manager.delete_template(template_name)


@when("I view recent templates")
def view_recent_templates(template_manager: TemplateManager, template_state: TemplateState):
    """View recently used templates."""
    template_state.recent_templates = template_manager.get_recent_templates()


# ============================================================================
# Given Steps (Setup/Preconditions)
# ============================================================================


@given(parsers.parse('I have used the template "{template_name}"'))
def have_used_template(template_manager: TemplateManager, template_name: str):
    """Mark template as recently used."""
    template = template_manager.get_template(template_name)
    assert template is not None, f"Template '{template_name}' not found"
    template_manager.add_to_recent(template_name)


@given(parsers.parse('I have a custom template "{template_name}"'))
def have_custom_template(
    template_manager: TemplateManager, template_state: TemplateState, template_name: str
):
    """Create a custom template for testing."""
    # Delete if exists (for test idempotency)
    existing = template_manager.get_template(template_name)
    if existing and existing.file_path and existing.file_path.startswith(
        str(template_manager.custom_dir)
    ):
        template_manager.delete_template(template_name)

    template = Template(
        name=template_name,
        category="custom",
        description="Test template",
        variables=[
            TemplateVariable(name="title", description="Title", required=True),
        ],
        content="= {{title}}\n\nTest content",
    )

    success = template_manager.create_template(template, custom=True)
    assert success, f"Failed to create custom template '{template_name}'"
    template_state.custom_templates.append(template_name)
    # Track for cleanup
    if hasattr(template_manager, "_test_cleanup"):
        template_manager._test_cleanup.append(template_name)


# ============================================================================
# Then Steps (Assertions)
# ============================================================================


@then(parsers.parse("I should see {count:d} built-in templates"))
def verify_template_count(template_state: TemplateState, count: int):
    """Verify number of templates."""
    assert (
        len(template_state.templates) == count
    ), f"Expected {count} templates, found {len(template_state.templates)}"


@then(parsers.parse("I should see at least {count:d} templates"))
def verify_minimum_template_count(template_state: TemplateState, count: int):
    """Verify minimum number of templates."""
    assert (
        len(template_state.templates) >= count
    ), f"Expected at least {count} templates, found {len(template_state.templates)}"


@then(parsers.parse('the templates should include "{template_name}"'))
def templates_include(template_state: TemplateState, template_name: str):
    """Verify specific template is in list."""
    template_names = [t.name for t in template_state.templates]
    assert (
        template_name in template_names
    ), f"Expected '{template_name}' in templates: {template_names}"


@then(parsers.parse('I should see templates in the "{category}" category'))
def verify_category(template_state: TemplateState, category: str):
    """Verify templates are in specified category."""
    for template in template_state.templates:
        assert (
            template.category == category
        ), f"Template '{template.name}' has category '{template.category}', expected '{category}'"


@then(parsers.parse('the results should include "{template_name}"'))
def results_include(template_state: TemplateState, template_name: str):
    """Verify template is in results."""
    template_names = [t.name for t in template_state.templates]
    assert (
        template_name in template_names
    ), f"Expected '{template_name}' in results: {template_names}"


@then(parsers.parse('the editor should contain "{text}"'))
def editor_contains(app: AsciiDocEditor, text: str):
    """Verify editor contains text."""
    content = app.editor.toPlainText()
    assert text in content, f"Expected '{text}' in editor content"


@then(parsers.parse('I should see required variable "{var_name}"'))
def verify_required_variable(template_state: TemplateState, var_name: str):
    """Verify required variable exists."""
    var_names = [v.name for v in template_state.variables if v.required]
    assert (
        var_name in var_names
    ), f"Expected required variable '{var_name}', found: {var_names}"


@then(parsers.parse('I should see optional variable "{var_name}"'))
def verify_optional_variable(template_state: TemplateState, var_name: str):
    """Verify optional variable exists."""
    var_names = [v.name for v in template_state.variables]
    assert var_name in var_names, f"Expected variable '{var_name}', found: {var_names}"


@then("the custom template should be saved")
def verify_template_saved(template_state: TemplateState):
    """Verify custom template was saved."""
    assert len(template_state.custom_templates) > 0, "No custom templates were saved"


@then(parsers.parse('the template "{template_name}" should be available'))
def template_available(template_state: TemplateState, template_name: str):
    """Verify template is available."""
    # Use stored manager instance
    manager = template_state.manager
    assert manager is not None, "Template manager not initialized"
    template = manager.get_template(template_name)
    assert template is not None, f"Template '{template_name}' not found"


@then(parsers.parse('the template "{template_name}" should not be available'))
def template_not_available(template_manager: TemplateManager, template_name: str):
    """Verify template is not available."""
    template = template_manager.get_template(template_name)
    assert template is None, f"Template '{template_name}' should not exist"


@then("the template file should be removed")
def template_file_removed(template_manager: TemplateManager, template_state: TemplateState):
    """Verify template file was deleted."""
    # Check that custom templates directory doesn't contain the file
    for template_name in template_state.custom_templates:
        template = template_manager.get_template(template_name)
        if template:
            # Template still exists - file not removed
            pytest.fail(f"Template file for '{template_name}' still exists")


@then(parsers.parse('"{template_name}" should be the most recent'))
def verify_most_recent(template_state: TemplateState, template_name: str):
    """Verify template is most recent."""
    assert len(template_state.recent_templates) > 0, "No recent templates"
    most_recent = template_state.recent_templates[0]
    assert (
        most_recent.name == template_name
    ), f"Expected '{template_name}' as most recent, got '{most_recent.name}'"


@then(parsers.parse('"{template_name}" should be in recent list'))
def verify_in_recent(template_state: TemplateState, template_name: str):
    """Verify template is in recent list."""
    recent_names = [t.name for t in template_state.recent_templates]
    assert (
        template_name in recent_names
    ), f"Expected '{template_name}' in recent list: {recent_names}"

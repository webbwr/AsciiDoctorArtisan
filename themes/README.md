# Themes Directory

Place custom themes and stylesheets in this directory.

## Custom CSS for HTML Output

Create a custom CSS file and reference it in your AsciiDoc:

```asciidoc
:stylesheet: themes/custom.css
```

## PDF Themes

For PDF output, create a YAML theme file:

```bash
asciidoctor-pdf -a pdf-theme=themes/custom-theme.yml docs/index.adoc
```

## Resources

- [AsciiDoctor Styling Documentation](https://docs.asciidoctor.org/asciidoctor/latest/html-backend/default-stylesheet/)
- [PDF Theming Guide](https://docs.asciidoctor.org/pdf-converter/latest/theme/)

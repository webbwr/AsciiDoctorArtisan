# Themes

Put custom looks here.

## Custom CSS for HTML

Make a CSS file and use it:

```asciidoc
:stylesheet: themes/custom.css
```

## PDF Themes

For PDF, make a YAML theme file:

```bash
asciidoctor-pdf -a pdf-theme=themes/custom-theme.yml docs/index.adoc
```

## Help

- [Styling Docs](https://docs.asciidoctor.org/asciidoctor/latest/html-backend/default-stylesheet/)
- [PDF Theme Guide](https://docs.asciidoctor.org/pdf-converter/latest/theme/)

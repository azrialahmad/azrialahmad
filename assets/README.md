# Profile artwork

The light and dark headers follow the [portfolio](https://azrialahmad.is-a.dev/)'s
design tokens: cream surfaces, cobalt accents, Cormorant Garamond Italic, and DM Sans.
Lettering is converted to SVG paths for consistent rendering on GitHub.

To regenerate both headers:

```sh
uv run --with fonttools python scripts/generate-banners.py
```

The typefaces are licensed under the SIL Open Font License 1.1:

- [Cormorant Garamond · Christian Thalmann](https://github.com/google/fonts/blob/main/ofl/cormorantgaramond/OFL.txt)
- [DM Sans · The DM Sans Project Authors](https://github.com/google/fonts/blob/main/ofl/dmsans/OFL.txt)

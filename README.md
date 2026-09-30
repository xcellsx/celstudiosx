# celstudiosx

Branding and graphic design work for the celstudiosx portfolio.

The portfolio is split into three sections:

- **Branding + graphic design**: the main focus. This repo.
- **3D**: [cel.3d](https://github.com/xcellsx/cel.3d). Packaging from projects here can be rendered there.
- **UI/UX**: for fun

## Projects

| # | Project | Brief | Status |
|---|---|---|---|
| 01 | [Athena](projects/01-athena/) | designerbriefs #47: makeup brand, identity + packaging | Direction chosen (marble and gold); logo exploration next |

## Structure

```
projects/
  NN-project-name/
    README.md     brief, concept, identity decisions, progress
    brief/        the original brief (screenshots, text)
    reference/    moodboard images
    identity/     logo, pattern and other brand assets (SVG sources)
    source/       Affinity files
    exports/      finished exports (PNG, SVG, PDF) and portfolio slides
```

## Conventions

- New project: copy the folder layout above and bump the number.
- Work in Affinity. Save sources in `source/`, and export finished assets to `exports/` (SVG for vectors, PNG @2x for previews).
- Screen work is RGB. Print and packaging work is CMYK, with foils set up as spot colours.
- Portfolio slides: **1080 × 1440** (3:4), matching the cel.3d Instagram grid.
- Fonts must be free for commercial use (for example SIL Open Font License from Google Fonts). Note the licence in the project README.

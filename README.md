# Medical World Models: From Static Prediction to Clinically Valid Action-Aware Simulation

LaTeX source for the TMLR survey. `main.tex` is the entry point and compiles standalone with `latexmk`.

## Compile

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

All packages are standard TeX Live (no local binaries needed). The bibliography is `references.bib`; the TMLR style files (`tmlr.sty`, `tmlr.bst`, `fancyhdr.sty`, `math_commands.tex`) are included.

In the full project workspace, regenerate and verify the corpus figures/tables with:

```bash
python3 tools/make_landscape_figure.py
python3 tools/check_evidence_map_counts.py
```

## Sync to Overleaf

Two ways:

1. **Import from GitHub** (Overleaf account linked to GitHub): *New Project → Import from GitHub →* this repository. Subsequent updates are pulled or pushed through Overleaf's GitHub sync UI.
2. **Manual:** download this repo as a ZIP and use *New Project → Upload Project* in Overleaf.

`main.tex` is at the repository root, so Overleaf detects it as the main document automatically.

## Structure

- `main.tex` — manuscript body.
- `figure_motivation.tex`, `figure_audit.tex` — editable TikZ figures for the action boundary and the two-axis audit framework.
- `figure_landscape.tex` — wrapper for the data-driven corpus landscape.
- `table_*.tex` — generated tables (corpus distribution, capability levels, SATO-V core audit, openness audit, validation pyramid, representative works per track).
- `tools/make_landscape_figure.py` — regenerates Figure 3 from `../db/papers.csv` in the full project workspace.
- `figures/` — compiled and generated visual assets.
- `docs/visual_system_zh.md` — frozen palette and figure/table acceptance rules.
- `docs/structure_freeze_and_student_workpackages_zh.md` — bilingual section map and student work packages.

Figures and tables are generated from the project's evidence database; the companion paper list lives at <https://github.com/lanqz7766/awesome-medical-world-models>.

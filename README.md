# Saarbrücken Cookbook Corpus: a recipe for a diachronic study *à la CLARIN-D*


![sacoco logo](index_files/img/sacoco-logo.png "Saarbrücken Cookbook Corpus' logo")

This is the repository for the tutorial [Saarbrücken Cookbook Corpus: a recipe for a diachronic study *à la CLARIN-D*](http://chozelinek.github.io/sacoco).

This **tutorial** will show you step-by-step how to use the **CLARIN-D infrastructure** to **compile** a diachronic corpus of German cooking recipes (the [**Sa**arbrücken **Co**okbook **Co**rpus](http://hdl.handle.net/11858/00-246C-0000-001F-7C43-1)). Afterwards, you will learn how to **exploit** this resource to discover how the conative function has evolved in this register during the last centuries.

## Contents

- `data/`, SaCoCo's corpus data used for this showcase.
    - `contemporary/`
        - `source/`
        - `tei/`
        - `vrt/`
    - `historical/`
        - `source/`
        - `tei/`
        - `vrt/`
    - `metadata/`
    - `results/`
- `img/`, images and other graphic material used in the tutorial.
- `test/`, testing material used for the development of the tutorial and the scripts. It mimics the data folder structure. (Use this to check how the scripts work.)
    - `contemporary/`
    - `historical/`
    - `metadata/`
- `utils/`, files used by the scripts such as tool chains in XML format, XML templates, Relax NG schemas for validation...
- `README.md`, a file describing the contents of the repo.
- `index.html`, HTML version of the tutorial.
- `index.md`, markdown version to be better read in GitHub.
- `index.Rmd`, step-by-step guide on how to compile and exploit the SaCoCo corpus to to answer a research question. This is the source code used to generate `.md` and `.html` versions.
- `weblichtwrapper.py`, a script wrapping WebLicht as a Service to process big amounts of data.
- `wikiextractor.py`, a script to extract German recipes from a wiki dump.

## How to contribute

If you find a bug, a spelling mistake, or you want to share different or better solutions, you're more than welcome to submit a pull request with changes to the tutorial materials.

The HTML file of the tutorial is generated using Rmarkdown. Accordingly, the best way to contribute to the tutorial itself is to update the `.Rmd` file, rather than the `.html` or `.md` files.

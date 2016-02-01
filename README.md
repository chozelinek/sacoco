# Saarbrücken Cookbook Corpus: a recipe for a diachronic study *à la CLARIN-D*


![sacoco logo](index_files/img/sacoco-logo.png "Saarbrücken Cookbook Corpus' logo")

This is the repository for the tutorial [Saarbrücken Cookbook Corpus: a recipe for a diachronic study *à la CLARIN-D*](http://chozelinek.github.io/sacoco).

This **tutorial** will show you step-by-step how to use the **CLARIN-D infrastructure** to **compile** a diachronic corpus of German cooking recipes (the [**Sa**arbrücken **Co**okbook **Co**rpus](http://hdl.handle.net/11858/00-246C-0000-001F-7C43-1)). Afterwards, you will learn how to **exploit** this resource to discover how the conative function has evolved in this register during the last centuries.

## Contents

- `data/`, SaCoCo's corpus data used for this showcase.
    - `historical/`
        - `source/`
- `index_files/`, folder for CSS, JS, images, figures...
    - `img/`, images and other graphic material used in the tutorial.
- `results/`, csv files containing CQP output.
- `test/`, testing material used for the development of the tutorial and the scripts. It mimics the data folder structure. (Use this to check how the scripts work.)
    - `contemporary/`
        - `meta/`, VRT files with metadata as structural attributes
        - `source/`, source XML excerpt
        - `tei/`, TEI files
        - `vrt/`, VRT files after WebLicht
    - `historical/`
        - `meta/`, VRT files with metadata as structural attributes
        - `source/`, source XML excerpt
        - `tei/`, TEI files
        - `vrt/`, VRT files after WebLicht
    - `metadata/`, folder containg to CSV files generated from raw input, and `.meta` file for CQPweb.
- `utils/`, files used by the scripts: WebLicht tool chains in XML format, XML templates, Relax NG schemas for validation...
- `README.md`, a file describing the contents of the repo.
- `index.html`, HTML version of the tutorial.
- `index.Rmd`, step-by-step guide on how to compile and exploit the SaCoCo corpus to to answer a research question. This is the source code used to generate the `.html` version.
- `cqpwebsetup.html`, HTML version of the tutorial explaining how to set up the SaCoCo corpus for CQPweb.
- `cqpwerbsetup.html`, the source code to generate the `.html` version.
- `SaCoCo.bib`, SaCoCo's bibliography in `.bib` format.
- `sacoco.cqp`, CQP script.
- `metadata4cqpweb.py`, a script to convert extracted metadata in CSV form into the format suitable for CQPweb.
- `texts2corpus.py`, a script to concatenate all texts in one singe XML file.
- `waaswrapper.py`, a script wrapping WebLicht as a Service to process big amounts of data.
- `wikiextractor.py`, a script to extract German recipes from a wiki dump.
- `xmlextractor.py`, a script to transform historical recipes into TEI Lite.
- `requirements.txt`, Python 3 dependencies.
- `_output.yaml`, configuration for markdown to html transformations

## How to contribute

If you find a bug, a spelling mistake, or you want to share different or better solutions, you're more than welcome to submit a pull request with changes to the tutorial materials.

The HTML file of the tutorials are generated using Rmarkdown. Accordingly, the best way to contribute to the tutorial itself is to update the `.Rmd` file, rather than the `.html` files.

# Configuration file for the Sphinx documentation builder.
#
# Requires: sphinx, sphinx-autodoc-typehints, furo


# -- Project information -----------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath("../../../"))

project = 'parus'
copyright = "2026, Si-yang Yu, XiaoLe 'Eddie' Liu"
author = "Si-yang Yu, XiaoLe 'Eddie' Liu"


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.napoleon",  # Google-style docstrings
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints"
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ['_templates']
exclude_patterns = ['*assets*']
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown"
}


# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_static_path = ['_static']
html_logo = "_static/logo.png"
html_theme_options = {
    "logo_only": True
}

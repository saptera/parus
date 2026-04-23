# Configuration file for the Sphinx documentation builder.
# Requires: `sphinx` `sphinx-autodoc-typehints` `sphinx-design` `pydata-sphinx-theme`

import os
import sys

sys.path.insert(0, os.path.abspath("../../.."))  # Make the package importable


# -- Project information -----------------------------------------------------

project = "parus"
author = "Si-yang Yu, XiaoLe 'Eddie' Liu"
copyright = "2020-%Y, Research Group Saptera"
version = "1.0"
release = "1.0.0"


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx_design"
]

templates_path = ["_templates"]
source_suffix = {".rst": "restructuredtext"}
exclude_patterns = []
language = "en"


# -- Autodoc / Napoleon / typehints ------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource"
}
autodoc_typehints = "description"   # Render type hints in the body
autodoc_typehints_format = "short"  # `np.ndarray` instead of `numpy.ndarray`
autodoc_preserve_defaults = True
autoclass_content = "class"
autosummary_generate = True

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = False
napoleon_use_ivar = True
napoleon_attr_annotations = True

typehints_fully_qualified = False
always_document_param_types = True
typehints_defaults = "comma"


# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python":     ("https://docs.python.org/3", None),
    "numpy":      ("https://numpy.org/doc/stable", None),
    "scipy":      ("https://docs.scipy.org/doc/scipy", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "h5py":       ("https://docs.h5py.org/en/stable", None),
    "torch":      ("https://pytorch.org/docs/stable", None)
}

# Shorthand aliases used in docstrings that intersphinx cannot resolve.
nitpick_ignore_regex = [
    ("py:class", r"np\..*"),
    ("py:class", r"plt\..*"),
    ("py:class", r"h5\..*"),
    ("py:class", r"h5py\._hl\..*"),     # Private `h5py` submodules
    ("py:class", r"data\.DataLoader"),
    ("py:class", r"nn\.Module"),
    ("py:class", r"Module"),
    ("py:class", r"function"),          # Bare `function` type hint
    ("py:class", r".*\._[A-Za-z].*")    # Any private class
]


# -- HTML output -------------------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["apidoc.css"]
html_logo = "_static/logo.svg"
html_title = "[%s - %s]" % (project.upper(), release)
html_short_title = project.upper()
html_show_sourcelink = False
html_copy_source = False
html_last_updated_fmt = "%Y-%m-%d"
pygments_style = "sphinx"
pygments_dark_style = "monokai"

html_theme_options = {
    "github_url": "https://github.com/saptera/parus",
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/parus-major/",
            "icon": "fa-brands fa-python"
        }
    ],
    "navbar_align": "left",
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "show_prev_next": False,
    "show_toc_level": 2,
    "navigation_with_keys": True,
    "header_links_before_dropdown": 5,
    "secondary_sidebar_items": ["page-toc"],
    "footer_start": ["copyright", "last-updated"],
    "footer_end": ["sphinx-version", "theme-version"],
    "use_edit_page_button": False,
    "back_to_top_button": True
}

html_context = {
    "default_mode": "auto"
}

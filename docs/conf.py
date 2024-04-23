import sys
import os

# Insert HDrezka path into the system.
sys.path.insert(0, os.path.abspath(".."))

import HDrezka

project = HDrezka.__title__
copyright = f"2024, {HDrezka.__author__}"
author = HDrezka.__author__
release = HDrezka.__version__

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Options for EPUB output
epub_show_urls = "footnote"

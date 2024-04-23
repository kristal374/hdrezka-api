import re
import os


about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "..", "HDrezka", "__version__.py"), "r", encoding="utf-8") as f:
    text = re.sub(r"[\"\']\s*?\\\n\s*?[\"\']", "", f.read())
    for line in text.strip().split("\n"):
        name, value = re.search(r"(.*?)\s*?=\s*?[\"\'](.*?)[\"\']$", line).groups()
        about[name.strip()] = value.strip()

project = about["__title__"]
copyright = f"2024, {about['__author__']}"
author = about["__author__"]
release = about["__version__"]

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

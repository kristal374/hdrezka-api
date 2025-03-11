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

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.duration",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]

# -- Options for internationalization ----------------------------------------
language = "ru"
locale_dirs = ["locale"]
gettext_compact = False
gettext_uuid = True

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Options for EPUB output -------------------------------------------------
epub_show_urls = "footnote"

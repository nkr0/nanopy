import os, sys
from datetime import date

sys.path.insert(0, os.path.abspath("../"))

project = "nanopy"
author = "npy"
copyright = str(date.today().year) + ", " + author + ", MIT License"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]
autodoc_mock_imports = ["nanopy.ext"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

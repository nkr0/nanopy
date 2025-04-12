import os, sys
from datetime import date

sys.path.insert(0, os.path.abspath("../"))

project = "nanopy"
author = "npy"
copyright = str(date.today().year) + ", " + author + ", MIT License"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]
autodoc_mock_imports = ["nanopy.ed25519_blake2b", "nanopy.work"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

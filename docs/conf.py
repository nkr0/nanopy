import time

project = "nanopy"
author = "nkr0"
copyright = f"{time.strftime('%Y')}, {author}, MIT License"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

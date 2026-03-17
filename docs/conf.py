import os, sys
from datetime import date
sys.path.insert(0, os.path.abspath('../'))

project = 'nanopy'
author = 'npy'
copyright = str(date.today().year) + ', ' + author + ', MIT License'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

#autodoc_member_order = 'bysource'

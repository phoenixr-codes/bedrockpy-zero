#:==========================================
# Sphinx Documentation Builder Configuration
#:==========================================


#########
# Imports

from datetime import date
from importlib.metadata import version as version_of
import os
import sys


#############
# Change Path

sys.path.insert(0, os.path.abspath("."))


#####################
# Project Information


project = "bedrockpy"
copyright = f"{date.today().year}, phoenixR"
author = "phoenixR"
release = version_of("bedrockpy")


###############
# Configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    
    "sphinxcontrib_trio"
]

#nitpicky = True
#pygments_style = "github-dark"


#######################
# Autodoc Configuration

autodoc_typehints = "description"
autoclass_content = "both"


############
# Find Files

master_doc = "_source/index"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


###########################
# HTML Output Configuration

html_theme = "furo"
html_static_path = ["_static"]

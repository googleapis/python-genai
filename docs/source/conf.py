# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Google Gen AI SDK'
copyright = '2024, Google'
author = 'Google'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autoclass_content = 'both'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']

import html
import os
import sys
sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path
sys.path.insert(0, os.path.abspath('../google'))

extensions = ['sphinxcontrib.autodoc_pydantic', 'myst_parser', 'sphinx.ext.autodoc', 'sphinx_autodoc_typehints', 'sphinx.ext.napoleon']
html_theme = 'furo'

TEXT_FONTS = '"Google Sans Text", Roboto, "Helvetica Neue", Helvetica, Arial, sans-serif'
CODE_FONTS = 'Roboto Mono, "Helvetica Neue Mono", monospace'
FONT_COLOR_FOR_LIGHT_THEME = 'black'
FONT_COLOR_FOR_DARK_THEME = 'white'

html_theme_options = {
    "light_css_variables": {
        "font-stack": TEXT_FONTS,
        "font-stack--monospace": CODE_FONTS,
        "font-stack--headings": TEXT_FONTS,
        "color-brand-primary": FONT_COLOR_FOR_LIGHT_THEME,
        "color-brand-content": FONT_COLOR_FOR_LIGHT_THEME,
    },
    "dark_css_variables": {
        "font-stack": TEXT_FONTS,
        "font-stack--monospace": CODE_FONTS,
        "font-stack--headings": TEXT_FONTS,
        "color-brand-primary": FONT_COLOR_FOR_DARK_THEME,
        "color-brand-content": FONT_COLOR_FOR_DARK_THEME,
    },
}

# These folders are copied to the documentation's HTML output
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/custom.css',
]

autodoc_pydantic_model_show_json = True
autodoc_pydantic_model_show_config_summary = False

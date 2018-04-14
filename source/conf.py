#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sphinx_bootstrap_theme
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- General configuration ------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'pproject'
copyright = '2018, Simon Kallfass'
author = 'Simon Kallfass'

# The short X.Y version.
version = ''
# The full version, including alpha/beta/rc tags.
release = ''

# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['setup.py', 'tests/test_*', 'ouroboros/__init__.py']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'friendly'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------
html_theme = 'bootstrap'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#html_sidebars = {
#    '**': [
#        'relations.html',  # needs 'show_related': True theme option to display
#        'searchbox.html',
#    ]
#}
#html_sidebars = { '**': ['globaltoc.html', 'localtoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html', 'about.html'], }
#html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'], }
html_sidebars = {'**': []}
#html_sidebars = {'**': ['localtoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html']}



# -- Options for HTMLHelp output ------------------------------------------
htmlhelp_basename = 'pprojectdoc'


# -- Options for LaTeX output ---------------------------------------------
latex_elements = {
    'fontpkg': r'''
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
''',
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '12pt',

    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',

    # Latex figure (float) alignment
    # 'figure_align': 'htbp',
    'extraclassoptions': 'openany',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'pproject.tex', 'pproject Documentation',
     'Simon Kallfass', 'manual', True),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'pproject', 'pproject Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------
# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'pproject', 'pproject Documentation',
     author, 'pproject', 'One line description of project.',
     'Miscellaneous'),
]



napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = False
napoleon_use_param = False
napoleon_use_keyword = False
napoleon_use_rtype = False
napoleon_use_admonition_for_notes = True


html_theme_options = {
    'navbar_title': "pproject",
    'navbar_pagenav': False,
    'navbar_site_name': "",
    'navbar_sidebarrel': False,
    'bootswatch_theme': "slate",
    'navbar_class': "navbar navbar-inverse",
    'globaltoc_depth': -1,
    'navbar_links': [
#        ("pproject", "pprojecttool"),
#        ("Installation", "pprojectinstallation"),
#        ("Configuration", "pprojectconfiguration"),
#        ("Usage", "pprojectusage"),
#        ("Tutorial", "pprojecttutorial"),
#        ("Concepts", "pprojectconcepts"),
#        ("Impressum", "impressum"),
    ],
        }

html_logo = "_static/pproject.svg"
html_favicon = "_static/pproject.svg"
html_show_sourcelink = False

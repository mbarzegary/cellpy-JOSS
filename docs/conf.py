import os
import sys

INCLUDE_SOURCE_FILES = False

project_root = os.path.abspath("../")
name = "cellpy"
version_ns = {}
with open(os.path.join(project_root, name, "_version.py")) as f:
    exec(f.read(), {}, version_ns)


# -- Path setup -------------------------------------------------------

if INCLUDE_SOURCE_FILES:
    project_prmsdir = os.path.join(project_root, r"cellpy\parameters")
    project_utils = os.path.join(project_root, r"cellpy\utils")
    project_scripts = os.path.join(project_root, r"cellpy\scripts")
    project_readers = os.path.join(project_root, r"cellpy\readers")
    project_internals = os.path.join(project_root, r"cellpy\internals")

    sys.path.insert(0, project_root)
    sys.path.insert(0, project_prmsdir)
    sys.path.insert(0, project_utils)
    sys.path.insert(0, project_scripts)
    sys.path.insert(0, project_readers)
    sys.path.insert(0, project_internals)


# -- General configuration ---------------------------------------------

# Extensions
extensions = [
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    # "myst_nb",
    "myst_parser",
    "sphinx.ext.graphviz",
    # "autodoc2",
    "nbsphinx",
    "autoapi.extension",
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source file_names.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "cellpy"
copyright = "2023, Jan Petter Maehlen"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = version_ns["__version__"]
# The full version, including alpha/beta/rc tags.
release = version_ns["__version__"]


# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
# language = None

# There are two options for replacing |today|: either, you set today to
# some non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "_build",
    "_autoapi_templates",
    "jupyter_execute",
    "examples/.ipnb_checkpoints",
]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ["cellpy."]

# If true, keep warnings as "system message" paragraphs in the built
# documents.
# keep_warnings = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_book_theme"
html_theme_path = ["_themes"]

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as
# html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the
# top of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon
# of the docs.  This file should be a Windows icon file (.ico) being
# 16x16 or 32x32 pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets)
# here, relative to this directory. They are copied after the builtin
# static files, so a file named "default.css" will overwrite the builtin
# "default.css".
html_static_path = ["_static"]

# If not '', a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names
# to template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer.
# Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer.
# Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages
# will contain a <link> tag referring to it.  The value of this option
# must be the base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = "cellpydoc"


# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ("index", "cellpy.tex", "cellpy Documentation", "Jan Petter Maehlen", "manual")
]

# The name of an image file (relative to this directory) to place at
# the top of the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings
# are parts, not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "cellpy", "cellpy Documentation", ["Jan Petter Maehlen"], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "cellpy",
        "cellpy Documentation",
        "Jan Petter Maehlen",
        "cellpy",
        "Utilities for handling data from battery cell cycling.",
        "Miscellaneous",
    )
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

# --- other options ---------------------------------------------------

nbsphinx_kernel_name = "python3"
autoapi_dirs = ["../cellpy"]
# autodoc2_packages = ["../cellpy"]
# autoapi_template_dir = "_templates/_autoapi_templates"

# autodoc2_render_plugin = "myst"

autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "show-inheritance-diagram",
]


# myst settings
# see https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "colon_fence",
    "substitution",
]
myst_substitutions = {
    "ProjectVersion": version,
}

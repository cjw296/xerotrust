from importlib import metadata

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('http://docs.python.org', None),
}

project = 'xerotrust'
author = 'Chris Withers'
release = metadata.version(project)
copyright = f'2025 onwards {author}'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_member_order = 'bysource'

html_theme = 'furo'

nitpicky = True
nitpick_ignore: list[tuple[str, str]] = []

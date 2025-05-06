from importlib import metadata

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_tabs.tabs',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'starlette': ('https://www.starlette.io', None),
    'fastapi': ('https://fastapi.tiangolo.com', None),
    'typing': ('https://typing.readthedocs.io/en/latest/', None),
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
nitpick_ignore: list[tuple[str, str]] = [
    ('py:class', 'OAuth2PKCECredentials'),
    ('py:class', 'xero.auth.OAuth2PKCECredentials'),
    ('py:class', 'starlette.requests.Request'),
    ('py:class', 'starlette.responses.Response'),
    ('py:class', 'T'),
    ('py:class', 'P'),
    ('py:class', 'P.args'),
    ('py:class', 'P.kwargs'),
    ('py:obj', 'typing.P'),
]

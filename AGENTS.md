This file provides guidance to LLM tools such as [aider](https://aider.chat/) 
and [Claude Code](claude.ai/code) when working with code in this repository.

## Commands
- Build: `uv sync`
- Run tests: `uv run -m pytest`
- Run single test: `uv run -m pytest tests/test_file.py::TestClass::test_method -v`
- Run with coverage: `uv run -m pytest --cov`
- Coverage report: `uv run coverage report --show-missing --skip-covered --fail-under 100`
- Type check: `uv run mypy src tests`
- Lint: Don't run any linters.
- Format: `ruff format .`
- Update pytest-insta snapshots that use SnapshotFixture with: `uv run -m pytest --insta update tests/test_file.py::TestClass::test_method -v`

## Important: Always Format Code
**ALWAYS run `ruff format .` after making any code changes.** This ensures consistent code formatting across the entire codebase. Do not commit code without formatting it first.

## Code Style
- Python 3.13+ with strict type annotations
- Line length: 100 characters
- Imports: standard library first, then third-party, then local, clean up unused imports
- Naming: snake_case for functions/variables, CamelCase for classes
- Custom exceptions inherit from standard exceptions
- Comprehensive error handling with context
- Testing: pytest with fixtures
- Testing: Do not use assert in unit tests when comparing two values, always use textfixtures.compare
- Testing: When using pytest-insta SnapshotFixture, always call snapshot() as a function, not just snapshot. Use: compare(actual, expected=snapshot())
- Testing: Maintain 100% test coverage for all code
- Docstrings with clear parameter descriptions
- Automated formatting with ruff

## Git commits
- Keep commit messages succinct, do not use any emojis
- Do not add prefixes such as "feat:", "chore:", "test:", "fix:", etc.
- Capitalize the first letter of any commit message

## Xero API Documentation

The `api-docs/` directory contains comprehensive documentation for the Xero Accounting API:

- **Complete endpoint reference**: 35+ documented endpoints with parameters, examples, and cross-references
- **AI/LLM optimized format**: Structured markdown tables and consistent formatting
- **Usage guidance**: When working on Xero API-related features, ALWAYS consult this documentation first
- **Key files**:
  - `api-docs/README.md` - Overview and format standards
  - `api-docs/METHODOLOGY.md` - How the documentation was created and maintained
  - `api-docs/{endpoint}.md` - Individual endpoint documentation

**When to use the API documentation**:
- Implementing new Xero API integrations
- Understanding request/response parameters
- Debugging API calls and responses  
- Adding support for new endpoints
- Verifying field names, types, and relationships

**Example endpoints**: `accounts.md`, `invoices.md`, `banktransactions.md`, `contacts.md`, etc.

This documentation should be your primary reference for Xero API development work.

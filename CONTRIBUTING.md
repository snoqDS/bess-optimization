# Contributing to BESS Optimization

Thank you for your interest in contributing. This document outlines the process for contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:

    git clone https://github.com/YOUR_USERNAME/bess-optimization.git
    cd bess-optimization

3. Install dependencies:

    uv sync

4. Create a feature branch:

    git checkout -b feat/your-feature-name

## Branch Naming

- `feat/` for new features
- `fix/` for bug fixes
- `chore/` for maintenance tasks
- `docs/` for documentation updates

## Commit Messages

Follow Conventional Commits format:

- `feat: add weather integration for price forecasting`
- `fix: correct SoC boundary constraint`
- `chore: update dependencies`
- `docs: expand user guide`

## Code Style

This project uses Ruff for linting and formatting. Before committing:

    uv run ruff check src/ main.py
    uv run ruff format src/ main.py

## Running Tests

    uv run pytest tests/ -v

All tests must pass before submitting a pull request.

## Pull Request Process

1. Ensure all tests pass
2. Ensure ruff check passes with no errors
3. Update README.md if your change affects usage or installation
4. Submit your pull request against the `main` branch
5. Describe what your change does and why

## Adding a New Optimization Model

1. Create a new module under `src/opt_engine/models/`
2. Follow the existing pattern in `src/opt_engine/models/battery/`
3. Add corresponding tests under `tests/unit/`
4. Document parameters and return values in docstrings

## Reporting Issues

Open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 license.

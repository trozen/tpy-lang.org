# Everyday tasks. All targets use uv, which bootstraps .venv from
# pyproject.toml on first run -- no manual setup.

.DEFAULT_GOAL := help
.PHONY: help serve site docs test examples

help:  ## list available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-10s %s\n", $$1, $$2}'

serve:  ## docs dev server with live reload (http://127.0.0.1:8000/docs/)
	uv run mkdocs serve -f docs-site/mkdocs.yml

site:  ## preview the whole site, landing page + docs (http://127.0.0.1:8000/)
	rm -rf .site-preview
	cp -r docs .site-preview
	uv run mkdocs build -f docs-site/mkdocs.yml -d $(CURDIR)/.site-preview/docs
	python3 -m http.server 8000 --directory .site-preview

docs:   ## rebuild the committed docs/docs/ output from docs-site/src
	uv run mkdocs build -f docs-site/mkdocs.yml

test:   ## verify every docs code snippet against the pinned compiler
	uv run pytest

examples:  ## regenerate docs/examples.js from examples/
	python3 build_examples.py

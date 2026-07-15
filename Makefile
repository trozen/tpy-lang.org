# Everyday tasks. All targets use uv, which bootstraps .venv from
# pyproject.toml on first run -- no manual setup.

.DEFAULT_GOAL := help
.PHONY: help serve site docs test check examples

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

# The pre-push gate: nothing the site shows should fail to compile. Both passes
# run against the pinned vendor/tpy -- `--project` puts its `tpy` on PATH, which
# is all verify_examples.py wants.
#
# The landing-page examples are NOT checked against the published release, so
# this gate does not prove a `pip install tpy-lang` user can run them -- today
# requests_demo.py cannot (it needs tplib.requests, unreleased). That is
# deliberate while the site is unannounced; see the launch note in CLAUDE.md.
check:  ## verify everything the site shows: docs snippets + landing examples
	uv run pytest
	uv run --project vendor/tpy python verify_examples.py

examples:  ## regenerate docs/examples.js from examples/
	python3 build_examples.py

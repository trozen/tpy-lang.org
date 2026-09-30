# Everyday tasks. All targets use uv, which bootstraps .venv from
# pyproject.toml on first run -- no manual setup.

.DEFAULT_GOAL := help
.PHONY: help serve site docs test check examples og

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
# The landing-page examples are NOT checked against the published release
# here, so this gate alone does not prove a `pip install tpy-lang` user can run
# them whenever the pin runs ahead of PyPI. The announce gate in CLAUDE.md
# covers that.
check:  ## verify everything the site shows: docs snippets + landing examples
	uv run pytest
	uv run --project vendor/tpy python verify_examples.py

examples:  ## regenerate docs/examples.js from the tpy-examples submodule
	python3 build_examples.py

# The card is a screenshot rather than a hand-drawn PNG so it can reuse the
# landing page's CSS verbatim. Needs a Chrome/Chromium binary on PATH.
CHROME ?= $(shell command -v google-chrome chromium chromium-browser 2>/dev/null | head -1)
og:  ## regenerate docs/og.png, the social-share card, from og-card.html
	@test -n "$(CHROME)" || { echo "make og: no Chrome/Chromium found; set CHROME=/path/to/binary" >&2; exit 1; }
	$(CHROME) --headless=new --disable-gpu --hide-scrollbars \
	  --window-size=1200,630 --screenshot=docs/og.png file://$(CURDIR)/og-card.html

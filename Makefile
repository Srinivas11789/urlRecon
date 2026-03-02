.DEFAULT_GOAL := help
.PHONY: help install test lint run demo clean

# ── Formatting helpers ────────────────────────────────────────────────────────
BOLD  := $(shell tput bold 2>/dev/null)
RESET := $(shell tput sgr0 2>/dev/null)

## help: Show this help message
help:
	@echo ""
	@echo "$(BOLD)urlRecon — available targets$(RESET)"
	@echo ""
	@sed -n 's/^## //p' $(MAKEFILE_LIST) | column -t -s ':' | sed 's/^/  /'
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────

## install: Install Python dependencies
install:
	pip install -r requirements.txt

## install-dev: Install dependencies including test and lint tools
install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8

# ── Quality ───────────────────────────────────────────────────────────────────

## lint: Run flake8 (fatal errors only)
lint:
	flake8 urlrecon/ test/ --count --select=E9,F63,F7,F82 --show-source --statistics

## lint-full: Run flake8 with style warnings
lint-full:
	flake8 urlrecon/ test/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

## test: Run test suite (no network required)
test:
	python3 -m pytest test/ -v --tb=short

## test-cov: Run tests with coverage report
test-cov:
	python3 -m pytest test/ -v --tb=short --cov=urlrecon --cov-report=term-missing

# ── Run ───────────────────────────────────────────────────────────────────────

## run: Scan sample URLs and write reports to ./output
run:
	python3 urlrecon/main.py -i samples/demo_urls.txt -o ./output -v

## run-kml: Scan sample URLs, KML output only
run-kml:
	python3 urlrecon/main.py -i samples/demo_urls.txt -o ./output --format kml -v

# ── Demo ──────────────────────────────────────────────────────────────────────

## demo: Record CLI demo GIF using VHS in Docker (writes samples/urlrecondemo.gif)
demo:
	docker build -f Dockerfile.demo -t urlrecon-vhs .
	docker run --rm -v "$(PWD)":/vhs urlrecon-vhs demo.tape

# ── Clean ─────────────────────────────────────────────────────────────────────

## clean: Remove generated output, caches and coverage files
clean:
	rm -rf output/ report/ .pytest_cache/ .coverage coverage.xml htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

# urlRecon

[![Tests](https://github.com/srixivas/urlRecon/actions/workflows/test.yml/badge.svg)](https://github.com/srixivas/urlRecon/actions/workflows/test.yml)
[![Security](https://github.com/srixivas/urlRecon/actions/workflows/security.yml/badge.svg)](https://github.com/srixivas/urlRecon/actions/workflows/security.yml)
[![CodeQL](https://github.com/srixivas/urlRecon/actions/workflows/codeql.yml/badge.svg)](https://github.com/srixivas/urlRecon/actions/workflows/codeql.yml)

<img src="https://srixivas.github.io/urlRecon/logo.png" width="150" height="150" title="Logo">

Reconnaissance tool for URLs and domains. Given a list of targets, collects technical intelligence in a single pass and writes reports in three formats.

---

## What it collects

| Data | Source |
|------|--------|
| Domain / hostname | Parsed from URL |
| IP address | Socket DNS resolution |
| DNS A records | `dnspython` |
| WHOIS / ASN | `ipwhois` (RDAP) + whois.com scrape |
| Server fingerprint | HTTP response headers |
| Geolocation (city, country, lat/long, ISP) | [ipapi.co](https://ipapi.co) |

## Output formats

| File | Format | Contents |
|------|--------|----------|
| `report/report.txt` | Plain text | Human-readable summary of all fields |
| `report/urlInformation.db` | SQLite | One row per URL — queryable with any SQL tool |
| `report/urlLocation.kml` | KML | Geolocation pins — open in Google Earth or Maps |

---

## Requirements

- Python 3.10+
- Dependencies from `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Scan a local file of URLs (one per line)
python3 urlrecon/main.py -i samples/sample_urls.txt

# Write reports to a specific directory
python3 urlrecon/main.py -i samples/sample_urls.txt -o /tmp/recon-out

# KML output only, with a 0.5 s delay between requests
python3 urlrecon/main.py -i samples/sample_urls.txt --format kml --delay 0.5

# Fetch the URL list from a remote endpoint
python3 urlrecon/main.py --url-source -i https://example.com/urls.txt

# Verbose / debug logging
python3 urlrecon/main.py -i samples/sample_urls.txt -v
```

All three invocation styles are supported:

```bash
python3 urlrecon/main.py -i <file>       # direct script
python3 -m urlrecon.main -i <file>       # module
python3 -m urlrecon -i <file>            # package
```

### All options

```
usage: urlrecon [-h] -i INPUT [-o OUTPUT] [--format {text,sql,kml,all}]
                [--delay DELAY] [--url-source] [-v]

options:
  -h, --help            show this help message and exit
  -i, --input           Local file of URLs (one per line), or a remote URL
                        when --url-source is set.
  -o, --output          Output directory (default: current working directory)
  --format              text | sql | kml | all  (default: all)
  --delay               Seconds to wait between each URL request (default: 0)
  --url-source          Treat --input as a remote URL returning a URL list
  -v, --verbose         Enable debug-level logging
```

### Input file format

One URL per line, e.g. `samples/sample_urls.txt`:

```
https://www.google.com/
http://www.wikipedia.org/
https://github.com/
```

---

## Demo

<img src="https://github.com/srixivas/urlRecon/blob/master/samples/urlrecondemo.gif" title="Demo">

---

## Project structure

```
urlrecon/
├── __init__.py
├── __main__.py          # enables: python3 -m urlrecon
├── main.py              # CLI entry point (argparse)
└── modules/
    ├── __init__.py
    ├── restApi.py        # HTTP layer — GET/POST/DELETE with timeout
    ├── domainInfoApi.py  # Core engine — DNS, WHOIS, geo, fingerprint
    └── reportGenerator.py # Text / SQLite / KML writers

test/
├── test_domain_info_api.py   # Unit tests (all network calls mocked)
└── test_full_work_flow.py    # Integration tests (all network calls mocked)

.github/workflows/
├── test.yml      # Lint + tests across Python 3.10 / 3.11 / 3.12
├── security.yml  # pip-audit (CVE scan) + bandit (SAST)
└── codeql.yml    # GitHub CodeQL semantic analysis
```

---

## Makefile

```
make help         Show all available targets
make install      Install dependencies
make install-dev  Install dependencies + test/lint tools
make lint         flake8 fatal errors only
make lint-full    flake8 with style warnings
make test         Run test suite (offline, no network needed)
make test-cov     Run tests with coverage report
make run          Scan samples/demo_urls.txt → ./output
make demo         Record CLI demo GIF via VHS in Docker
make clean        Remove output/, caches, .pyc files
```

## Running tests

```bash
make test
# or directly:
python3 -m pytest test/ -v
```

Tests run entirely offline — all network calls are mocked with `unittest.mock`.

## Recording the demo GIF

The demo is recorded with [VHS](https://github.com/charmbracelet/vhs) running in Docker — nothing installs on your machine:

```bash
make demo
# equivalent to:
docker run --rm -v "$PWD":/vhs ghcr.io/charmbracelet/vhs demo.tape
```

The script is in `demo.tape`. Edit it to change the URLs, theme, or timing, then re-run `make demo` to regenerate `samples/urlrecondemo.gif`.

---

## CI / Security workflows

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| **Tests** | push, PR | Lint (flake8) + pytest across Python 3.10–3.12, coverage report |
| **Security** | push, PR, weekly | `pip-audit` for dependency CVEs, `bandit` for SAST |
| **CodeQL** | push, PR, weekly | GitHub semantic analysis — results in Security tab |

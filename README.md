# AtScale Aggregate Manager 🚀

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A lightweight command-line tool to manage, report, and analyze AtScale aggregates with a simple, scrollable list selection UI.

--- 

## Table of Contents 📚
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Troubleshooting & Tips](#troubleshooting--tips)
- [Contribution](#contribution)
- [License](#license)

---

## Overview ✨
AtScale Aggregate Manager provides quick CLI-based workflows for:
- Rebuilding aggregates for selected cubes
- Listing, exporting, and analyzing aggregates
- Performing health checks and viewing build history
- Generating CSV reports and statistics for offline review

Built to be cross-platform (Windows, macOS, Linux) and easy to run locally.

## Features ✅
- Aggregate Rebuild: trigger full rebuilds per cube
- Aggregate Reports: list aggregates, export CSV, and view statistics
- Health Checks: detect common issues and warnings
- Build History: list recent builds and details
- JWT Token Management: automatic token refresh + caching

## Prerequisites ⚠️
- Python 3.8 or higher
- Access to an AtScale instance (installer — currently the code supports **V1 installer** only; container support is planned for a future release)
- Network access to your AtScale host

## Installation 🔧
Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd atscale-aggregate-util
pip install -r requirements.txt
```

## Configuration 🔐
Create a `config.json` in the project folder. Example for an installer instance:

```json
{
  "instance_type": "installer",
  "username": "admin",
  "password": "your_password",
  "host": "development.atscaledomain.com",
  "organization": "default"
}
```

For a container-based instance (OAuth):

```json
{
  "instance_type": "container",
  "username": "admin",
  "password": "your_password",
  "host": "development.atscaledomain.com",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

**Host entry notes:**

- If your server uses HTTP, include the protocol: `http://<host>` (e.g., `http://dev.example.com`).
- If your server uses HTTPS, you can either provide just the hostname (e.g., `dev.example.com`) or include the protocol: `https://<host>` (both are accepted).
- The **default port is `10500`**. To use a non-default port include it in the host value (e.g., `https://dev.example.com:10501`).

**Examples:**

```json
{
  "host": "http://dev.example.com"
}
```

```json
{
  "host": "dev.example.com"
}
```

> **Note:** Starting with **v2**, container (public API) instances are supported. For container instances you must provide a valid **`token`** in `config.json`. The `client_id` and `client_secret` are **optional** — some endpoints (for example, **aggregate build history**) may require OAuth client credentials; if provided the utility will use them to access those endpoints.


## Usage 🧭
Run the CLI (interactive):

```bash
python main.py
```

Main menu options:
- Refresh Token
- Aggregate Rebuild
- Aggregate Report
- Exit

Report options (choose a cube first):
- List aggregates with details
- Export aggregates to CSV
- Show aggregate statistics
- Check aggregate health
- Aggregate build history

CSV reports are generated in the current directory with the pattern:
`aggregates_<CubeName>_<timestamp>.csv`

Headless / non-interactive usage (v2):
```bash
python main.py -h
usage: main.py [-h] [--project-id PROJECT_ID] [--cube-id CUBE_ID] [--export-csv] [--list-aggregates] [--list-projects]

ATSCALE AGGREGATE MANAGEMENT TOOL

options:
  -h, --help            show this help message and exit
  --project-id PROJECT_ID
                        Project/Catalog ID (required for direct export)
  --cube-id CUBE_ID     Cube/Model ID (required for direct export)
  --export-csv          Export aggregates to CSV directly (requires --project-id and --cube-id)
  --list-aggregates     List aggregates with details directly (requires --project-id and --cube-id)
  --list-projects       List all published projects/catalogs and exit
```

Examples:
- Export aggregates to CSV directly:
```bash
python main.py --project-id <PROJECT_ID> --cube-id <CUBE_ID> --export-csv
```
- List aggregates for a cube:
```bash
python main.py --project-id <PROJECT_ID> --cube-id <CUBE_ID> --list-aggregates
```
- List published projects and exit:
```bash
python main.py --list-projects
```

## Project Structure 🗂️
```
./
├── main.py                    # CLI entry point
├── config.py                  # Configuration + JWT handling
├── api_client.py              # API requests to AtScale
├── ui_components.py           # CLI UI helpers
├── rebuild_manager.py         # Rebuild logic
├── report_generator.py        # Report flow
├── cube_aggregate_reporter.py # Listing & CSV export
├── aggregate_statistics.py    # Statistics and analysis
├── aggregate_health_checker.py# Health checks
├── aggregate_build_history.py # Build history analysis
├── config.json                # Example config (create locally)
└── requirements.txt           # Python dependencies
```

## Troubleshooting & Tips 🛠️
- Authentication Failed: verify credentials and user permissions in `config.json`.
- Connection Refused: check host/port and firewall settings.
- No Projects Found: ensure projects are published in AtScale.
- Token Expired: use Refresh Token or restart the app.

For development, you can add print/log statements to debug; the app currently prints errors to the console.

## Changelog 📝
**v2.0.0** — Added container (public API) support & headless run (2025-12-24)
- Container (public API) support (requires `token` in `config.json`)
- Optional `client_id`/`client_secret` for endpoints like aggregate build history
- Headless mode: CLI flags for automated exports and listing
- Documentation updates and examples

**v1.0.0** — Initial release
- Aggregate management (rebuild & reporting)
- Multiple report types and build history analysis

## License
This project is provided as-is. See `LICENSE` for details.

---

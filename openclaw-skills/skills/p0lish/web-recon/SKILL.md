---
name: web-recon
description: "Web security scanning and reconnaissance. Use when: user asks to scan a website, check security headers, find subdomains, discover directories, scan for secrets/vulnerabilities, fingerprint tech stacks, capture screenshots, port scan, or perform any web security assessment. Covers: passive recon, DNS, port scanning, Shodan, tech fingerprinting, WAF detection, subdomain enumeration, directory bruteforce, secrets scanning, security header scoring, CORS checks, vulnerability scanning, WordPress analysis, SSL/TLS checks, Nuclei template scans, and screenshot capture."
---

# Web Recon

Web security scanner with modular steps, header scoring, port scanning, and JSON output.

## Quick Start

```bash
# Quick scan (recon, fingerprint, secrets, header scoring, report)
scripts/webscan.sh example.com --quick

# Full scan (all 12 steps)
scripts/webscan.sh example.com

# Full scan with JSON output and screenshot
scripts/webscan.sh example.com --json --screenshot

# Resume a crashed scan (skips completed steps)
scripts/webscan.sh example.com --resume

# Single step
scripts/webscan.sh example.com recon
scripts/webscan.sh example.com vulns

# Secrets scan only
scripts/titus-web.sh https://example.com
```

Output: `~/.openclaw/workspace/recon/<domain>/`

## Options

| Flag | Description |
|------|------------|
| `--quick` | Light scan: recon, fingerprint, secrets, vulns, report |
| `--full` | All steps (default) |
| `--json` | Generate `results.json` alongside markdown report |
| `--screenshot` | Capture homepage screenshot |
| `--resume` | Skip steps that already have output files |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `SHODAN_API_KEY` | Shodan API key for infrastructure intel (falls back to CLI) |
| `OUTDIR` | Override output directory |

## Steps

| Step | What it does |
|------|-------------|
| `recon` | DNS records, IP geolocation, **port scan (nmap)**, Shodan, Wayback URLs |
| `fingerprint` | HTTP headers, WhatWeb tech stack, WAF detection, CMS check |
| `subdomains` | Subfinder + Amass enumeration, httpx probing |
| `dirs` | Gobuster + ffuf directory/file bruteforce |
| `secrets` | Titus secrets scan + expanded sensitive file checks (30+ paths) |
| `vulns` | **Security header scoring** (10 headers, severity-weighted), **CORS check**, SSL, Nikto |
| `wpscan` | WordPress-specific scan (auto-skips if not WP) |
| `nuclei` | Template-based vulnerability scanning |
| `ssl` | SSL/TLS analysis via testssl |
| `screenshot` | Homepage capture via cutycapt/chromium |
| `report` | Generates `results.md` (+ `results.json` with `--json`) |

## Security Header Scoring

Scores 10 security headers by severity:

| Severity | Points | Headers |
|----------|--------|---------|
| Critical | 30 | Strict-Transport-Security, Content-Security-Policy |
| High | 20 | X-Frame-Options |
| Medium | 10 | X-Content-Type-Options, Referrer-Policy, Permissions-Policy |
| Low | 5 | X-XSS-Protection, COOP, CORP, COEP |

Rating: 🟢 ≥80% · 🟡 ≥50% · 🟠 ≥25% · 🔴 <25%

## Output Structure

```
~/.openclaw/workspace/recon/<domain>/
├── results.md              # Markdown report
├── results.json            # JSON report (--json)
├── screenshot.png          # Homepage capture (--screenshot)
├── dns.txt                 # DNS records
├── geo.json                # IP geolocation
├── ports.txt               # nmap port scan
├── ports-grep.txt          # nmap greppable output
├── shodan.json/txt         # Shodan infrastructure data
├── headers.txt             # HTTP response headers
├── header-score.txt        # Security header score card
├── cors.txt                # CORS configuration check
├── whatweb.txt             # Technology fingerprint
├── waf.txt                 # WAF detection
├── cms.txt                 # CMS detection
├── subdomains.txt          # Discovered subdomains
├── subdomains-live.txt     # Live subdomains (httpx)
├── dirs.txt                # Discovered directories/files
├── sensitive-files.txt     # Exposed config files
├── titus.txt               # Secrets scan results
├── nikto.txt               # Vulnerability scan
├── nuclei.txt              # Template-based findings
├── ssl.txt                 # SSL/TLS analysis
├── wpscan.txt              # WordPress scan
├── wayback.txt             # Wayback Machine URLs
└── robots.txt / sitemap.xml
```

## Review Priority

1. **header-score.txt** — overall security posture at a glance
2. **sensitive-files.txt** — any "FOUND" = critical
3. **cors.txt** — misconfigured CORS = data theft risk
4. **titus.txt** — exposed secrets/API keys
5. **ports.txt** — unexpected open ports
6. **nuclei.txt** — known CVEs
7. **subdomains-live.txt** — forgotten/dev subdomains

## Tool Requirements

See [references/tools.md](references/tools.md) for install instructions. Scripts skip missing tools gracefully.

## Wordlists

See [references/wordlists.md](references/wordlists.md). Auto-selects medium, falls back to smaller.

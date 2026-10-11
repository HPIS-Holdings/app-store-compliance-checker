# Security Policy

## Supported versions
The latest release receives security fixes.

## Reporting a vulnerability
Please **do not open a public issue**. Use GitHub's private reporting:
[Report a vulnerability](https://github.com/HPIS-Holdings/app-store-compliance-checker/security/advisories/new).
We aim to acknowledge reports within 3 business days.

## Scope
The checker reads local files only, never executes `app.config.js/ts`, and makes no network calls unless you pass `--check-links`. The MCP server restricts reads to `COMPLIANCE_ALLOWED_ROOTS`. Path-escape, code-execution, secret-leak-in-output and supply-chain issues (e.g. the optional Greenlight installer) are in scope.

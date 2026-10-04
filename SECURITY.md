# Security Policy

## Scope

REALITYX is a security-sensitive evidence verification system. Security reports should focus on authentication, authorization, evidence integrity, provenance, cryptographic verification, provider isolation, data exposure, dependency vulnerabilities, and denial-of-service risks.

## Do not disclose secrets

Never include API keys, owner master keys, private signing keys, database credentials, access tokens, or personal data in an issue or pull request. If a report contains sensitive material, remove it and use the repository owner's private security-reporting channel.

## Security principles

- Owner/Master control is restricted to the owner role.
- Providers and external APIs supply evidence; they never become decision authority.
- Secrets are deployment-managed and must never be committed to source control.
- Failed or unavailable providers are not treated as negative verification evidence.
- Cryptographic validity does not by itself imply legal or government certification.
- Security-sensitive changes require automated tests before merge.

## Dependency security

Production dependencies are pinned in `backend/pyproject.toml`. CI performs an automated Python dependency vulnerability audit. A dependency with a known vulnerability must be upgraded or explicitly reviewed before release.

## Reporting

For a suspected vulnerability, provide the affected component, impact, reproduction steps that do not expose secrets, and the first known affected commit or version when available.

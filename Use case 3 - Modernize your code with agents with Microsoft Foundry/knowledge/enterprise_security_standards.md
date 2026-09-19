# Enterprise Application Security Standards

## Risk classification

- **Critical:** Immediate compromise, exposed production secret, active remote
  code execution, or unauthenticated access to highly sensitive operations.
- **High:** Likely exploitation with serious confidentiality, integrity, or
  availability impact.
- **Medium:** Exploitation requires additional conditions or has limited impact.
- **Low:** Defense-in-depth or low-impact weakness.
- **Informational:** Improvement with no demonstrated security weakness.

## Mandatory controls

- Use centralized identity, least privilege, and server-side authorization.
- Keep secrets outside source code and rotate any exposed credential.
- Validate input at trust boundaries and encode output for its destination.
- Use parameterized queries and safe, structured APIs.
- Use supported cryptographic libraries and approved algorithms. Do not invent
  encryption or store plaintext passwords.
- Enforce TLS validation and secure transport.
- Pin, inventory, and scan third-party dependencies.
- Record security-relevant events without recording secrets or excessive
  personal data.
- Apply secure defaults, bounded resource use, timeouts, and rate limits.

## Review requirements

Every reported security issue must include code evidence, attack preconditions,
business impact, confidence level, remediation, and a verification test. Do not
assign a CVE unless the affected product and version have been confirmed.

## Release gate

Critical findings block release. High findings require remediation or written
risk acceptance. Security tests and secret scanning must pass before release.

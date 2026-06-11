# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of RegOps Shield seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report

Please send an email to the repository owner via GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/nsavarn/regops-shield/security)
2. Click **"Report a vulnerability"**
3. Fill in the details of the vulnerability

### What to Include

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline

- **Initial Response**: Within 48 hours
- **Triage**: Within 5 business days
- **Resolution**: Depends on severity (Critical: 7 days, High: 30 days, Medium/Low: 90 days)

## Security Best Practices

When deploying RegOps Shield:

### Environment Variables
- Never commit `.env` files to version control
- Use Google Cloud Secret Manager for production secrets
- Rotate API keys regularly

### Container Security
- The Docker image runs as a non-root user (`appuser`, UID 1001)
- Use read-only file systems where possible
- Scan images with `docker scout` or `trivy` before deployment

### Network Security
- Restrict CORS origins to known domains
- Use HTTPS/TLS in production (Cloud Run handles this automatically)
- Enable VPC Service Controls on Google Cloud

### API Security
- Validate all inputs with Pydantic models
- Implement rate limiting on all endpoints
- Use API keys for service-to-service authentication

### MongoDB Atlas
- Use IP allowlisting
- Enable audit logging
- Use least-privilege database users

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported versions
4. Release patches as soon as possible

Thank you for helping keep RegOps Shield and our users safe!

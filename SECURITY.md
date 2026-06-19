# Security Policy

## Supported Versions

The supported security scope for `django-rest-apis` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Sample Django App for Twitter showcasing OAuth and simple REST API calls.

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/django-rest-apis` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a Python web API or service project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: requirements.txt. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

For this Django sample, missing Twitter access tokens should fail with an explicit Django configuration error before an API client is constructed.
Expected Twitter API errors should render stable generic messages and must not
expose raw provider exception details to authenticated users.
Production settings must always mark session and CSRF cookies secure; local
debug mode may opt in when it is served over HTTPS.
GitHub Actions resolves and verifies absolute root-owned host tools, then runs
the canonical checker and independent mutation tests in separate read-only
containers before explicit absolute `make -f Makefile` coverage
on Python 3.10, 3.12, and 3.14 with commit-pinned
actions, read-only repository access, and bounded execution. CI deliberately
does not install the unsupported Django 1.6-era dependency set and does not persist checkout credentials
after source retrieval. The checker freezes the
complete reviewed workflow and Makefile bytes. It also uses recursive no-follow
`lstat` traversal to enforce exact path/type inventories under
`.github/workflows` and `.github/actions`, rejecting every symlink and
non-regular entry; the current local-action inventory is empty and its root is
absent. `PYTHON` is
non-overridable in the reviewed Makefile. Any legitimate workflow,
local-action, or Makefile change requires a reviewed canonical contract update
in both checker and independent tests before it can pass verification.
The hosted integrity step requires a clean tracked tree and snapshots exact file
blobs and permission modes, index entries, and committed tree identity. Both
prepared copies are byte/mode validated, and the directly executed baseline
must retain its executable bit. Candidate tests receive only
a read-only test copy in a non-root, no-network, capability-free container and
cannot access the source, verifier, snapshot, or host tools. Separate verifier
containers use read-only mounts to validate source state before and after the
Make container. Python startup paths/user site and GNU Make environment inputs,
including `GNUMAKEFLAGS`, are removed. `GNUmakefile`, lowercase `makefile`, includes introduced by changing
the canonical Makefile, and alternate Make roots are rejected or bypassed by
the explicit absolute `-C`/`-f` invocation.
The Python matrix validates dependency-free source contracts; it is not
evidence that the historical Django runtime is compatible with those Python
releases or free from known dependency vulnerabilities.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.

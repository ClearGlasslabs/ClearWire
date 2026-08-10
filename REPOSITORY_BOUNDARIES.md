# ClearWire Repository Boundaries

## Purpose

ClearWire follows a strict public/private repository separation model. Public code and commercial presentation assets may live in this repository. Proprietary commercial systems, privileged infrastructure, internal operations, customer-specific integrations, credentials, secrets, and sensitive analytics must not be committed here.

---

## PUBLIC — `company-website`

**Visibility:** Public

Approved content:

- Landing pages
- Product descriptions
- Public demos
- Documentation
- Case studies approved for public release
- Selected open-source components

Public repositories must contain only information that ClearGlass is prepared to disclose permanently. Do not commit credentials, API keys, customer data, private environment files, privileged endpoints, internal architecture secrets, or proprietary commercial logic.

---

## PRIVATE — `company-core`

**Visibility:** Private

Required content:

- Proprietary algorithms
- Automation agents
- Revenue systems
- Backend/API implementations that expose commercial logic
- Infrastructure source and service topology
- Customer integrations
- Internal analytics
- Commercial intellectual property

This repository is the protected product and IP boundary. Access should follow least privilege and be limited to personnel who require it.

---

## PRIVATE — `company-ops`

**Visibility:** Private

Required content:

- Deployment configuration
- Internal workflows
- Business intelligence
- Privileged infrastructure

Operational credentials and secrets must remain in approved secret-management systems and GitHub encrypted secrets, not committed to source control.

---

## Classification Rule

Before committing a file, classify it using this decision rule:

1. If disclosure would not materially damage ClearGlass, its customers, security posture, revenue model, or competitive advantage, it may qualify for `company-website`.
2. If it implements proprietary product behavior, automation, monetization logic, customer-specific functionality, or commercial IP, place it in `company-core`.
3. If it controls deployment, internal operations, privileged access, production topology, business intelligence, or administrative workflows, place it in `company-ops`.
4. If classification is uncertain, default to **PRIVATE** until reviewed.

---

## Non-Negotiable Public-Repository Exclusions

Never commit the following to a public repository:

- Passwords, tokens, API keys, private keys, certificates, or session secrets
- `.env` files containing real values
- Customer personal information or confidential customer records
- Private database dumps or production logs
- Internal-only endpoints or privileged network information
- Proprietary algorithms intended to remain commercial IP
- Internal financial, pricing-strategy, revenue-operations, or business-intelligence data
- Production deployment credentials or privileged infrastructure configuration

---

## Target Architecture

```text
PUBLIC
company-website
├── landing pages
├── product descriptions
├── public demos
├── documentation
├── case studies
└── selected open-source components

PRIVATE
company-core
├── proprietary algorithms
├── automation agents
├── revenue systems
├── backend/API
├── infrastructure
├── customer integrations
├── internal analytics
└── commercial IP

PRIVATE
company-ops
├── deployment configuration
├── internal workflows
├── business intelligence
└── privileged infrastructure
```

## Enforcement

Repository visibility is the security boundary. GitHub does **not** provide private folders inside a public repository. Therefore `company-core` and `company-ops` must be separate private repositories rather than directories inside ClearWire.

Any sensitive material discovered in ClearWire should be migrated to the appropriate private repository and, where credentials or secrets were exposed, rotated immediately before the public copy is removed from active history.
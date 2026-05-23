# IP-Secure Scanner

Reduce intellectual property, security, and supply-chain risk in AI-assisted codebases.

A GitHub-native workflow that classifies repository assets, detects secrets, flags license-header issues, verifies dependencies, and produces structured audit logs.

## Overview

IP-Secure Scanner is designed for teams adopting AI-assisted development who need operational controls around provenance, security, authorship evidence, and dependency hygiene.

The scanner runs as a GitHub Actions workflow and produces timestamped JSON audit logs for every execution.

## Integrated Controls

- Asset classification
- Secret detection
- Dependency verification
- License-header review
- Audit logging
- GitHub Actions enforcement

## Security Objectives

The workflow supports:

- Trade-secret protection
- AI provenance review
- Supply-chain reduction
- Human oversight documentation
- Pull-request compliance visibility

## Repository-Specific Hardening

This repository already excludes sensitive files through `.gitignore`, including `.env`, credentials, certificates, and local configuration artifacts. fileciteturn5file0L3-L3

The repository also uses:

- Ruby 3.4.3 fileciteturn11file0L3-L3
- Rails 7.1.6 fileciteturn6file0L3-L3
- Node.js 22.x tooling fileciteturn7file0L3-L3

The scanner workflow was tuned for both Bundler and npm dependency ecosystems present in this codebase.

## Disclaimer

This workflow is a technical safeguard layer and does not replace legal review, security review, or formal compliance programs.

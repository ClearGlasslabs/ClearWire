# GitHub Actions remediation report

## Executive decision

This audit covers every file in `.github/workflows` as of 2026-07-26. All 15 files parse as YAML, but no workflow is approved for unattended execution yet because every external action is referenced by a mutable major-version tag. The repair order is:

1. Keep the IP-Secure Scanner fail-closed. This change is included in this remediation.
2. Pin every action to an owner-verified full commit SHA through a reviewed dependency update. Mutable tags are intentionally not replaced with unverified hashes.
3. Put the five issue/PR AI triage workflows and the repair agent behind governance controls before execution.
4. Review the protected-environment approval and secret scope used by `tests.yml` before allowing fork code to run.
5. Run read-only validation workflows first, then state-changing triage workflows in dry-run mode.

No GitHub Pages workflow or direct deployment workflow exists. `tests.yml` can unblock an external Buildkite deployment, but only after both test matrices pass, only for a push to `main`, during the weekday deployment window, and when the feature secret equals `true`.

## Shared supply-chain finding

All workflows that use actions reference mutable tags such as `@v4`, `@v7`, or `@v1`. This is valid GitHub Actions syntax, but it does not meet the repository's production safety gate. Pin each reference to a reviewed 40-character commit SHA and retain the release tag in a comment. Dependabot or Renovate should then update those hashes through pull requests. Until that governance change lands, the workflows below are not explicitly marked safe to execute.

The action inventory is:

- `actions/cache@v4`
- `actions/checkout@v4` and `actions/checkout@v6`
- `actions/github-script@v7`
- `actions/setup-node@v4`
- `actions/setup-python@v6`
- `actions/upload-artifact@v4`
- `anthropics/claude-code-action@v1`
- `nick-fields/retry@v3`
- `ruby/setup-ruby@v1`
- `useblacksmith/setup-docker-builder@v1`

## Workflow inventory and classification

### `.github/workflows/agent.yml` — unsafe; governance required

- **Trigger:** manual `workflow_dispatch` with `mode` and `scope`; serialized by a global concurrency group.
- **Permissions:** workflow default `contents: read`; the repair job elevates to contents and pull-request write, Actions read, and OIDC write.
- **Secrets:** `ANTHROPIC_API_KEY` and the generated `GITHUB_TOKEN`.
- **Job/steps:** checkout, then Claude repair agent. No cache, artifact, environment, or deployment target.
- **Risk:** repository-controlled `PROMPT.md` is an instruction source for a write-capable agent; `id-token: write` is unnecessary; mutable actions and broad git/PR tools permit autonomous commits and pushes.
- **Required patch:** remove OIDC, split dry-run and fix jobs, make dry-run read-only, bind fix mode to an approval-protected environment, pin actions, and constrain the prompt/tool contract to a fixed trusted policy. Keep all PRs draft and prohibit direct default-branch writes.

### `.github/workflows/artemis-revenue-agent.yml` — valid but needs improvement

- **Trigger:** relevant pull requests, pushes to `main`, and manual dispatch; ref-scoped cancel-in-progress concurrency.
- **Permissions:** contents read.
- **Job/steps:** Python 3.12 setup with pip cache, editable test dependency install, pytest, and import smoke test. No secrets, artifacts, environment, or deployment.
- **Risk:** mutable action tags and an unbounded dependency resolution from `pyproject.toml` can drift.
- **Required patch:** pin action SHAs and install from a reviewed lock or constraints file with hashes. The workflow is otherwise fail-fast and path-correct.

### `.github/workflows/auto-merge-gate.yml` — valid but needs improvement

- **Trigger:** selected `pull_request_target` lifecycle events.
- **Permissions:** contents read, pull-request write, and status write.
- **Job/steps:** trusted base checkout, head fetch for diff only, signer/label metadata lookup, Ruby gate, and label/status publication. No secrets beyond `github.token`, cache, artifact, environment, or deployment.
- **Risk:** mutable actions. The status is deliberately always green; branch protection must therefore consume the eligibility label through a separate trusted merge policy or the status can be misread as approval.
- **Required patch:** pin actions, add a job timeout, and document/test the external policy that requires the eligibility label. Continue never executing PR code in this workflow.

### `.github/workflows/close-non-compliant-issues.yml` — unsafe; governance required

- **Trigger:** newly opened issues, serialized per issue.
- **Permissions/secrets:** contents read, issues write, OIDC write; Claude OAuth and `GITHUB_TOKEN`.
- **Job/steps:** collaborator/state check, trusted default-branch checkout, AI classification and optional comment. No cache, artifact, environment, or deployment.
- **Risk:** attacker-controlled issue text reaches a write-capable model; OIDC is unnecessary; action references are mutable.
- **Required patch:** remove OIDC, separate classification from mutation, emit a structured decision artifact, and require deterministic validation or human approval before commenting. Pin actions.

### `.github/workflows/close-non-compliant-prs.yml` — unsafe; governance required

- **Trigger:** external PR opened via `pull_request_target` only.
- **Permissions/secrets:** contents read, pull-request write, OIDC write; Claude OAuth and `GITHUB_TOKEN`.
- **Job/steps:** trusted base checkout and AI review/comment. No PR-head checkout, cache, artifact, environment, or deployment.
- **Risk:** PR title/body/file metadata is untrusted model input combined with a write token. OIDC is unnecessary and actions are mutable.
- **Required patch:** use a read-only classification job and approval-gated comment job, remove OIDC, validate structured output, and pin actions.

### `.github/workflows/close-non-english-issues.yml` — unsafe; governance required

- **Trigger:** issue opened, serialized per issue.
- **Permissions/secrets:** contents read, issues write, OIDC write; Claude OAuth and `GITHUB_TOKEN`.
- **Job/steps:** checkout and AI language detection that can comment and close. No cache, artifact, environment, or deployment.
- **Risk:** untrusted prose drives a destructive close action; there is no collaborator exemption or approval; OIDC is unnecessary and actions are mutable.
- **Required patch:** change the first phase to label/recommend only, exclude collaborators, require human approval to close, remove OIDC, and pin actions.

### `.github/workflows/close-questions-issues.yml` — unsafe; governance required

- **Trigger:** issue opened, serialized per issue.
- **Permissions/secrets:** contents read, issues write, OIDC write; Claude OAuth and `GITHUB_TOKEN`.
- **Job/steps:** collaborator/state check and AI classification that can comment and close. No cache, artifact, environment, or deployment.
- **Risk:** prompt injection and false-positive closure from attacker-controlled issue content; unnecessary OIDC and mutable actions.
- **Required patch:** separate read-only classification from an approval-gated close, validate a strict decision schema, remove OIDC, and pin actions.

### `.github/workflows/close-stale-issues.yml` — valid but needs improvement

- **Trigger:** hourly schedule and manual dispatch; globally serialized.
- **Permissions:** issues write only.
- **Job/steps:** deterministic pagination, stale labeling, warning, and closure after grace. No secrets, checkout, cache, artifact, environment, or deployment.
- **Risk:** mutable `github-script`; hourly mutation creates a large operational blast radius; there is no dry-run input.
- **Required patch:** pin the action, add a default-true manual dry-run option, and run scheduled mutation only after a monitored canary period. Existing timeout and pagination are sound.

### `.github/workflows/close-stale-prs.yml` — valid but needs improvement

- **Trigger:** hourly schedule and manual dispatch; globally serialized.
- **Permissions:** pull requests and issues write.
- **Job/steps:** deterministic pagination, activity calculation, stale labeling, warning, and closure. No secrets, cache, artifact, environment, or deployment.
- **Risk:** mutable action, broad scheduled mutation, and no dry-run input.
- **Required patch:** pin the action and add dry-run/canary controls before rollout.

### `.github/workflows/close-support-issues.yml` — unsafe; governance required

- **Trigger:** issue opened, serialized per issue.
- **Permissions/secrets:** contents read, issues write, OIDC write; Claude OAuth and `GITHUB_TOKEN`.
- **Job/steps:** collaborator/state check and AI-generated support guidance comment. No cache, artifact, environment, or deployment.
- **Risk:** untrusted issue input reaches a write-capable model; OIDC is unnecessary and actions are mutable.
- **Required patch:** classify without a write token, validate fixed response content in a deterministic second job, remove OIDC, and pin actions.

### `.github/workflows/enforce-review-cycles.yml` — valid but needs improvement

- **Trigger:** every six hours and manual dispatch with dry-run; globally serialized.
- **Permissions:** pull requests and issues write.
- **Job/steps:** deterministic review-age computation and optional reminder comments. No secrets, cache, artifact, environment, or deployment.
- **Risk:** mutable action; scheduled executions cannot select dry-run; review pagination is limited to one 100-item page.
- **Required patch:** pin the action, paginate reviews/comments where correctness requires it, and introduce a repository-variable kill switch for scheduled comments.

### `.github/workflows/ip-secure-scanner.yml` — broken; patched in this change

- **Trigger:** pushes and pull requests for `main`, `develop`, and `staging`, plus pushes to its bot branch.
- **Permissions:** contents read only after this patch.
- **Job/steps:** checkout, Node and Ruby setup, secret scan, npm/Ruby dependency audits, license/provenance review, audit JSON, artifact upload. No secrets, cache, environment, or deployment.
- **Root cause:** dependency installation and audit failures were suppressed with `|| true`, so the security job could report success after finding high-severity vulnerabilities or a broken dependency graph. PR file selection used `HEAD^1`, which is fragile for merge commits and nonstandard checkout histories. Artifacts were skipped on early failure.
- **Applied patch:** compare the event's exact base/head SHAs, install deterministically with `npm ci --ignore-scripts`, fail on npm/Bundler audit errors, remove unused write permissions, add a timeout, and always upload a run-unique 30-day audit artifact while failing when no audit file exists.
- **Remaining patch:** pin action SHAs. Until then, do not mark the workflow safe for execution under the stated gate.

### `.github/workflows/label-new-issues.yml` — valid but needs improvement

- **Trigger:** issue opened, serialized per issue.
- **Permissions:** issues write only.
- **Job/steps:** deterministic addition of the `planning` label. No secrets, cache, artifact, environment, or deployment.
- **Risk:** mutable action; a missing repository label makes the job fail without a clear remediation summary.
- **Required patch:** pin the action and either provision the label as repository configuration or create it deterministically with the intended color/description.

### `.github/workflows/stripe-security.yml` — valid but needs improvement

- **Trigger:** pull requests, pushes to `main`/`master`, and manual dispatch.
- **Permissions:** contents read.
- **Job/steps:** checkout, credential-pattern scan, and contract log. No secrets, cache, artifact, environment, or deployment.
- **Risk:** mutable checkout; full-tree `git grep` finds committed patterns but does not scan history, encoded values, or all provider token formats. The account identifier in the contract is non-secret but creates unnecessary coupling.
- **Required patch:** pin checkout and treat this as a narrow defense-in-depth check, not a replacement for GitHub secret scanning. Add a timeout.

### `.github/workflows/tests.yml` — unsafe; governance required before fork execution

- **Trigger:** every branch push except production tags and `pull_request_target`.
- **Permissions:** contents read globally.
- **Jobs/steps:** protected CI gate; Node and Ruby lint; Docker image build/cache/push; 30-way fast and 50-way slow RSpec matrices with logs/screenshots; optional Buildkite unblock after both matrices. Docker Hub and private gem secrets build images; Knapsack tokens split tests; Buildkite secrets govern the external unblock. Fork PRs bind to `ci-protected`; internal PR target runs are no-ops because pushes already test them.
- **Artifacts/caches:** asset precompile cache; flaky logs always; failure-only Capybara and test logs. No GitHub deployment environment; `ci-protected` is an approval/security boundary. The external target is Buildkite pipeline `gumroad-inc/<secret slug>`.
- **Risk:** after protected-environment approval, untrusted fork code is checked out and executed in jobs that receive Docker Hub/private gem/Knapsack secrets and can push content-addressed images. Mutable third-party retry/build actions amplify supply-chain risk. External Buildkite unblock is deployment-adjacent and has no GitHub environment binding.
- **Required patch:** pin every action; build fork code without repository secrets or image push, then run privileged image publication only for trusted refs; bind Buildkite unblock to a deployment approval environment with narrowly scoped token; validate Buildkite response JSON without logging sensitive response bodies; add job timeouts and artifact digest/provenance checks.

## Corrected scanner execution path

The corrected scanner now follows this path:

1. Check out the triggering revision with full history.
2. Calculate changed PR files from the immutable event base/head SHAs.
3. Fail immediately on a matching credential pattern.
4. Install the exact npm lockfile without lifecycle scripts, validate the dependency tree, and fail on high-severity advisories.
5. Install the locked Ruby bundle and fail on `bundler-audit` findings.
6. Generate audit metadata.
7. Upload the audit directory even when a preceding check fails, using a run-unique artifact name, 30-day retention, and strict missing-file behavior.

## Validation and rollout runbook

### Before any execution

1. Parse all YAML files with a YAML 1.2-aware parser and run `actionlint`.
2. Run a policy check that rejects every non-local `uses:` value not pinned to a 40-character SHA.
3. Confirm effective workflow/job permissions through GitHub's workflow UI.
4. Confirm required secrets exist by name only; never print their values.
5. Confirm `ci-protected` requires named reviewer approval and does not expose secrets before approval.
6. Confirm branch protection and merge policy consume the auto-merge eligibility label correctly.

### Safe staged rollout after SHA pinning

1. Manually run `stripe-security.yml`; it is read-only.
2. Open a test-only Artemis PR to exercise `artemis-revenue-agent.yml` without secrets.
3. Run IP-Secure Scanner on a synthetic clean branch and a disposable branch containing a fake matching token; require success and failure respectively, and verify both artifacts.
4. Exercise `auto-merge-gate.yml` against an ineligible test PR and verify it changes only its label/status.
5. Run stale/review workflows in dry-run mode after those controls are added.
6. Run AI workflows only after the classifier/mutator split and protected approval are implemented.
7. Run the full tests workflow first on a trusted branch. Do not test the Buildkite unblock unless release management explicitly authorizes it and rollback ownership is assigned.

### Rollback

Revert the remediation commit to restore the previous scanner behavior. Do not delete audit artifacts; preserve them for incident review. If the fail-closed dependency audits expose an accepted advisory, document a time-bounded exception in dependency policy rather than restoring `|| true`.

## Monitoring and weekly health checks

After rollout, monitor job failure rate, queue time, runner saturation, artifact upload success, cache hit rate, audit finding counts, issue/PR false-positive mutation rate, protected-environment approvals, Docker image provenance, and Buildkite unblock attempts.

Every week:

- Verify action SHA updates and upstream release notes.
- Run YAML/actionlint and least-privilege policy checks.
- Verify required secret names, ages, and owners without reading values.
- Sample audit artifacts for completeness and retention.
- Review AI triage false positives and prompt-injection attempts.
- Test rollback on a disposable branch.
- Review runner image changes and third-party action ownership.
- Confirm branch protection, environment reviewers, concurrency, and deployment-window controls have not drifted.

# ClearGlassInc.github.io — Workflow Migration

Drop-in replacement set for `.github/workflows/`. Reduces estimated
monthly Actions usage from **~334 minutes** to **~120–160 minutes**
(50–65% reduction) without removing security coverage or the
production deploy path.

## TL;DR

| Action | Why |
|---|---|
| Delete `deploy-pages.yml` | Duplicate of pages workflow |
| Delete `pages-deploy.yml` | Duplicate |
| Delete `jekyll-docker.yml` | Duplicate, custom Docker not needed for stock Jekyll |
| Add `pages.yml` (provided) | Single authoritative deploy |
| Replace `codeql.yml` | Was running on every push; now PR + push-to-main + weekly |
| Replace `python-tests.yml` | Adds path filter — only runs when Python files change |
| Replace `site-integrity.yml` | Adds path filter — only runs on site files |
| Replace `site-reliability.yml` | Schedule-only, was running on push |
| In Pages settings: switch source to "GitHub Actions" | Removes the auto-generated `pages-build-deployment` runs |

## Step-by-step migration

### 1. Switch GitHub Pages source

In the repo, go to **Settings → Pages → Build and deployment → Source**
and change it from **"Deploy from a branch"** to **"GitHub Actions"**.

This single change eliminates the auto-generated
`pages-build-deployment` runs that show up in your Actions usage but
have no `.yml` file in the repo. They're controlled by the Pages
setting, not by a workflow you can edit.

**Don't skip this step** — if you leave it on "Deploy from a branch"
AND add the new `pages.yml`, you'll have two pipelines fighting each
other.

### 2. Drop in the new workflows

Copy the four files in this directory's `.github/workflows/` into the
repo's `.github/workflows/`:

- `pages.yml`
- `codeql.yml`
- `python-tests.yml`
- `site-integrity.yml`
- `site-reliability.yml`

### 3. Delete the obsolete files

```
git rm .github/workflows/deploy-pages.yml
git rm .github/workflows/pages-deploy.yml
git rm .github/workflows/jekyll-docker.yml
```

(Keep these as `git rm` — clean removal, easy to revert via git history.)

### 4. Verify before merging

On a new branch:

```bash
git checkout -b chore/optimize-actions
# copy in new files, git rm old ones
git add .github/workflows/
git commit -m "Optimize GitHub Actions: consolidate Pages, scope CodeQL, add path filters"
git push -u origin chore/optimize-actions
```

Open a PR. Watch which workflows trigger:

- `python-tests.yml` should NOT run (no .py changed)
- `site-integrity.yml` should NOT run (no site files changed yet — only workflow files)
- `codeql.yml` SHOULD run (PR target)
- `pages.yml` should NOT run (only triggers on push to main)

If that matches, merge to main. On the main-branch push:

- `pages.yml` SHOULD run and deploy
- `codeql.yml` SHOULD run
- `python-tests.yml` SHOULD NOT run
- `site-integrity.yml` SHOULD NOT run

After deploy, hit your live site URL — confirm it loaded the new build.

## What changed and why

### Pages deployment (the big win)

You had 4 pipelines doing the same job:

- `pages-build-deployment` (auto-generated, runs on every main push)
- `deploy-pages.yml` (manual workflow, also deploying)
- `pages-deploy.yml` (manual workflow, also deploying)
- `jekyll-docker.yml` (custom Docker build, also deploying)

This is why you see "duplicated Pages deploys ~28 times each."
Consolidating to one `pages.yml` saves an estimated 60–100 min/month.

### CodeQL (124 → ~30–50 min/month)

The old config likely ran CodeQL on every push to every branch. The
new config:

- Push to `main` only (not feature branches)
- PRs targeting `main` (catches issues before merge)
- Weekly scheduled scan (keeps Security tab fresh)
- Path-ignore for `.md` and asset-only changes
- `cancel-in-progress: true` so older runs die when newer commits land

If your site is pure HTML/CSS/Markdown with no JavaScript or Python,
**you can delete `codeql.yml` entirely** — there's nothing for CodeQL
to analyze. Static Jekyll sites don't need code scanning. Check your
Security tab: if CodeQL has been finding zero alerts for months on
this repo, that's a sign it's not the right fit and the workflow is
pure cost.

### Path filters

Both `python-tests.yml` and `site-integrity.yml` previously ran on
every commit. Now they only run when their relevant files change. For
a site repo with frequent content commits, this typically cuts those
workflow runs by 70–80%.

### Concurrency

Every workflow now cancels older in-progress runs when a newer commit
lands on the same ref — except `pages.yml`, which finishes any
in-flight deploy to avoid leaving the site half-published.

### Permissions

Every workflow now declares an explicit `permissions:` block at the
least-privilege level. The default `GITHUB_TOKEN` is no longer
write-everything by accident.

### Timeouts

Every job has a `timeout-minutes` — kills runaway jobs before they
eat hours.

## Estimated savings

| Workflow | Before (min/mo) | After (est) | Savings |
|---|---:|---:|---:|
| CodeQL | 124 | 35 | -89 |
| Pages duplicates (3 redundant) | ~80 | 0 | -80 |
| `pages-build-deployment` (auto) | ~30 | 0 | -30 |
| python-tests (no path filter) | ~40 | ~12 | -28 |
| site-integrity (no path filter) | ~35 | ~10 | -25 |
| site-reliability (was on push) | ~25 | ~3 | -22 |
| **Total** | **~334** | **~120–160** | **~50–65% reduction** |

These are estimates from the data you provided; actuals depend on
commit cadence and what changes per commit.

## Things to verify after merging

1. `https://clearglassinc.github.io/` still loads the same site
2. Pushing a commit that only touches a `.md` file deploys the site
   (Jekyll content is real content) but does NOT trigger CodeQL,
   python-tests, or site-integrity unless the .md is in a watched path
3. The Security tab still shows CodeQL results (it'll show "last
   scanned" within a week)
4. Actions usage for the next month drops materially

## Risks and assumptions

- **Assumption:** the site is a stock Jekyll build with no custom
  pre-processing that the deleted `jekyll-docker.yml` was doing. If
  that workflow was running a custom plugin chain, port the relevant
  steps into `pages.yml`.
- **Assumption:** there is Python code in the repo that warrants
  `python-tests.yml`. If it's purely a Jekyll site with no Python,
  delete the workflow entirely.
- **Risk:** the path filters are conservative. If you publish content
  from `_drafts/`, add it to the path lists in `pages.yml` and
  `site-integrity.yml`. (Default Jekyll doesn't publish drafts.)
- **Risk:** if you don't switch Pages source to "GitHub Actions" in
  Settings → Pages, the new `pages.yml` will run alongside the
  auto-generated `pages-build-deployment` and you'll see double
  deploys. **Do step 1.**

## What I cannot do from here

- Open a PR on `ClearGlassInc/ClearGlassInc.github.io` — the GitHub MCP
  tools available in this session are scoped to a different repo.
- Read your existing workflows to confirm I'm not missing a
  customization. If any of the old workflows had non-obvious logic
  (custom Jekyll plugins, secret-using deploy steps, signed commits),
  paste them in and I'll merge that logic into the new files before
  you ship.

If you paste the contents of your current `.github/workflows/`, I'll
do a precise diff-level merge instead of a generic replacement.

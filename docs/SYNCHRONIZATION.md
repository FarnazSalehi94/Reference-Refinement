# Safe research synchronization

## Policy

**PR #1 merged the initial reorganization on 2026-11-10. The owner approved correcting the latest-completed BN evaluation status, checks, commit, normal push to the existing documentation branch and a pull request; merging the new PR is not authorized.** For future research milestones, update eligible documentation/scripts/verified results/figures, propose the reviewed commit and push, and obtain explicit approval before publication. Commands below remain approval-gated steps—not standing authorization to run them. Persistent instructions are in [AGENTS.md](../AGENTS.md) and the parent HPC project instructions.

Curation is separate from computation. Never point Git at the large assembly tree. No HPC job pushes to GitHub. Import is allowlist-only, does not delete files automatically, and never edits scientific sources. `configs/evaluation_policy.json` records jobs 2871273/2871274/2871275 as the latest completed BN k-mer/reference/Merqury evaluation, dated 2026-11-09, with preliminary scientific interpretation and further validation planned. Older historical analyses remain separate. Do not classify completed work as unfinished/merely historical because validation is planned, or infer later job IDs/results. Numerical outputs remain unchanged. Policy changes require explicit scientific review and matching generator/tests.

Scheduler success alone is insufficient for corrected Hi-C imports: a successful corrected job, validation report, count/sample checks and converged weights are required. New analysis objectives or results must be added deliberately to `configs/import_allowlist.json`.

Exact source snapshots may contain HPC usernames/paths and public accessions; review for privacy before publication. The heuristic scanner cannot prove absence of sensitive information or biological misinterpretation.

## One-command local update

From this curated checkout:

```bash
python3 scripts/sync_project.py plan --source /moosefs/salehi/ref-refine/assemblies
python3 scripts/sync_project.py apply --source /moosefs/salehi/ref-refine/assemblies
```

`apply` is the regular local synchronization command. It imports selected small files, updates current job states in PROJECT_STATUS.md, rebuilds the verified assembly comparison/README table and figure index, and records exact source hashes. It does NOT stage, commit, push, submit jobs or run analyses. Repeating it without source/status changes is idempotent. It refuses locally edited managed-file collisions, oversized/unsafe inputs, missing evidence, incomplete required results and disappearing managed sources. No automatic deletion or conflict resolution occurs.

When accounting records are unavailable, stop and update the evidence policy deliberately—never invent completed states. Approximate dataset totals and planned-analysis text remain manually curated; this tool is not a scientific interpretation engine. If a new analysis finishes outside the configured objectives, add reviewed source/destination/evidence entries before import.

## Review, stage, commit

```bash
git status --short
git diff --stat
git diff -- README.md PROJECT_STATUS.md
# Stage explicit reviewed paths; avoid blind git add .
git add -- AGENTS.md README.md PROJECT_STATUS.md assembly analyses configs metadata results figures docs scripts .github .gitignore .gitattributes
python3 scripts/sync_project.py check
git diff --cached --check
git diff --cached --stat
python3 scripts/sync_project.py commit --message "docs: clarify latest completed BN quality evaluation and preliminary interpretation"
```

Inspect the full staged diff and manually confirm biological claims/figure labels. Binary figure content needs visual review. Use specific messages, e.g. `methods: document 1-based Cooler correction` or `results: add validated Hi-C maps for revision ...`; avoid `update files`.

The local pre-commit hook is enabled with:

```bash
git config --local core.hooksPath .github/hooks
```

The guard scans actual staged blobs, rejects files over 5 MiB, data/binary formats, symlinks, common credential patterns and active SVG content. CI checks tracked content and current local documentation links. Historical source snapshots are excluded from the local-link check, not the safety scan. Do not bypass hooks or assume scanning is exhaustive.

## Approved publication only

The initial `curate/bn-reference-20261110` branch was merged through PR #1. The current correction branch is `research/documentation-preliminary-kmer-20261110`, based on the merged main. Push only explicitly approved, reviewed commits; verify actual remote state and do not merge the new PR:

```bash
python3 scripts/sync_project.py push --approve-push
```

The tool permits only `curate/*` or `research/*` review branches, accepts only the exact approved repository URL via HTTPS or SSH, verifies the existing remote, requires a clean working tree, fetches origin, refuses if origin/main is no longer an ancestor, scans every outgoing commit tree, and uses a normal non-forced push with an explicit branch ref. A non-fast-forward is a stop for review, not a reason to force-push. Open a GitHub pull request into main and review its diff before merging. There is no direct-main push path in this tool.

After merging an approved PR, start the next update from current main rather than stacking unrelated work on an old branch:

```bash
git fetch origin
git switch -c research/descriptive-update-name origin/main
```

SSH authentication and branch push were verified for this repository. SSH keys authenticate Git operations, not pull-request REST API calls. GitHub CLI/API authentication must be configured separately to create PRs programmatically; never assume that a successful branch push created a PR. Use GitHub's credential helper or authenticated SSH after configuration if needed; never put tokens in remote URLs, files, shell history or commits.

## HTTPS trust repair

This HPC Git executable is from a Guix profile and failed with no CAfile configured. The existing system CA bundle successfully verified GitHub. A repository-local setting was applied (not SSL bypass):

```bash
git config --local http.sslCAInfo /etc/ssl/certs/ca-certificates.crt
```

Do not disable `http.sslVerify`. Other machines should use their own trusted system bundle/credential setup rather than copying HPC paths blindly.

## Failures

If a source disappears, a result gate fails, or a managed file was edited locally, stop. Preserve the current diff and reconcile intentionally; do not overwrite local work or regenerate expensive data. Corrected matrices remain on HPC; only selected validated small reports/figures are eligible for Git.

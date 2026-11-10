# Persistent instructions for research-repository maintenance

## Identity and scope

Maintain the existing repository `https://github.com/FarnazSalehi94/Reference-Refinement`; do not create a replacement or discard its history. The curated checkout is separate from `/moosefs/salehi/ref-refine/assemblies/`, which contains large scientific inputs/outputs. Never modify those scientific originals as part of synchronization.

Initial-review branch: `curate/bn-reference-20261110`, based on recovered main commit `bfce107a802c7ce40a5df68a7bc7027b4c1fe576`. Existing commits must remain ancestors. On 2026-11-10 the owner approved committing the reviewed 84-file reorganization, a normal push of this branch, and opening a pull request into main. **Merging is not authorized.** Verify actual Git/remote state rather than assuming publication succeeded. For future updates, propose the reviewed commit and push after every meaningful completed research task and obtain explicit approval before either action. A prepared/staged diff is not a commit, and approval to commit is not approval to push.

## After each meaningful research milestone

1. Inspect actual outputs and SLURM accounting. Distinguish completed, failed, running and planned work. Do not interrupt jobs or launch/repeat scientific analyses during repository maintenance.
2. Read `docs/SYNCHRONIZATION.md`, `PROJECT_STATUS.md` and `configs/import_allowlist.json`.
3. From this checkout preview changes:

   ```bash
   python3 scripts/sync_project.py plan --source /moosefs/salehi/ref-refine/assemblies
   ```

4. Review eligibility and scientific evidence. For a new objective/result, explicitly add reviewed source/destination/evidence entries before import. No automatic globbing of arbitrary HPC outputs.
5. Apply appropriate local updates within approved scope:

   ```bash
   python3 scripts/sync_project.py apply --source /moosefs/salehi/ref-refine/assemblies
   ```

   This updates curated files, PROJECT_STATUS.md, verified comparison tables, README metric/status blocks, figure indexes and source hashes. It does not stage, commit, push or submit jobs.
6. Inspect all changes, including image content. Explain observations separately from interpretation. Review privacy manually; heuristic secret scanning is not a guarantee.
7. Stage only explicitly reviewed paths, preserving any unrelated user work. Run:

   ```bash
   python3 scripts/sync_project.py check
   git diff --cached --check
   git diff --cached --stat
   ```

8. Report proposed changes and remaining issues. Request separate commit/push approval while the current restriction remains in effect. Only after approval use a meaningful commit message and the documented explicit push command. Never auto-push intermediate job outputs.

## Git safeguards

- Use `curate/*` or `research/*` review branches and pull requests; no direct main push through the update tool.
- Never force-push, rewrite remote history, disable SSL verification, bypass safety hooks, or embed credentials in URLs/files.
- Verified local HTTPS configuration: `http.sslCAInfo=/etc/ssl/certs/ca-certificates.crt`. This machine-specific setting belongs in `.git/config`, not portable scientific configuration.
- A public fetch proves read connectivity, not authenticated write access. Configure a trusted credential helper or authenticated SSH only if needed; never print or commit secrets.
- Respect `.gitignore`, `.gitattributes` and the 5-MiB publication limit. No raw reads, assembly FASTAs/GFAs, alignment/pairs/matrix files, databases, executables, complete logs, private identifiers or credentials.
- Imported snapshots must match their source hashes. Do not silently overwrite locally edited managed files. Resolve conflicts deliberately; no automatic deletion.
- Preserve dated historical notes. A source snapshot may have stale status or old paths; current narrative must identify those limitations.

## Scientific reporting rules

Use verified results only. Hifiasm is **experimental hybrid_v1 0.25.1-r942**, not ordinary hifiasm. The exact build/source commit remains unresolved. Do not claim same-individual sequencing provenance. N50, k-mer completeness and reference span coverage measure different things and do not establish structural correctness.

Hi-C legacy Cooler matrices are excluded. Import corrected maps only with successful corrected-job accounting, finished pairs validation, matrix/contact-count/sample validation and converged balancing. Pretext completion is separate from Cooler success and separate from scientific visual review. Never edit assemblies or scaffold them merely because of repository curation.

No reuse license is established by the historical MIT badge alone; the recovered repository lacked a LICENSE file. Obtain the owner's license decision rather than inventing one.

## Persistent instruction locations

The parent `/moosefs/salehi/ref-refine/AGENTS.md` makes these obligations discoverable from both scientific and curated working trees. This repository's AGENTS.md records the versionable maintenance workflow. Keep them consistent when the owner changes approval policy.

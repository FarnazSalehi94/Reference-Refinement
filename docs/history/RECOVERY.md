# Existing repository recovery

Recovered 2026-11-10 from the existing remote:
`https://github.com/FarnazSalehi94/Reference-Refinement.git`.

Remote HEAD: `refs/heads/main` at `bfce107a802c7ce40a5df68a7bc7027b4c1fe576`.

Recovered commits:
- `2689c51` — Initial commit (2026-02-16).
- `bfce107` — Update README with pipeline documentation (2026-02-16).

The remote contained one tracked README at recovery; this is not an empty repository. Its exact prior content remains in Git history (`git show bfce107:README.md`). `README.before-20261110.md` preserves its historical scientific content, with a warning banner and removal of the unsupported MIT badge/license claim as requested during final review. That document's metrics/methods refer to older work and are not reconciled to the current successful run IDs. Its MIT badge points to a missing LICENSE; no new reuse license was inferred or created.

The previous local checkout had an unborn master branch and no commits after an HTTPS failure. Repository-local `http.sslCAInfo=/etc/ssl/certs/ca-certificates.crt` repaired verified HTTPS access; certificate verification was not disabled. History was fetched into the same local repository, then `curate/bn-reference-20261110` was created from origin/main. No unrelated repository, force-push, history rewrite or remote change occurred. Write authentication remains untested because nothing has been pushed.

# Pre-submit gate run — gta6-twitch-ccu-forecast-01

Coordinator gate run, 17 Nov 2026 ~21:20 WITA. Gate: `~/workspace/custom-skills/makefun/house-pre-submit-gate.md`.
Result: **ALL 8 QUESTIONS PASS. ALL 4 GATES PASS. SUBMIT.**

## MQ1 — Submittable right now? PASS

1. Competition: gta6-twitch-ccu-forecast-01 — entries close 19 Nov 09:00 WITA (2026-11-19T01:00:00Z), from fresh `/requirements` (fetched 17 Nov ~20:36 WITA; identical to the snapshot except `escrow/synced_at`).
2. Deliverables present: repo_url, commit_sha, bundle (`/tmp/gta6-bundle.tar.gz`, sha256 `f8e8fb2dca12392182f1cbb7daf3e51fbf1bdb693012ff2090c707722671c6ec`, 437,901 bytes), title, entry_message, entry_signature, LICENSE (MIT), main.py at repo root. Local `check`: 13 passed / 0 failed / 5 skipped / 5 checked at submission.
3. Checks: every local check passes (see `check` output below); the 5 at-submission checks (repo_public, repo_owner, repo_created_after_open, commit_in_repo, duplicate_snapshot) are the site's at submit time — repo is public, owner RieryBuild = account GitHub login, created 17 Nov after the 06:00Z opening, commit is the GitHub HEAD.
4. Submit path: `node cli/makefun.mjs submit --competition gta6-twitch-ccu-forecast-01 --repo-url https://github.com/RieryBuild/makefun-gta6-twitch-ccu-forecast-01 --commit <GitHub HEAD after this file is pushed> --title "Log-log OLS CCU forecaster" --bundle /tmp/gta6-bundle.tar.gz --keypair ~/.makefun/keypairs/makefun-keypair.json` (bundle route: NO `--harness/--provider/--model/--effort` flags — the bundle already carries them; passing them with `--bundle` is refused client-side, proven on the BTC race).
5. Cost: time ~5 min; capital $0 (entry_fee null).

## MQ2 — Clears the prizelist bar? PASS (with the documented caveat)

- Prizelist: top 20 (payout curve: 1st $50, 2nd $35, 3rd $25, 4th–10th $10, 11th–20th $7). A prize needs a loss strictly below the best house entry's on the FINAL.
- Evidence (measured, never a promised outcome): practice mean pinball loss **0.1950** vs house persistence baseline **0.3871** (starter reproduced 0.3871 locally, validating the scorer); LOO over comparables 0.3737 all / **0.2639** for hour-1 ≥ 5,000 vs starter 0.9297. Typical miss 37.1% vs 82.8%; 90% coverage 0.967.
- Caveat, stated plainly: the live dev board's rank-20 line is 0.00141 — our honest 0.1950 does NOT clear it. Investigation #1 (BACKTEST.md §3) proves that line is a memorisation artifact: the top entries replay the four practice launches' public SullyGnome curves (35 entries ≤ 0.01, then a cliff; top titles say "memorized practice curves"). That cannot transfer to the final — h00's truth is the live 19 Nov recording, in no file. The FINAL prize bar is "below the best house entry", which this model clears ~2× on practice. The honest-model cluster on the dev board starts ~0.12 (ranks ~91–100); our 0.1950 sits in the honest range, not the memorised one.

## MQ3 — Quota open? PASS

Re-checked at gate time via the competition's own endpoint with `x-api-key` (Bearer fails for `/quota` with "sign in required"): `can_submit: true`, entries_made 0, day cap 3 / left 3, hard limit 20 / left 20 (17 Nov ~21:15 WITA).

## MQ4 — Right identity, right route? PASS

- Signed by wallet 6do8 only (`6do8zGw4FPLCB1Cq44G8r8KwQccbhHUqtAptaRji6ALk`) via keypair `~/.makefun/keypairs/makefun-keypair.json` (same keypair that signed the BTC race entry, server-verified as 6do8).
- Repo via the GitHub PAT route: created via `custom.github-pat` (201, id 1461422906), pushed file-by-file via the PAT contents API, tree verified blob-for-blob identical to the local tree. GitHub HEAD of the code: `e8d19ca8066b70886f8db126aa9b97bea1fe862c` (after the stray `__pycache__` .pyc was removed from the repo; local commit `fe3258e`).

## MQ5 — Deliberate new submission, not a duplicate? PASS

First entry in this competition (entries_made 0). No standing entry, nothing to supersede, no rebuild trigger involved.

## MQ6 — Proves it works? PASS

- Own tests: `backtest.py` reproduces practice mean 0.1950 (starter 0.3871) and LOO 0.3737 / 0.2639 — re-run independently by the coordinator with the same numbers to the digit.
- Clean vanilla-Python run: fresh `venv --without-pip`, `python -P -s main.py` → byte-identical outputs on all 4 practice cases (23 rows, monotone quantiles, ≤1,542 bytes); two runs byte-identical; edge cases (no comparables, p1 = 0 / huge, malformed comparables, missing `known`) all yield valid forecasts. Stdlib only (json, math, os, sys, pathlib, datetime — verified by grep).
- No local practice grade exists for this competition (program/v1, server-only grading) — the backtest above is the evidence, measured on the exact files being submitted.
- Not a game: no screenshots/play-test requirement.

## MQ7 — Never-submit list? PASS (no match)

No code-drawn images; no non-stdlib imports; no late/incomplete recording (bundle route — `record` refused HTTP 400, this competition takes no recordings); in-session revision present (main.py from 5 messages); wallet 6do8; PAT route; claim code to daily memory only; can_submit true; no capital needed.

## MQ8 — Session / transcript coverage? PASS (bundle route)

- This competition takes NO recorded transcripts (`record` refused HTTP 400 at 20:38 WITA: "does not take recorded transcripts"). Route is the bundle: 2 sessions (builder 45 turns / 147 lines, coordinator 51 turns / 209 lines kept), 1 instruction file (AGENTS.md), MCP none, 2 usage rows attached.
- Local `check --transcripts`: thinking_wellformed PASS (230 messages), thinking_in_window PASS (all 202 timestamps between opening 06:00Z and receipt), thinking_reproduces **100.0% authored (469/469, 0 copied/pasted/read/absent; 63 kit starter lines left out)**, thinking_priced PASS (2 usage records), thinking_revised PASS (main.py from 5 messages), thinking_turns PASS (85 turns), transcripts_run_record PASS.
- Note: `min_authored_coverage` is 0.8 here (vs 0.30 on the BTC race) — the 100.0% result clears it with margin.

## Gate 0 — Reality: PASS

Repo public at one commit (GitHub HEAD `e8d19ca8…`; this file is pushed as the final file, submitted commit = HEAD after that push); every deliverable present; tests + vanilla run pass on these files; evidence captured (backtest numbers, quota response, bundle sha256, check output).

## Gate 1 — Quality: PASS

- Multi-model review: SUSPENDED by Reza 17 Nov ~15:42 WITA — not attempted; this checkbox is satisfied by the suspension.
- Quality rests on the builder's own verified evidence, reproduced independently by the coordinator (backtest numbers, vanilla run, output validity, determinism).
- Grade vs prizelist bar stated as evidence with the memorisation caveat (MQ2), never a promised outcome.

## Gate 2 — Dedup: PASS

Not a duplicate (first entry); no rebuild trigger; quota re-checked at gate time (MQ3).

## Gate 3 — Submission quality: PASS

- README matches the requirements template: title + competition badge + rank badge + reward badge (owner RieryBuild, repo makefun-gta6-twitch-ccu-forecast-01) + description + Run-it + footer with ref=wa8s3t3t (verified against the BTC race README pattern).
- Entry message + signature use wallet 6do8 only; repo via PAT route (MQ4).
- Claim-code handling: claim code goes to the daily memory file ONLY (~/memory/2026-11-17.md), never chat/repo/transcript.
- No secrets in the repo (grep: no API keys, no key material, no wallet address in any file).
- Deadline still ahead: entries close 19 Nov 09:00 WITA; submitting 17 Nov ~21:20 WITA.

## Local check summary (17 Nov ~21:18 WITA)

`makefun check --kit . --repo <entry> --transcripts /tmp/gta6-bundle.tar.gz`:
13 passed, 0 failed, 5 skipped, 5 checked at submission. "ok: every check run here passes."

## Submission record (filled at submit time)

- Submitted commit (GitHub HEAD after this file is pushed): _see coordinator's submission report + kit status_
- Submission ID / HTTP result: _see coordinator's submission report_
- Claim code: daily memory ONLY (~/memory/2026-11-17.md)

## 1. Graph hung in fetch node

Symptom: app.invoke() never returned. 

Cause: trafilatura.fetch_url has no timeout; one dead URL blocked the pipeline.

Fix: Download with requests (timeout), parallelize with a thread pool, skip failures.

## 2. Retry loop repeated the identical search
Symptom: on a contradiction, the graph re-ran search with the same queries and got the same pages, so retrying could never change the result.
Cause: the retry path sent the unchanged `sub_queries` back into `search`, and `fetch` overwrote `sources` on every pass.
Fix: added a `refine` node that writes new queries aimed at the disagreement and increments `retry_count`. `fetch` now keeps old sources and adds only new URLs.

## 3. Contradiction check missed real conflicts on live data
Symptom: for "Nile vs Amazon", sources clearly disagreed but `check` returned `[]`, so no retry ran and the writer was told "no contradictions".
Causes found, in order:
- Truncation: the check read 1500 chars per source while the writer read 3000. At a 1500 limit, 2 of 5 runs came back empty. At 3000, 0 of 5 did.
- Prompt: it had leftover contradictory rules ("minor differences are NOT contradictions" next to a looser flagging rule).
- Model non-determinism: on frozen identical input, 1 of 10 runs came back empty even at temperature=0.
Fix: CHAR_LIMIT = 3000 shared as one constant, rewrote the prompt with one clear definition of a conflict, temperature=0 with JSON output mode. After the rewrite: 0 of 10 empty runs on frozen input.
Still open: 10 runs is a small sample, so the true miss rate is not pinned down.

## 4. Writer forgot earlier contradictions
Symptom: a conflict found on pass 1 disappeared when a later check returned `[]`, so the writer stated the answer without noting the disagreement.
Cause: `contradictions` was overwritten on every check.
Fix: added `all_contradictions` to state. The router still uses the latest `contradictions`, the writer reads `all_contradictions`, and repeats are deduplicated.

## 5. Duplicate sources
Symptom: the same Wikipedia URL appeared twice in `sources`, so the writer could cite one page as two sources.
Cause: search returned the same URL twice and fetch only deduplicated against earlier passes.
Fix: fetch now deduplicates within a batch and skips URLs it already has.

## 6. Debugging against live search was unreliable
Symptom: the same query returned different pages on each run, so a prompt change could not be told apart from a change in input.
Fix: saved one real set of sources to `test/nile_sources.json`, and run `frozen_check.py` and `test_contradiction_set.py` against fixed inputs. Rule: freeze the input before tuning anything.

## Open items
- The retry cap of 2 has not yet been confirmed by a run where conflicts persist across passes.
- Many large sites (Britannica, journals) return HTTP errors to bots and are skipped. Retries may fetch fewer new sources than expected.
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

## 7. Faithfulness judge invented citations
Symptom: an answer with no citation, "Google was founded in 1998.", was marked `partial` instead of `uncited`.
Cause: the judge returned a `cited` list for each claim, and the model filled in `[1]` itself because source 1 contained the fact, even though the answer never cited it. My first fix (override the verdict when `cited` is empty) never fired for that reason.
Fix: the judge now copies each claim with its `[n]` markers, and our code reads the citation numbers from the claim text with a regex. A claim with no `[n]` is marked `uncited` by code, not by the model.

## 8. Faithfulness judge skipped and bundled claims
Symptom: a real answer produced only 3 claims. The first sentence was dropped, and one claim held three separate facts, so a single verdict covered all of them and could inflate the score.
Cause: the prompt said "split into claims" without defining how small a claim is.
Fix: the prompt now asks for atomic claims, one fact each, and says every sentence must be covered. Still open: the judge sometimes splits mid-sentence into fragments ("or in September 1998 [3].") and still bundles some pairs of facts.

## 9. Refine node wrote queries the fetcher could not use
Symptom: after a conflict, the new queries used `site:britannica.com` and `site:usgs.gov`, and almost every page returned an HTTP error or no extractable text, so retrying added no new sources.
Cause: the refine prompt asked for authoritative sources, and the model chose sites that block bots.
Status: not fixed yet. Next step is to tell the refine prompt not to use `site:` filters.

## 10. Gemini 503 crashed a run in the writer
Symptom: the whole graph crashed with `503 UNAVAILABLE: high demand` on the writer's API call.
Cause: a temporary overload on the model provider's side, not a bug in the code.
Status: not handled. In development a rerun is enough. Before deploying, add retries with backoff around model calls, since a crash after 30+ seconds of searching is a bad experience.

## Verified
- The retry cap works: with the router forced to always retry, the graph ran `refine` exactly twice and then went to the writer.
- The faithfulness judge separates good from bad: a real answer scored 1.0, and the same answer with every date changed to a wrong one scored 0.0.

## Open items
- The contradiction check is not fully reliable. On frozen input it flagged in 9 of 10 runs before the prompt rewrite and 10 of 10 after, which is a small sample.
- The faithfulness judge is untested on subtle errors (a wrong month, a close number) and on claims that cite several sources where only one supports it.
- Many large sites (Britannica, journals, SEC filings) block bots or have no extractable text, so they are skipped.
- No handling yet for model API errors (see 10).
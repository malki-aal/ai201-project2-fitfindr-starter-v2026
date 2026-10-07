# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user types a plain-language query like `"vintage graphic tee under $30"` — a
description, optionally a size and a price ceiling. FitFindr searches the
listings data for the best match, suggests one or two outfits that pair it
with pieces from the user's wardrobe (or general styling advice if they don't
have one saved), and writes a short social-media caption for the find. If
nothing in the data matches the query, it stops and says what to change
instead of making something up.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings data for items matching a free-text description, optionally narrowed by a size and a price ceiling.
- **Inputs:** `description` (str) — keywords describing what the user wants, e.g. `"vintage graphic tee"`. `size` (str or None) — a size token to filter by, case-insensitive whole-token match (`"M"` matches `"S/M"`; `"L"` does **not** match `"XL"`); `None` skips size filtering. `max_price` (float or None) — inclusive price ceiling; `None` skips price filtering.
- **Returns:** A list of listing dicts, best match first, sorted by keyword overlap with `description`. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), `platform` — capped at `config.SEARCH_RESULT_LIMIT` (10) items.
- **When it has nothing:** Returns `[]` — an empty list, never `None` and never an exception.

### `suggest_outfit`

- **What it does:** Given a listing the user is considering and their wardrobe, asks the model for one or two outfit ideas that pair the new item with pieces they already own.
- **Inputs:** `new_item` (dict) — a listing dict (the item being considered). `wardrobe` (dict) — a wardrobe dict with an `items` key holding a list of wardrobe item dicts; `items` may be `[]`.
- **Returns:** A non-empty string of prose outfit suggestions. When the wardrobe has items, it names those pieces specifically (by the descriptions passed into the prompt).
- **When it has nothing:** If `wardrobe["items"]` is empty, it asks the model for general styling advice for the new item instead — still a non-empty string, never a raise and never `""`.

### `create_fit_card`

- **What it does:** Writes a short caption (two to four sentences) someone would post about the find, combining the listing's details with the outfit suggestion.
- **Inputs:** `outfit` (str) — the suggestion string returned by `suggest_outfit`. `new_item` (dict) — the listing dict for the item.
- **Returns:** A two-to-four sentence string that mentions the item, its price, and its platform once each.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a fixed string — `"No outfit suggestion was available to build a caption for {title}."` — without calling the model or raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change (broader description, higher `max_price`, drop the size filter) and stop — do not call `suggest_outfit`. Otherwise, take the first result as `session["selected_item"]` and continue on to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::_parse_query`. One pattern matches `"under $X"` / `"below X"` / `"less than $X"` for `max_price`; another matches `"size Y"` for `size`. Both matched phrases are stripped out of the original query, and whatever text is left becomes `description`.

**What moves through the session:** `query` → `parsed` (`description`, `size`, `max_price`) → `search_results` → `selected_item` (first of `search_results`) → `outfit_suggestion` → `fit_card`. `wardrobe` is carried unchanged from `new_session` straight through to `suggest_outfit`. `error` is set only on the early-stop branch, and every field after it stays `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair the butterfly baby tee with your baggy straight-leg jeans, black combat boots, and the slightly cropped vintage black denim jacket for an effortless Y2K streetwear look. Alternatively, tuck it into your wide-leg khaki trousers with chunky white sneakers and the black crossbody bag for a casual, 90s-inspired contrast.

  Fit card: Obsessed with this Y2K butterfly baby tee, especially since it's in mint condition and only $18. I just listed it on depop so you can channel your inner 2000s pop star with zero effort. Snag it before I change my mind and keep it for myself!

2 model calls this session, 538 prompt + 130 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'price': 18.0, ...},
 {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'price': 24.0, ...},
 {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'price': 15.0, ...},
 {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'price': 19.0, ...},
 {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'price': 27.0, ...},
 {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'price': 26.0, ...}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Pair the vintage Levi's with your fitted white ribbed tank top and chunky white sneakers for an effortless, classic streetwear look. Throw on your slightly cropped vintage black denim jacket and accessorize with the black crossbody bag to complete the outfit.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Found these broken-in vintage Levi's 501s thrifting for just $38.00 and I'm never taking them off. That perfect medium wash has that exact 90s slouch you can't fake. Throw them on with crisp white sneakers and a beat-up tee for the ultimate effortless weekend uniform, now up on my depop.
```

**Checking `create_fit_card` isn't returning the same words every time** — ran it three times on the same item with the cache off (`AI201_CACHE=0`), since a cache hit and `TEMPERATURE=0` are the two things that would make three runs identical, and this project's `TEMPERATURE` is 0.9:

```
$ AI201_CACHE=0 python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

run 1: Nothing beats the wash on these vintage Levi's 501 jeans, especially when they're broken in just right. Pair them with crisp white sneakers for that effortlessly cool 90s off-duty model vibe. Snagged them for $38.0 on depop before anyone else could.

run 2: The absolute holy grail of denim just landed in my Depop shop. These vintage Levi's 501s feature that perfect broken-in medium wash you can't fake. Grab them for $38 and pair them with crisp white sneakers for an effortless off-duty model vibe.

run 3: The hunt is officially over because I just scored these broken-in vintage Levi's 501 jeans for only $38. They've got that perfect relaxed 90s slouch that you just can't fake. Throw them on with crisp white sneakers and an oversized tee for the ultimate effortlessly cool fit. Now live on my Depop—grab 'em before I change my mind and keep them.
```

Three different captions confirms the variation comes from `TEMPERATURE`, not a bug — and that the cache (on by default) is why identical back-to-back calls in the same process looked identical at first.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* My `git push` was rejected with a GitHub secret-scanning error, and I asked Claude why.
- *What came back:* It found that I'd pasted my real `GEMINI_API_KEY` into `.env.example` (which is tracked by git) instead of `.env` (which is gitignored). It also pointed out that just committing a fix on top wouldn't work, because GitHub's push protection scans every commit in the push, not just the final diff — the real key was still sitting in the one unpushed commit's history.
- *What I changed:* I put the placeholder back in `.env.example`, and instead of adding a new commit, amended the one unpushed commit so the key never existed in any commit that reached GitHub. I also rotated the key afterward since it had already been written to disk and shown in my terminal.

**Moment 2**

- *What I asked for:* For criteria.md, I asked Claude to just write my three remaining acceptance criteria and the "why this target" reasoning for me.
- *What came back:* It refused — pointed out the assignment explicitly says not to have a model write the criteria, since the reasoning only means something if I can defend it myself. It offered guided questions and fill-in-the-blank templates instead, and when I pushed back, it gave me multiple-choice reasoning options to pick from for each "why" line rather than writing the reasoning itself.
- *What I changed:* I picked the reasoning that actually matched my code (e.g. for the state criterion, that `selected_item` is a plain dict passed straight through the session with no model call involved, so there's no reason to accept less than 5 of 5), and wrote the final targets and numbers in my own words from there.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

`python run_eval.py --label before` — 10 scenarios × 5 tries, caching off. Full
output: `results/run_2026-10-07_1834_before.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools, returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | FAIL | MET (4/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item`'s id matches what `suggest_outfit` received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the item's price (same item, 5 tries) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Rephrased query still returns a result (5 *different* rephrasings — see note) | 4 of 5 | FAIL | FAIL | PASS | PASS | PASS | MISSED (3/5) |

> **Note on row 5:** unlike the other rows, each "Try" here is a *different*
> query, not a repeated run of the same one — `search_listings` has no model
> call and no randomness, so running one query 5 times would just give the
> same answer 5 times. Try 1–5 above correspond to scenarios "rephrase 1"
> through "rephrase 5" in `scenarios.py`, in order: `trench coat` (FAIL),
> `pleated slacks` (FAIL), `block heel booties` (PASS), `evening gown midi`
> (PASS), `chunky jumper vest` (PASS).

Try 5 of criterion 1 and tries 4–5 of the (diagnostic, non-criterion) empty-wardrobe
scenario failed for a reason outside my code: the Gemini API itself returned
`503 UNAVAILABLE` ("currently experiencing high demand") during this run — a
real, unplanned trigger of the same `ModelUnavailable` path I tested on purpose
in Milestone 2, not a bug in the agent.

**Real output, one per criterion, as text — file and function named:**

**Criterion 1** — `tools.py::search_listings` finds it, `agent.py::run_agent`
completes the run, `tools.py::create_fit_card` writes the card (Try 1):

```
Query: vintage graphic tee under $30

Outfit suggestion:
Pair the Y2K baby tee with your baggy straight-leg jeans and chunky white sneakers for an effortless streetwear look, throwing on the black cropped zip hoodie just in case. Alternatively, tuck the baby tee into your wide-leg khaki trousers, add the brown leather belt, and finish with the black combat boots for a cool, mixed-aesthetic outfit.

Fit card:
Found this pristine Y2K baby tee with the cutest butterfly print hiding on Depop for just $18. The condition is unreal, and it's giving major 2000s mall-rat energy in the best way possible. Snag it before I keep it for myself and live out my Lizzie McGuire dreams.
```

**Criterion 2** — `agent.py::run_agent`, the branch, stopping before
`suggest_outfit` (Try 1):

```
Query: designer ballgown size XXS under $5

[2] search_listings (via MCP)
      out: [] (empty)
      →    branch: empty — stopping before suggest_outfit

session["error"]: No listings matched. Try a broader description, a higher max_price, or dropping the size filter.
session["selected_item"]: None
session["fit_card"]: None
```

**Criterion 3** — `agent.py::run_agent`, state passing through the session
(Try 1 of the run_eval scenario, plus the independent instrumented check from
Milestone 5 that actually captures what `suggest_outfit` received):

```
Query: vintage graphic tee under $30

session["selected_item"]["id"] -> lst_002
id captured inside a patched tools.suggest_outfit (Milestone 5 spy test) -> lst_002
match: True
```

**Criterion 4** — `tools.py::create_fit_card`, same item, price mentioned
(Try 3, picked because it's the one that spells out the price two different
ways in one card):

```
Query: vintage levi 501 jeans medium wash
Item: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)

Fit card:
Found the holy grail of denim: these vintage Levi's 501 jeans in the absolute best medium wash. Snagged them for just $38.00 and they're ready for your rotation over on my Depop right now. Pair them with a cropped zip hoodie and chunky sneakers for that effortless 90s off-duty model vibe.
```

**Criterion 5** — `tools.py::search_listings`, the recall gap on rephrased
queries (one PASS, one FAIL, real output from each):

```
$ python -c "from agent import _parse_query; from tools import search_listings; print(search_listings(**_parse_query('trench coat')))"
[]   # FAIL — no literal word in 'trench coat' appears anywhere in the data

$ python -c "from agent import _parse_query; from tools import search_listings; print(search_listings(**_parse_query('evening gown midi')))"
[{'id': 'lst_013', 'title': '90s Silk Slip Dress — Floral, Midi Length', 'price': 30.0, ...}]   # PASS — 'midi' overlaps with the listing's own title
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | **MET (4/5)** | Counted PASS across the 5 tries in `results/run_2026-10-07_1834_before.md` — 4 ran to a finished fit card, 1 stopped early. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | **MET (5/5)** | All 5 tries stopped with the branch message before `suggest_outfit` ran — read the trace for each, not just the final message. |
| 3 | `selected_item`'s id matches what `suggest_outfit` received | 5 of 5 | **MET (5/5)** | All 5 tries carried the same item through the session; independently confirmed with an instrumented spy on `suggest_outfit` (Milestone 5) that captured the literal id it received and compared it to `session["selected_item"]["id"]`. |
| 4 | Fit card mentions the price | 4 of 5 | **MET (5/5)** | Read all 5 fit cards from the "same item, 5 tries" scenario — every one states the $38 price explicitly (as `$38`, `$38.0`, or `$38.00`). |
| 5 | Rephrased query still returns a result | 4 of 5 | **MISSED (3/5)** | Of the 5 differently-worded queries, `trench coat` and `pleated slacks` returned `[]`; the other 3 returned at least one listing. 3 PASS out of 5 is below the 4-of-5 target — a miss, not a near-miss I can round up. |

**Diagnoses**

**Criterion 5 is the one miss, and it's in the tool, not the loop or the session.** `_score()` in `tools.py` ranks a listing by exact, unstemmed word-token overlap between the query and the listing's title, description, category, brand, colors, and style tags — there is no synonym table and no stemming. I checked: neither "trench," "coat," "pleated," nor "slacks" appears as a literal token anywhere in `data/listings.json`'s 40 records (built the full vocabulary set across all six fields and checked membership directly). The listing a person would call "khaki slacks" is titled "Straight Leg Khaki Trousers" in the data — a word a real shopper would use scores zero because it's the wrong word, not because nothing relevant exists. The tool is doing exactly what it was built to do; the design (plain keyword overlap) just doesn't generalize past the data's own vocabulary. This is the only miss, so there's no cross-tool pattern to report — but it's notable that the four criteria that held (branching, state, an explicitly-instructed model behavior) all test mechanical or heavily-constrained paths, while the one that missed tests the system's least-constrained capability: open-vocabulary matching with no model or synonym handling in the loop.

**One thing worth flagging even though it isn't a miss:** criterion 1's "why this target" reasoning (written in `criteria.md` before any results existed) predicted the 1-in-5 miss would come from the search being "a plain keyword match" that some phrasings would miss. That's not what actually happened — criterion 1's one failed try had `search_listings` succeed with 10 results; the run stopped later, inside `suggest_outfit`, when the Gemini API returned a genuine `503 UNAVAILABLE` ("currently experiencing high demand"). The target (4 of 5) still held, but the mechanism I'd predicted wasn't the mechanism that actually fired — a reminder that "why I expect to miss sometimes" and "why I actually missed" can be two different tools entirely, and it's worth re-checking both every time rather than assuming the original guess was right.

**Talk this through, on my own — arguing the opposite verdict for criterion 5:**
The strongest case I can make for MET instead of MISSED: the criterion's wording only asks whether `search_listings` "returns at least one result" — it never requires the result to be the *correct* item. By that narrow reading, 3 of 5 rephrasings did return something, and for an unaided keyword matcher (no embeddings, no synonym table) built in a few hours, a 60% hit rate on genuinely different vocabulary isn't an unreasonable showing — maybe the real problem is that 4-of-5 was an optimistic target for this architecture, not that the system is broken.

That argument doesn't survive, though — and this milestone says explicitly why: "the target was too ambitious" is the one reason that is *not* allowed to turn a miss into a revision. The criterion was fully measurable (a clean, repeatable 3-of-5 count, no ambiguity about what counts as a result), so it doesn't qualify as "broken" under the unit's own rule — it qualifies as missed. The honest move is to leave the target at 4 of 5, log this as a real miss, and attempt an actual fix in Milestone 5 (the criteria.md target itself stays untouched, with the original line intact).


---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace

[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: matched — continuing to suggest_outfit
[3] suggest_outfit
      in:  dict with keys: item
      out: Pair the butterfly baby tee with your baggy straight-leg jeans, black combat boots, and the slightly cropped v…
[4] create_fit_card
      in:  dict with keys: outfit
      out: Obsessed with this Y2K butterfly baby tee, especially since it's in mint condition and only $18. I just listed…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair the butterfly baby tee with your baggy straight-leg jeans, black combat boots, and the slightly cropped vintage black denim jacket for an effortless Y2K streetwear look. Alternatively, tuck it into your wide-leg khaki trousers with chunky white sneakers and the black crossbody bag for a casual, 90s-inspired contrast.

  Fit card: Obsessed with this Y2K butterfly baby tee, especially since it's in mint condition and only $18. I just listed it on depop so you can channel your inner 2000s pop star with zero effort. Snag it before I change my mind and keep it for myself!

0 model calls this session, 2 served from cache
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace

[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty — stopping before suggest_outfit

  No listings matched. Try a broader description, a higher max_price, or dropping the size filter.

0 model calls this session
```

The empty-search trace is two steps; the happy path is four. The branch is doing its job — it stops the loop before `suggest_outfit` or `create_fit_card` ever run, rather than calling them with nothing to work with.

**On the MCP move:** Moved `search_listings` to `mcp_server.py`, registered with `@mcp.tool()`. In `agent.py::run_agent`, the direct call `search_listings(description, size, max_price)` became `call_tool("search_listings", {...})` from `mcp_client`. The rewire worked on the first attempt — the only snag was environmental, not architectural: `mcp` wasn't on `PATH` for the global `python`, because the project uses a `.venv` with its own installed packages, so I had to run everything through `.venv/Scripts/python.exe` instead. Once that was sorted, the output was byte-for-byte the same as the direct call — same item found, same price as a real `float`, same list shape — confirming the MCP wrapper changed nothing about what the tool actually returns.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** Added a small, one-directional synonym table (`_SYNONYMS` in
`tools.py`) and expanded the query's keyword set with it before scoring in
`_score()` — e.g. a query containing "slacks" now also counts as containing
"trousers"/"pants", "coat" also counts as "jacket", "gown" also counts as
"dress". One function changed (`_score`), one new constant. Nothing about
`search_listings`'s inputs, outputs, or the empty-list guarantee changed.

**Which failure it was meant to fix:** Criterion 5's diagnosis (previous
section) — `_score()` does exact, unstemmed word overlap with no synonym
handling, so a real rephrasing like "pleated slacks" scored 0 against a
listing titled "Straight Leg Khaki Trousers" even though it's clearly the
same kind of item. The synonym table is a direct, scoped answer to that exact
mechanism, not a rewrite of the scoring approach.

### Run Log — After

`python run_eval.py --label after` — same 10 scenarios, 5 tries each, caching
off. Full output: `results/run_2026-10-07_1847_after.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item`'s id matches what `suggest_outfit` received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Rephrased query still returns a result | 4 of 5 | PASS | PASS | PASS | PASS | PASS | **MET (5/5)** |

> Row 5's "Try" columns are the same five rephrased-query scenarios as the
> before table, in the same order (`trench coat`, `pleated slacks`, `block
> heel booties`, `evening gown midi`, `chunky jumper vest`) — not five repeats
> of one query, for the same reason as before: no model, no randomness.

**Did it help, and how do I know:** Yes, for the criterion it targeted —
criterion 5 went from 3/5 to 5/5, and I can point at exactly why: `pleated
slacks` now matches "Straight Leg Khaki Trousers — Olive" via the
`slacks → trousers` synonym, and `trench coat` now matches jacket listings via
`coat → jacket`. That second one is a real trade-off worth naming honestly:
it fixes *recall* (the criterion only asks whether something comes back) but
it isn't a precise match — a trench coat and a track jacket aren't the same
garment, and the synonym table can't tell the difference. The fix is
correctly scoped (it widens recall exactly where the diagnosis said to, and
nowhere else) but it trades a little precision for that recall, which the
current criterion doesn't measure and so didn't catch.

Criterion 1 also went from 4/5 to 5/5 in this run, but **not because of this
fix** — this run simply didn't hit the Gemini `503` outage that caused
criterion 1's one miss in the before run. `search_listings` isn't involved in
that criterion's failure mode at all, so crediting the synonym change for it
would be the wrong diagnosis. Criteria 2, 3, and 4 are unchanged, as expected
— the fix never touches the branch, the session, or either prompt.

---

## What's Still Broken

No criterion is currently below its target, but the fix itself is incomplete
in a way worth naming rather than hiding:

- **The synonym table is hand-picked and tiny** (9 entries), built by looking
  at the two queries that actually failed rather than any general vocabulary
  coverage. It'll keep missing any rephrasing whose alternate word isn't one
  of the ones I happened to add — this patches the two cases the test
  surfaced, it doesn't fix the underlying architecture (exact keyword
  matching will always have a vocabulary ceiling; an embeddings-based or
  fuzzy-match approach would generalize further, but that's a bigger change
  than one unit's "pick one thing" scope allows).
- **Recall went up, precision wasn't measured.** The `coat → jacket` synonym
  means "trench coat" now matches jacket listings that aren't really trench
  coats. Criterion 5 only checks "did something come back," so this passes
  cleanly — but a criterion that also checked relevance (e.g., "the top
  result shares at least one tag with the query's intent") would likely still
  catch this as a problem. I didn't write that criterion this unit, so it's
  not caught, and I'm flagging it here instead of pretending the fix is
  clean.
- I stopped at one change, as the milestone asked — I didn't also revisit
  criterion 1's actual failure mode (the `503` outage), since that's a
  transient upstream issue, not something `agent.py`'s existing
  `ModelUnavailable` handling got wrong; it already degraded correctly when
  it happened.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # Criterion 3 — state. Any matching query works; what's being
        # checked is that session["selected_item"]'s id is the same id the
        # item passed into suggest_outfit has, not what the user typed.
        "name": "state: selected item matches what suggest_outfit receives",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 — fit card mentions the price. This query has one
        # clear, stable top-1 match (lst_001, the Levi's 501s) — verified
        # empirically that it wins every time — so running it 5 times is
        # really "the same item through create_fit_card 5 times," which is
        # exactly what the criterion asks for.
        "name": "fit card mentions price (same item, 5 tries)",
        "query": "vintage levi 501 jeans medium wash",
        "wardrobe": "example",
        "criterion": 4,
    },
    # Criterion 5 — recall on rephrased queries. _score() in tools.py is
    # exact keyword overlap with no synonyms, so this criterion needs 5
    # DIFFERENT queries that deliberately avoid the target listing's own
    # vocabulary, not the same query 5 times (search_listings has no model
    # call and no randomness — one query would just give the same answer
    # 5 times over). Each is its own scenario here; the five Try columns in
    # the README's criterion-5 row come from one try of each of these five,
    # not from repeated tries of any single one.
    {
        "name": "rephrase 1: 'trench coat' for the denim jacket (lst_007)",
        "query": "trench coat",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "rephrase 2: 'pleated slacks' for khaki trousers (lst_021)",
        "query": "pleated slacks",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "rephrase 3: 'block heel booties' for suede boots (lst_028)",
        "query": "block heel booties",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "rephrase 4: 'evening gown midi' for the slip dress (lst_013)",
        "query": "evening gown midi",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "rephrase 5: 'chunky jumper vest' for the knit vest (lst_030)",
        "query": "chunky jumper vest",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems

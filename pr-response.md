# PR Response Doc — CineLog Watchlist Feature

## Comment 1 — Rename
> `save_to_watchlist()` should follow the project's naming convention. Compare with `add_to_collection()` — the pattern here is `verb_to_noun`. Please rename to `add_to_watchlist()` and update all call sites.

**What I did:** Change the function name `save_to_watchlist()` to `add_to_watchlist()` in `services/watchlist_service.py`. Update its docstring accordingly to reflect the new name and keep it consistent with the existing pattern. Finally, update all call sites, particularly `add_film()` in `routes/watchlist.py`, to ensure the system remains error-free.

**Reasoning:** These updates reflect the pre-defined naming conventions in [CONTRIBUTING.md](CONTRIBUTING.md) and promote consistency, maintainability, and readability across the project.

**How I verified:** Seed some sample data to the database via `sqlite3`, run the application and try to save a film to an existing watchlist via `curl` API request. The site ran smoothly as expected and without errors.

## Comment 2 — Deduplication
> What happens if a user calls this with a film that's already on their watchlist? The current implementation would add a duplicate entry. Please handle this case.

**What I did:**
**Reasoning:**
**How I verified:**

## Comment 3 — Missing test
> Please add a test for the case where `film_id` doesn't exist in the database. Look at the existing tests in `test_collection.py` — the pattern is there.

**What I did:**
**Reasoning:**
**How I verified:**

## Comment 4 — Default visibility
> I notice watchlists default to `public=True`. We don't have a documented decision on default visibility for user lists. Before I can approve this, I need you to add a note to your PR description explaining your reasoning. I want to make sure we're being intentional here, not just inheriting a default.

**My decision:**

**Reasoning:**

**Tradeoff acknowledged:**

## Comment 5 — Sort order
> I'd prefer watchlists to default to "date added" order rather than alphabetical. Most users want to see what they added recently. I'm open to discussion if you see it differently — but let's make a decision and document it.

**My position:**

**Reasoning:**

**Engagement with reviewer's point:**

## Comment 6 — Rebase
> A refactor merged to `main` that changed film IDs from integers to UUIDs. Your watchlist code still references integer IDs. Please rebase on `main` and update accordingly.

**What conflicted:**
**How I resolved it:**
**Reasoning:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->
### Feature Overview

### Design Decisions

### Manual Testing Steps

## AI Usage
**Instance 1:**
* *What I gave the AI:* 
* *What it produced:* 
* *What I changed or overrode:*


**Instance 2:**
* *What I gave the AI:* 
* *What it produced:*
* *What I changed or overrode:*
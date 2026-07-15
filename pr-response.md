# PR Response Doc — CineLog Watchlist Feature

## Comment 1 — Rename
> `save_to_watchlist()` should follow the project's naming convention. Compare with `add_to_collection()` — the pattern here is `verb_to_noun`. Please rename to `add_to_watchlist()` and update all call sites.

**What I did:** Change the function name `save_to_watchlist()` to `add_to_watchlist()` in `services/watchlist_service.py`. Update its docstring accordingly to reflect the new name and keep it consistent with the existing pattern. Finally, update all call sites, particularly `add_film()` in `routes/watchlist.py`, to ensure the system remains error-free.

**Reasoning:** These updates reflect the pre-defined naming conventions in [CONTRIBUTING.md](CONTRIBUTING.md) and promote consistency, maintainability, and readability across the project.

**How I verified:** Seed some sample data to the database via `sqlite3`, run the application and try to save a film to an existing watchlist via `curl` API request. The site ran smoothly as expected and without errors.


## Comment 2 — Deduplication
> What happens if a user calls `add_to_watchlist()` with a film that's already on their watchlist? The current implementation would add a duplicate entry. Please handle this case.

**What I did:** As I compared code implementation of the only two services, watchlist and collection, I noticed that the collection service implemented a duplication check that raises an exception message and prevents user from adding the same film, while the other did not. To address this, I add similar deduplication implementation in watchlist service, particularly in `add_to_watchlist()` function. This implementation also includes custom Exception class `AlreadyInWatchlistError` that will be raised when duplication happens.

**Reasoning:** Since watchlist and collection services have similar functionality, they should follow the same deduplication behavior. From both a logical and user experience perspective, the same film should not be allowed to be added to a watchlist more than once.

**How I verified:** Using the database I have established earlier, I repeatedly attempted to add a random film into an existing playlist and the system responded with exception error after the first result. This behavior is expected and correct, confirming that the deduplication logic was functioning well. I also tried with other film item and the same result appeared.


## Comment 3 — Missing test
> Please add a test for the case where `film_id` doesn't exist in the database. Look at the existing tests in `test_collection.py` — the pattern is there.

**What I did:** After reviewing the test suite of the collection service, I implemented a corresponding pytest framework for the watchlist service. This new suite includes tests for record count, non-existent film, correct film names, empty watchlist, deduplication, and several additional scenarios. It follows the same mechanism as the collection service's while containing additional test cases.

**Reasoning:** Since watchlist and collection services have similar functionality, they should have similar,comparable test suite. This update also aligns with the existing project conventions defined in [CONTRIBUTING.md](CONTRIBUTING.md), which requires automated tests for every new feature.

**How I verified:** I compare side by side with the test suite in `tests/test_collection.py` to ensure mine follows the same patterns and conventions. After that, I ran all the test cases. Even though the non-existent film test case along with 3 other test case passed, 5 test cases failed. Tracing the root case, I discovered that there was no relationship between `WatchlistEntry` and `Film`, which caused an error in `get_watchlist()` in watchlist service. Therefore, I will establish this relationship in the following commit, similar to the one between `Film` and `CollectionEntry`. 


## Comment 4 — Default visibility
> I notice watchlists default to `public=True`. We don't have a documented decision on default visibility for user lists. Before I can approve this, I need you to add a note to your PR description explaining your reasoning. I want to make sure we're being intentional here, not just inheriting a default.

**My position:** Watchlist visibility should be set to public by default, but users can change to private at any time.

**Reasoning:** Watchlists are different from collection entries (watched films). A watchlist is a curated list of films you *recommend* or *want to discover*. They are shareable, social artifacts by default. Plus, we want to encourage users to discover what others are interested in, which adds social value to the platform. This approach is very much similar to what Spotify is doing. Users who want privacy can opt-out, but the default should enable discovery and recommendation-sharing as core features.

**Tradeoff acknowledged:** The alternative approach, `public=False`, would prioritize privacy and require users to explicitly opt-in to sharing. This is a valid safety-first approach, especially in early product stages. However, it risks making watchlists a hidden feature that doesn't generate network effects. The tradeoff is between *discovery and engagement* (public-first) versus *privacy-by-default*. As stated in [README.md](README.md), CineLog is a *community* film tracking platform. Therefore, discovery and social connection align with our goals and values.


## Comment 5 — Sort order
> I'd prefer watchlists to default to "date added" order rather than alphabetical. Most users want to see what they added recently. I'm open to discussion if you see it differently — but let's make a decision and document it.

**My position:** Watchlists should be ordered *chronologically* rather than alphabetically.

**Reasoning:** Your point about user behavior is correct and reasonable. When a user looks at their watchlist, their immediate instinct is *"what did I just add?"* or *"what's new on my list?"* Chronological order (newest first) directly satisfies that need, making the watchlist more convenient and user-friendly. Additionally, this change promotes consistency across the project. The collection service already sorts by `date_added` in descending order. Thus, it makes sense when the watchlist does the same. Matching the sort pattern reduces cognitive load for users switching between features. Alphabetical sorting was a convenience decision on my part, but it doesn't serve the actual user workflow as well as chronological ordering does.

**Engagement with reviewer's point:** I initially chose alphabetical sorting thinking it would make large watchlists easier to *search through*. But this is irrational. For actual searching, users can have the search feature in the UI. For browsing, they want to see what's current and relevant. From your feedback, I realized that the watchlist is a working list, not an archive. So chronological order is the right default. 

**What I did:**  I updated `get_watchlist()` in `services/watchlist_service.py` to sort by `WatchlistEntry.date_added DESC`.

## Comment 6 — Rebase
> A refactor merged to `main` that changed film IDs from integers to UUIDs. Your watchlist code still references integer IDs. Please rebase on `main` and update accordingly.

**What conflicted:**
**How I resolved it:**
**Reasoning:**
**How I verified no conflict remains:**


## PR Description
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
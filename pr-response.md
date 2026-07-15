# PR Response Doc — CineLog Watchlist Feature
## AI Usage
* *AI Tool:* Claude Code.

* *What I gave the AI:* The source code of `services/watchlist.py` and `tests/test_collection.py` (as a code pattern to follow), a request to create a comprehensive pytest framework for testing all functions in `services/watchlist.py`, following the same pytest pattern and conventions used in `tests/test_collection.py`.

* *What it produced:* A complete test suite in `tests/test_watchlist.py` with 14 test cases, organized into six logical groups.

* *What I changed or overrode:* I refactored several test function names to improve clarity and consistency. More importantly, followin watchlist ordering decision and main branch rebase, I updated the test cases for sorted films and non-existent film to reflect new behavior change. Specifically, `test_sorted_films_by_date_added` now expects films ordered by most-recently-added first, and `test_add_to_watchlist_nonexistent_film_raises` now uses a UUID string instead of an integer for the fake film ID.


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

**My position:** Set watchlist visibility to public by default. Users can change to private at any time.

**Reasoning:** Watchlists are different from collection entries (watched films). A watchlist is a curated list of films you *recommend* or *want to discover*. They are shareable, social artifacts by default. Plus, we want to encourage users to discover what others are interested in, which adds social value to the platform. This approach is very much similar to what Spotify is doing. Users who want privacy can opt-out, but the default should enable discovery and recommendation-sharing as core features.

**Tradeoff acknowledged:** The alternative approach, `public=False`, would prioritize privacy and require users to explicitly opt-in to sharing. This is a valid safety-first approach, especially in early product stages. However, it risks making watchlists a hidden feature that doesn't generate network effects. The tradeoff is between *discovery and engagement* (public-first) versus *privacy-by-default*. As stated in [README.md](README.md), CineLog is a *community* film tracking platform. Therefore, discovery and social connection align with our goals and values.


## Comment 5 — Sort order
> I'd prefer watchlists to default to "date added" order rather than alphabetical. Most users want to see what they added recently. I'm open to discussion if you see it differently — but let's make a decision and document it.

**My position:** Agree with the maintainer and sort watchlists *chronologically* rather than alphabetically.

**Reasoning:** When a user looks at their watchlist, their immediate instinct is *"what did I just add?"* or *"what's new on my list?"* Chronological order (newest first) directly satisfies that need, making the watchlist more convenient and user-friendly. Additionally, this change promotes consistency across the project. The collection service already sorts by `date_added` in descending order. Thus, it makes sense when the watchlist does the same. Matching the sort pattern reduces cognitive load for users switching between features. Alphabetical sorting was a convenience decision on my part, but it doesn't serve the actual user workflow as well as chronological ordering does.

**Engagement with reviewer's point:** I agree with your point. I initially chose alphabetical sorting thinking it would make large watchlists easier to search through. But this is irrational. For actual searching, users can have the search feature in the UI. For browsing, they want to see what's current and relevant. From your feedback, I realized that the watchlist is a working list, not an archive. So chronological order is the right default. 

**What I did:**  I updated query in `get_watchlist()` function from `services/watchlist_service.py` to sort by query result by `WatchlistEntry.date_added DESC`. I also revised its docstring to reflect the update and refactored test for sorted films as the films were no longer sorted alphabetically.

## Comment 6 — Rebase
> A refactor merged to `main` that changed film IDs from integers to UUIDs. Your watchlist code still references integer IDs. Please rebase on `main` and update accordingly.

**What conflicted:** The `WatchlistEntry` in `models.py` was removed entirely, which corrupted the watchlist service. That class only existed on `feature/watchlist` branch.

**How I resolved it:** I kept `WatchlistEntry` class as-is for the conflict resolution. Then, I changed data type of `film_id` of that class to `db.String(36)`, updated docstring of `add_to_watchlist()` function in `services/watchlist_service.py`, and updated my test's fake ID from an integer to a fake UUID string.

**Reasoning:** It is obvious that keeping `WatchlistEntry` is keeping watchlist feature alive. Additionally, minor changes in `film_id` data type, docstring, and test suite are important to reflect the film's UUID update from the main branch refactor.

**How I verified no conflict remains:** I ran `git log --merges --oneline origin/main..HEAD` and saw nothing. This confirmed that my branch's history is fully linear with no merge commits. Finally, I ran all the test suites and everything passed.


## Stretch Features

### Film Removal in Watchlist
**Overview:**
Implemented the ability for users to remove films from their watchlist. This completes the full CRUD lifecycle for watchlist management and synchronizes the watchlist service with the collection service. It also allows users to manage their watch-later lists by adding and removing films as their interests change.

**Implementation:**
- Added `remove_from_watchlist()` function to `services/watchlist_service.py` that follow similar code patterns and conventions in `services/collection_service.py`.
- Added **5 comprehensive test cases** covering this removal functionality.
- Added error handling with a new `NotInWatchlistError` exception and employed it in `remove_from_watchlist()`. When a user removes a film that was never added to their watchlist or when the watchlist entry does not exist in the database, this exception will be raised.

**User Experience Benefits:**
- Users can change their minds and remove films from their watchlist without friction
- Allows watchlists to stay current and relevant by removing films that have been watched or are no longer of interest
- Provides immediate feedback through exceptions instead of silent failures
- Maintains data integrity by preventing orphaned or duplicate entries when films are removed and re-added


### Extended Watchlist Test
**Total Test Count:** 14 test cases in `tests/test_watchlist.py`

**Overview:**
The watchlist test suite follows the same pytest patterns and conventions used in `tests/test_collection.py`, providing comprehensive coverage of the watchlist service functionality. Tests are organized into six logical groups:

**1. Basic Add Functionality (2 tests)**
- `test_add_to_watchlist`: Verifies that adding a valid film to a user's watchlist creates a `WatchlistEntry` in the database and persists correctly.
- `test_get_watchlist`: Confirms that after adding a film to the watchlist, it can be retrieved via `get_watchlist()` with correct film metadata (title, year, genre, etc.).

**2. Deduplication (1 test)**
- `test_add_to_watchlist_duplicate_raises`: Ensures that attempting to add the same film twice to a user's watchlist raises `AlreadyInWatchlistError` and prevents duplicate entries in the database.

**3. Error Handling (1 test)**
- `test_add_to_watchlist_nonexistent_film_raises`: Validates that adding a `film_id` that doesn't exist in the database raises `FilmNotFoundError` before any database operation occurs.

**4. Sort Order Verification (1 test)**
- `test_sorted_films_by_date_added`: Verifies that `get_watchlist()` returns films sorted by `date_added` in descending order (most recently added first), ensuring users see their latest additions at the top.

**5. Watchlist Count and Contents (4 tests)**
- `test_watchlist_returns_correct_number_of_films`: Confirms that `get_watchlist()` returns the exact count of films a user has added.
- `test_watchlist_returns_correct_film_names`: Validates that all films added to the watchlist are present in the retrieved list with correct titles.
- `test_empty_watchlist`: Tests the edge case where a user with no watchlist entries receives an empty list (not an error).
- `test_watchlist_only_returns_user_films`: Ensures data isolation—that `get_watchlist()` only returns films for the specified user, not films from other users' watchlists.

**6. Removal Functionality (5 tests)**
- `test_remove_from_watchlist_deletes_entry`: Verifies that removing a valid film deletes the `WatchlistEntry` from the database and returns `True`.
- `test_remove_from_watchlist_film_not_found`: Ensures `NotInWatchlistError` is raised when attempting to remove a non-existent entry.
- `test_remove_decreases_watchlist_count`: Confirms watchlist count decreases after removal with correct remaining films.
- `test_remove_only_affects_user_watchlist`: Validates that removal only affects the specified user's watchlist, not other users.
- `test_remove_from_empty_watchlist_raises`: Tests edge case of removing from an empty watchlist.


## PR Description

### Feature Overview
This PR introduces a complete **Watchlist** feature for CineLog. A watchlist is a curated list of films users want to *recommend* or *discover*. They are shareable artifacts which adds social value to the platform.

The feature includes:
- **Add to Watchlist:** Users can add films to their personal watchlist with deduplication to prevent duplicate entries
- **View Watchlist:** Retrieve all films on a user's watchlist, sorted chronologically (newest additions first) with full film metadata
- **Remove from Watchlist:** Remove films from the watchlist when they've been watched or are no longer of interest
- **Visibility Control:** Watchlists default to public, allowing users to share their watch-later recommendations with the community, with the option to set entries as private
- **Data Isolation:** Each user only sees and manages their own watchlist entries

The watchlist service follows the functionality and patterns of the existing collection service, ensuring consistency and maintainability across the platform while serving a different user need.


### Design Decisions
- **Sort Order: Chronological (Newest First)**  
Watchlists are sorted by `date_added DESC` rather than alphabetically. This respects actual user behavior. When checking a watchlist, users want to see what they *just* added, not browse alphabetically. This also maintains consistency with the collection service's sort order.

- **Default Visibility: Public**  
Watchlists default to `public=True` because they are shareable, social artifacts. They reflect user recommendations and interests. This decision promotes community value and CineLog's identity as a community film platform.


### Manual Testing Steps
**Prerequisites:**
1. Set up the environment: run `python -m venv .venv` to create a python virtual environment and activate it.
2. Download dependencies: `pip install -r requirements.txt`.
3. Run the application: `flask --app app run`
4. Seed a user and a film to the database using `sqlite3`.

**Test 1: Add a Film to Watchlist**
1. Call POST `/watchlist/add` with `user_id` and `film_id`
2. Verify the response includes the new `WatchlistEntry` with `date_added` and `public` fields
3. Confirm the film appears in GET `/watchlist/{user_id}`

**Test 2: Verify Deduplication**
1. Add the same film to the watchlist twice
2. Verify the second attempt returns a 400 error with message about `AlreadyInWatchlistError`
3. Confirm only one entry exists in the database

**Test 3: View Watchlist (Sorted Chronologically)**
1. Add 3 films to your watchlist at different times
2. Call GET `/watchlist/{user_id}`
3. Verify films are returned in reverse chronological order (most recent first)
4. Verify each film includes title, year, genre, director, and watchlist metadata (date_added, public)

**Test 4: Remove a Film from Watchlist**
1. Add a film to your watchlist
2. Call DELETE `/watchlist/remove` with `user_id` and `film_id`
3. Verify the response indicates successful removal
4. Call GET `/watchlist/{user_id}` and confirm the film no longer appears

**Test 5: Error Cases**
- Try to add a non-existent film → verify `FilmNotFoundError`
- Try to remove a film that's not in your watchlist → verify `NotInWatchlistError`
- View watchlist with non-existent user ID → verify empty list is returned

**Test 6: Data Isolation**
1. Create two user accounts
2. Have user A add Film X and Film Y to their watchlist
3. Have user B add Film Y and Film Z to their watchlist
4. Verify user A's watchlist contains only Film X and Film Y
5. Verify user B's watchlist contains only Film Y and Film Z

**Test Suite Execution:** `pytest tests/test_watchlist.py -v` → all 14 tests should pass.
"""
tests/test_watchlist.py — CineLog

Tests for the watchlist service.
Follows the same patterns as test_collection.py.
"""

import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.watchlist_service import (
    add_to_watchlist,
    get_watchlist,
    FilmNotFoundError,
    AlreadyInWatchlistError,
)


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id


# ── Basic add ───────────────────────────────────────────────────────────────

def test_add_to_watchlist(app, sample_user, sample_film):
    """
    Adding a valid film should create a WatchlistEntry in the database.
    """
    with app.app_context():
        entry = add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert entry is not None
        assert entry.user_id == sample_user
        assert entry.film_id == sample_film

        # Verify it persisted
        in_db = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert in_db is not None


def test_get_watchlist(app, sample_user, sample_film):
    """
    After adding a film to the watchlist, it should be retrievable via get_watchlist.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)
        watchlist = get_watchlist(sample_user)

        assert len(watchlist) == 1
        assert watchlist[0]["title"] == "Paddington 2"


# ── Deduplication ────────────────────────────────────────────────────────────

def test_add_to_watchlist_duplicate_raises(app, sample_user, sample_film):
    """
    Adding the same film twice should raise AlreadyInWatchlistError,
    not silently create a duplicate entry.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        # Confirm only one entry exists
        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1


# ── Nonexistent film ─────────────────────────────────────────────────────────

def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film_id that doesn't exist in the database should raise
    FilmNotFoundError.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


# ── Sort order ──────────────────────────────────────────────────────────────

def test_sorted_films_by_date_dadded(app, sample_user):
    """
    get_watchlist() should return films sorted by date added in descending order.
    """
    with app.app_context():
        film_a = Film(title="Zebra", year=2020, genre="Drama")
        film_b = Film(title="Alien", year=1979, genre="Sci-Fi")
        film_c = Film(title="Monkey Business", year=2015, genre="Comedy")
        db.session.add_all([film_a, film_b, film_c])
        db.session.commit()

        add_to_watchlist(user_id=sample_user, film_id=film_a.id)
        add_to_watchlist(user_id=sample_user, film_id=film_b.id)
        add_to_watchlist(user_id=sample_user, film_id=film_c.id)

        watchlist = get_watchlist(sample_user)
        titles = [f["title"] for f in watchlist]

        # Should be sorted chronologically
        assert titles == ["Monkey Business", "Alien", "Zebra"]


# ── Watchlist count and contents ────────────────────────────────────────────

def test_watchlist_returns_correct_number_of_films(app, sample_user):
    """
    get_watchlist() should return the correct number of films added.
    """
    with app.app_context():
        film_1 = Film(title="Film 1", year=2020, genre="Action")
        film_2 = Film(title="Film 2", year=2021, genre="Drama")
        film_3 = Film(title="Film 3", year=2022, genre="Comedy")
        db.session.add_all([film_1, film_2, film_3])
        db.session.commit()

        add_to_watchlist(user_id=sample_user, film_id=film_1.id)
        add_to_watchlist(user_id=sample_user, film_id=film_2.id)
        add_to_watchlist(user_id=sample_user, film_id=film_3.id)

        watchlist = get_watchlist(sample_user)
        assert len(watchlist) == 3


def test_watchlist_returns_correct_film_names(app, sample_user):
    """
    get_watchlist() should return the correct list of film names
    that were added.
    """
    with app.app_context():
        film_1 = Film(title="The Matrix", year=1999, genre="Sci-Fi")
        film_2 = Film(title="Inception", year=2010, genre="Sci-Fi")
        film_3 = Film(title="Interstellar", year=2014, genre="Sci-Fi")
        db.session.add_all([film_1, film_2, film_3])
        db.session.commit()

        add_to_watchlist(user_id=sample_user, film_id=film_1.id)
        add_to_watchlist(user_id=sample_user, film_id=film_2.id)
        add_to_watchlist(user_id=sample_user, film_id=film_3.id)

        watchlist = get_watchlist(sample_user)
        titles = [f["title"] for f in watchlist]

        assert "The Matrix" in titles
        assert "Inception" in titles
        assert "Interstellar" in titles
        assert len(titles) == 3


def test_empty_watchlist(app, sample_user):
    """
    get_watchlist() should return an empty list for a user with no watchlist entries.
    """
    with app.app_context():
        watchlist = get_watchlist(sample_user)
        assert watchlist == []


def test_watchlist_only_returns_user_films(app, sample_user):
    """
    get_watchlist() should only return films for the specific user,
    not films added by other users.
    """
    with app.app_context():
        # Create second user
        user_2 = User(username="otheruser", email="other@example.com")
        db.session.add(user_2)
        db.session.commit()

        film_1 = Film(title="Movie A", year=2020, genre="Action")
        film_2 = Film(title="Movie B", year=2021, genre="Drama")
        db.session.add_all([film_1, film_2])
        db.session.commit()

        add_to_watchlist(user_id=sample_user, film_id=film_1.id)
        add_to_watchlist(user_id=user_2.id, film_id=film_2.id)

        watchlist_user1 = get_watchlist(sample_user)
        watchlist_user2 = get_watchlist(user_2.id)

        assert len(watchlist_user1) == 1
        assert watchlist_user1[0]["title"] == "Movie A"

        assert len(watchlist_user2) == 1
        assert watchlist_user2[0]["title"] == "Movie B"

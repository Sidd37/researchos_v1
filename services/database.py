"""
database.py

Responsible for all USER DATA persisted in SQLite:
- research notes (create, read, update, delete)
- watchlist (add, remove, list)

Implemented so far:
- Phase 6: notes (init_db, add_note, get_notes, get_note, update_note, delete_note)
- Phase 7: watchlist (add_to_watchlist, get_watchlist, remove_from_watchlist, is_watchlisted)

Rule for this module: it is the ONLY place in the app that should
open a SQLite connection or run SQL. Pages call the functions below
instead of running queries directly.

The database file lives at data/researchos.db, located relative to
this file's own location (not the current working directory), so it
works correctly no matter where `streamlit run` is launched from.
The data/ directory and all tables are created automatically the
first time they're needed.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# data/researchos.db, relative to the project root (one level up from services/)
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "researchos.db"


def _get_connection():
    """
    Open a SQLite connection to the ResearchOS database.

    Creates the data/ directory if it doesn't exist yet. Rows are
    returned as sqlite3.Row objects so columns can be accessed by
    name (e.g. row["title"]) instead of by position.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """
    Create the notes and watchlist tables if they don't already exist.

    Safe to call every time a page loads - CREATE TABLE IF NOT EXISTS
    is a no-op if a table is already there.

    Returns
    -------
    bool
        True if the database is ready to use, False if something
        went wrong (e.g. the data/ folder couldn't be created or
        the database file couldn't be opened).
    """
    connection = None
    try:
        connection = _get_connection()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL UNIQUE,
                added_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if connection is not None:
            connection.close()


def add_note(company, title, content):
    """
    Create a new note for a company.

    Parameters
    ----------
    company : str
        The ticker or company identifier this note belongs to.
    title : str
        Note title. Should already be validated as non-empty by the
        caller - this function does not silently accept blank data,
        but it also doesn't re-validate; that's the page's job.
    content : str
        Note body text.

    Returns
    -------
    int or None
        The new note's id on success, or None if the note could not
        be saved (e.g. a database error). Callers should check for
        None and tell the user the save failed, rather than assuming
        it succeeded.
    """
    connection = None
    try:
        now = datetime.now().isoformat(timespec="seconds")
        connection = _get_connection()
        cursor = connection.execute(
            """
            INSERT INTO notes (company, title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company, title, content, now, now),
        )
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        return None
    finally:
        if connection is not None:
            connection.close()


def get_notes(company):
    """
    Fetch all notes for a given company, most recently updated first.

    Parameters
    ----------
    company : str
        The ticker or company identifier to filter by.

    Returns
    -------
    list of dict
        Each dict has keys: id, company, title, content, created_at,
        updated_at. Returns an empty list if there are no notes for
        this company, or if a database error occurs - callers can't
        tell "no notes" apart from "database error" from this alone,
        but init_db()'s return value should be checked first to catch
        setup problems.
    """
    connection = None
    try:
        connection = _get_connection()
        rows = connection.execute(
            # Secondary sort by id DESC breaks ties when two notes are
            # created/updated within the same second (updated_at has only
            # 1-second resolution), so ordering stays correct even then.
            "SELECT * FROM notes WHERE company = ? ORDER BY updated_at DESC, id DESC",
            (company,),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []
    finally:
        if connection is not None:
            connection.close()


def get_note(note_id):
    """
    Fetch a single note by its id.

    Returns
    -------
    dict or None
        The note as a dict, or None if no note with that id exists
        (or a database error occurred).
    """
    connection = None
    try:
        connection = _get_connection()
        row = connection.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        return dict(row) if row else None
    except sqlite3.Error:
        return None
    finally:
        if connection is not None:
            connection.close()


def update_note(note_id, title, content):
    """
    Update an existing note's title and content, and refresh its
    updated_at timestamp.

    Returns
    -------
    bool
        True if the update succeeded, False otherwise (database
        error, or no note with that id existed).
    """
    connection = None
    try:
        now = datetime.now().isoformat(timespec="seconds")
        connection = _get_connection()
        cursor = connection.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
            (title, content, now, note_id),
        )
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        if connection is not None:
            connection.close()


def delete_note(note_id):
    """
    Delete a note by its id.

    Returns
    -------
    bool
        True if a note was deleted, False if no note with that id
        existed or a database error occurred.
    """
    connection = None
    try:
        connection = _get_connection()
        cursor = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        if connection is not None:
            connection.close()


def add_to_watchlist(company):
    """
    Add a company to the watchlist.

    Parameters
    ----------
    company : str
        The ticker identifier to watch, e.g. "TCS.NS".

    Returns
    -------
    str
        "added" if the company was newly added,
        "duplicate" if it was already on the watchlist (no row was
            inserted - the UNIQUE constraint on the company column is
            the actual source of truth here, not just a pre-check in
            the page, so this is safe even without checking first),
        "error" if a database error occurred for some other reason.
    """
    connection = None
    try:
        now = datetime.now().isoformat(timespec="seconds")
        connection = _get_connection()
        connection.execute(
            "INSERT INTO watchlist (company, added_at) VALUES (?, ?)",
            (company, now),
        )
        connection.commit()
        return "added"
    except sqlite3.IntegrityError:
        # UNIQUE constraint violation - company is already watchlisted.
        return "duplicate"
    except sqlite3.Error:
        return "error"
    finally:
        if connection is not None:
            connection.close()


def get_watchlist():
    """
    Fetch all watchlisted companies, most recently added first.

    Returns
    -------
    list of dict
        Each dict has keys: id, company, added_at. Returns an empty
        list if the watchlist is empty, or if a database error
        occurs - callers can't tell these apart from this alone, but
        init_db()'s return value should be checked first to catch
        setup problems.
    """
    connection = None
    try:
        connection = _get_connection()
        rows = connection.execute(
            # Secondary sort by id DESC breaks ties when two companies
            # are added within the same second (added_at has only
            # 1-second resolution), same reasoning as get_notes().
            "SELECT * FROM watchlist ORDER BY added_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []
    finally:
        if connection is not None:
            connection.close()


def remove_from_watchlist(company):
    """
    Remove a company from the watchlist.

    Parameters
    ----------
    company : str
        The ticker identifier to remove, e.g. "TCS.NS".

    Returns
    -------
    bool
        True if a company was removed, False if it wasn't on the
        watchlist or a database error occurred.
    """
    connection = None
    try:
        connection = _get_connection()
        cursor = connection.execute(
            "DELETE FROM watchlist WHERE company = ?", (company,)
        )
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        if connection is not None:
            connection.close()


def is_watchlisted(company):
    """
    Check whether a company is currently on the watchlist.

    Useful for the page to decide what message to show *before*
    attempting to add a company - but add_to_watchlist() remains the
    authoritative check via the database's UNIQUE constraint, so this
    function existing doesn't introduce a race condition risk.

    Returns
    -------
    bool
        True if the company is on the watchlist, False if it isn't
        or if a database error occurred.
    """
    connection = None
    try:
        connection = _get_connection()
        row = connection.execute(
            "SELECT 1 FROM watchlist WHERE company = ?", (company,)
        ).fetchone()
        return row is not None
    except sqlite3.Error:
        return False
    finally:
        if connection is not None:
            connection.close()

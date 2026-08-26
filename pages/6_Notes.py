"""
Notes page.
"""

import streamlit as st

from services.companies import INDIAN_COMPANIES
from services.database import add_note, delete_note, get_notes, init_db, update_note

st.title("Notes")

if not INDIAN_COMPANIES:
    st.error("No companies are available to attach notes to.")
    st.stop()

db_ready = init_db()
if not db_ready:
    st.error("Could not set up the notes database. Notes cannot be saved or loaded right now - please check that the app has permission to create files in the data/ folder.")
    st.stop()

company_name = st.selectbox("Select a company", options=list(INDIAN_COMPANIES.keys()))
ticker = INDIAN_COMPANIES[company_name]

st.subheader("New Note")

st.session_state.setdefault("new_note_form_key", 0)
form_key = st.session_state["new_note_form_key"]

new_title = st.text_input("Title", key=f"new_title_{form_key}")
new_content = st.text_area("Note", key=f"new_content_{form_key}", height=120)

if st.button("Save Note"):
    if not new_title.strip() or not new_content.strip():
        st.error("Please enter both a title and note content before saving.")
    else:
        note_id = add_note(ticker, new_title.strip(), new_content.strip())
        if note_id is not None:
            st.success("Note saved.")
            st.session_state["new_note_form_key"] += 1
            st.rerun()
        else:
            st.error("Something went wrong saving your note. Please try again.")

st.subheader(f"Existing Notes — {company_name}")

notes = get_notes(ticker)

if not notes:
    st.info("No notes yet for this company. Add one above to get started.")
else:
    for note in notes:
        note_id = note["id"]
        is_editing = st.session_state.get("editing_note_id") == note_id

        header = f"{note['title']}  •  Updated {note['updated_at']}"
        with st.expander(header, expanded=is_editing):
            if is_editing:
                edited_title = st.text_input("Title", value=note["title"], key=f"edit_title_{note_id}")
                edited_content = st.text_area("Note", value=note["content"], key=f"edit_content_{note_id}", height=150)

                save_col, cancel_col = st.columns(2)
                if save_col.button("Save Changes", key=f"save_{note_id}"):
                    if not edited_title.strip() or not edited_content.strip():
                        st.error("Title and note content cannot be empty.")
                    else:
                        success = update_note(note_id, edited_title.strip(), edited_content.strip())
                        if success:
                            st.session_state.pop("editing_note_id", None)
                            st.rerun()
                        else:
                            st.error("Something went wrong saving your changes. Please try again.")
                if cancel_col.button("Cancel", key=f"cancel_edit_{note_id}"):
                    st.session_state.pop("editing_note_id", None)
                    st.rerun()
            else:
                st.write(note["content"])
                st.caption(f"Created {note['created_at']}")

                edit_col, delete_col = st.columns(2)
                if edit_col.button("Edit", key=f"edit_{note_id}"):
                    st.session_state["editing_note_id"] = note_id
                    st.rerun()
                if delete_col.button("Delete", key=f"delete_{note_id}"):
                    st.session_state[f"confirm_delete_{note_id}"] = True

                if st.session_state.get(f"confirm_delete_{note_id}"):
                    st.warning("Delete this note? This cannot be undone.")
                    yes_col, no_col = st.columns(2)
                    if yes_col.button("Yes, delete", key=f"confirm_yes_{note_id}"):
                        deleted = delete_note(note_id)
                        st.session_state.pop(f"confirm_delete_{note_id}", None)
                        if not deleted:
                            st.error("Could not delete this note. Please try again.")
                        st.rerun()
                    if no_col.button("Cancel", key=f"confirm_no_{note_id}"):
                        st.session_state.pop(f"confirm_delete_{note_id}", None)
                        st.rerun()

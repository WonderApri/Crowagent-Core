"""
Entry point for the CrowAgent Streamlit application.
"""
import sys
import os

# Ensure the repository root is in sys.path
sys.path.append(os.path.dirname(__file__))

import streamlit as st


def _check_password() -> bool:
    """Return True if the user has supplied the correct beta password."""
    required = os.environ.get("CROWAGENT_BETA_PASSWORD", "")

    # No password configured → open access (local dev default)
    if not required:
        return True

    if st.session_state.get("_authenticated"):
        return True

    st.set_page_config(page_title="CrowAgent — Beta Access", page_icon="🔒")
    st.markdown("## 🔒 CrowAgent Beta")
    st.markdown("This platform is in private beta. Enter the access password to continue.")
    entered = st.text_input("Password", type="password", key="_pw_input")
    if st.button("Enter"):
        if entered == required:
            st.session_state["_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    return False


if not _check_password():
    st.stop()

from app import main

if __name__ == "__main__":
    main.run()
else:
    main.run()

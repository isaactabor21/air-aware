import streamlit as st
import time


def start_view_transition(target_view, message, action=None, payload=None):
    """
    Queue a full-screen transition overlay before navigating to another view.
    """
    st.session_state.transition_active = True
    st.session_state.transition_phase = "show"
    st.session_state.transition_target = target_view
    st.session_state.transition_message = message
    st.session_state.transition_action = action
    st.session_state.transition_payload = payload
    st.session_state.transition_started_at = time.monotonic()
    st.session_state.transition_hold_until = None
    st.session_state.transition_error = None
    st.rerun()

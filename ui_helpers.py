"""
UI helper functions for the Streamlit dashboard.
"""

from html import escape

import streamlit as st


def get_query_param_value(params, key: str, default: str = "") -> str:
    """Return a query param as a normalized string."""
    value = params.get(key, default)

    if isinstance(value, list):
        return str(value[0] if value else default).strip()

    return str(value).strip()


def is_embed_mode(params) -> bool:
    """Return whether the app is being rendered in embedded mode.

    Uses app_embed because Streamlit's own embed=true param is consumed by
    the JS frontend and never forwarded to Python's st.query_params.
    """
    return get_query_param_value(params, "app_embed").lower() == "true"


def apply_embed_styles(params) -> bool:
    """Remove default framed styling when the app is embedded."""
    is_embedded = is_embed_mode(params)

    if not is_embedded:
        return False

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        hr {
            display: none;
        }

        /* Hide header, decoration stripe, and footer */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stBottom"],
        footer {
            display: none !important;
            visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    return True


def render_title(text: str, is_embedded: bool) -> None:
    """Render a page title, using a compact style in embedded mode."""
    if is_embedded:
        st.markdown(
            (
                '<h3 style="font-size: 2.2rem !important; font-weight: 600; '
                'margin: 0.25rem 0 0.5rem; line-height: 1.3;">'
                f"{escape(text)}"
                "</h3>"
            ),
            unsafe_allow_html=True,
        )
        return

    st.title(text)


def render_subheader(text: str, is_embedded: bool) -> None:
    """Render a subheader only outside embedded mode."""
    if not is_embedded:
        st.subheader(text)

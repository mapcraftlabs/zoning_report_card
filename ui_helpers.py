"""
UI helper functions for the Streamlit dashboard.
"""

from html import escape

import streamlit as st


def is_embed_mode(params) -> bool:
    """Return whether the app is being rendered in embedded mode."""
    embed_param = str(params.get("embed", params.get("embedded", "false"))).lower()
    return embed_param in {"1", "true", "yes"}


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

        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stPlotlyChart"],
        [data-testid="stDataFrame"] {
            border: none !important;
            box-shadow: none !important;
            border-radius: 0 !important;
            background: transparent !important;
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
                '<h3 style="font-size: 1rem; font-weight: 600; '
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

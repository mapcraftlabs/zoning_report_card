"""
UI helper functions for the Streamlit dashboard.
"""

import streamlit as st


def apply_embed_styles(params) -> None:
    """Remove default framed styling when the app is embedded."""
    embed_param = str(params.get("embed", params.get("embedded", "false"))).lower()
    is_embedded = embed_param in {"1", "true", "yes"}

    if not is_embedded:
        return

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

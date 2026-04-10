"""
UI helper functions for the Streamlit dashboard.
"""

from html import escape

import streamlit as st
import streamlit.components.v1 as components


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

        /* Remove borders and rounded corners */
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlock"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMainBlockContainer"] {
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }

        .embed-title {
            font-size: 1.25rem;
        }

        /* Hide header, decoration stripe, footer, and chart fullscreen button */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stBottom"],
        [data-testid="StyledFullScreenButton"],
        footer,
        div:has(> a[href*="utm_medium=oembed"]),
        div:has(a[href*="utm_medium=oembed"]) {
            display: none !important;
            visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # CSS :has() may be stripped — use JS as a reliable fallback to hide the
    # "Built with Streamlit / Fullscreen" oembed footer.
    components.html(
        """
        <script>
        function hideOembedFooter() {
            const doc = window.parent.document;
            doc.querySelectorAll('a[href*="utm_medium=oembed"]').forEach(a => {
                let el = a;
                while (el && el.parentElement && el.parentElement.tagName !== 'BODY') {
                    el = el.parentElement;
                }
                if (el) el.style.display = 'none';
            });
        }
        const observer = new MutationObserver(hideOembedFooter);
        observer.observe(window.parent.document.documentElement, { childList: true, subtree: true });
        hideOembedFooter();
        </script>
        """,
        height=0,
    )

    return True


def render_title(text: str, is_embedded: bool) -> None:
    """Render a page title, using a compact style in embedded mode."""
    if is_embedded:
        st.markdown(
            (
                '<div class="embed-title" style="font-weight: 600; '
                'margin: 0.25rem 0 0.5rem; line-height: 1.3;">'
                f"{escape(text)}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        return

    st.title(text)


def render_subheader(text: str, is_embedded: bool) -> None:
    """Render a subheader only outside embedded mode."""
    if not is_embedded:
        st.subheader(text)

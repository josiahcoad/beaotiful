from bokeh.models.widgets import Div
import streamlit as st


def go_to_link(url):
    js = f"window.open('{url}')"  # New tab or window
    js = f"window.location.href = '{url}'"  # Current tab
    html = '<img src onerror="{}">'.format(js)
    div = Div(text=html)
    st.bokeh_chart(div)

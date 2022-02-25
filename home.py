import streamlit as st
import pandas as pd
import numpy as np

st.title('Uber pickups in NYC')


df = pd.read_csv('nutritional_benefits.csv', index_col='item')

options = df.index

checkboxes = {}
col1, col2 = st.columns(2)

with col1:
    for option in options:
        checkboxes[option] = st.checkbox(option, value=False)

checkboxes = pd.Series(checkboxes, name='selected')
df = df.join(checkboxes)

# print(df[df.selected == True].sum(0))
with col2:
    st.bar_chart(df[df.selected == True].drop('selected', 1).sum(0))

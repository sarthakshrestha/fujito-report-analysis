import streamlit as st
from io import BytesIO
import io

import boto3
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time


df = st.session_state["df"]

st.title("Collection Analysis")

if df is None:
    st.markdown("### No Data Available")
else:
    st.divider()
    # Remaining Balance Analysis
    if 'Remaining Balance to Collect' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Customers with the Most Remaining Balance (Top 10)", expanded=True):
            remaining_balance = df[df['Remaining Balance to Collect'] > 0][['Customer Name', 'Remaining Balance to Collect']].sort_values(by='Remaining Balance to Collect', ascending=False).head(10)
            chart = alt.Chart(remaining_balance).mark_bar().encode(
            x=alt.X('Customer Name:N', 
                    sort='-y',
                    axis=alt.Axis(title='Customer Name', labelAngle=-45)),
            y=alt.Y('Remaining Balance to Collect:Q',
                    axis=alt.Axis(title='Remaining Balance (Rs.)')),
            color=alt.Color('Remaining Balance to Collect:Q',
                        scale=alt.Scale(scheme='blues'),
                        legend=alt.Legend(title='Balance (Rs.)')),
            tooltip=[
                alt.Tooltip('Customer Name:N', title='Customer'),
                alt.Tooltip('Remaining Balance to Collect:Q', 
                        title='Remaining Balance (In Rupees)',
                        format=',.2f')
            ]
        ).properties(
            title='Top 10 Customers by Remaining Balance',
            width=600,
            height=400
        )

        # Add text labels on top of bars
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5
        ).encode(
            text=alt.Text('Remaining Balance to Collect:Q', format=',.0f')
        )

        final_chart = (chart + text).interactive()
        st.altair_chart(final_chart, use_container_width=True)
        st.dataframe(remaining_balance, use_container_width=True)

            

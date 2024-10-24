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

if df is None:
    st.title('Overdue Analysis')
    st.markdown("### No Data Available")
else:
    st.title('Overdue Analysis')
    st.divider()
    # Top customers with most Overdue PDCs
    st.subheader("Overdue PDCs")
    if 'No. of Overdue PDCs' in df.columns and 'Customer Name' in df.columns and 'PDC Max Age' in df.columns:
            overdue_pdc = df[df['No. of Overdue PDCs'] > 0][['Customer Name', 'No. of Overdue PDCs', 'PDC Max Age', 'Total Overdue Bills']].sort_values(by='No. of Overdue PDCs', ascending=False)
            overdue_pdc['Total Overdue Bills'] = overdue_pdc['Total Overdue Bills'].astype(int)
            st.dataframe(overdue_pdc, use_container_width=True, hide_index=True)

    if 'Overdue PDC' in df.columns and 'Customer Name' in df.columns:
            st.subheader("Overdue Post-Dated Cheque Analysis")
            
            overdue_pdc = df[['Customer Name', 'Overdue PDC']].sort_values(by='Overdue PDC', ascending=False)
            overdue_pdc = overdue_pdc[overdue_pdc['Overdue PDC'] > 0]
            
            chart = alt.Chart(overdue_pdc).mark_bar().encode(
                x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Overdue PDC:Q', axis=alt.Axis(title='Overdue PDC Amount')),
                color=alt.Color('Overdue PDC:Q', scale=alt.Scale(scheme='oranges')),
                tooltip=['Customer Name', 'Overdue PDC']
            ).properties(
                title='Overdue PDC Amount by Customer',
                width=600,
                height=400
            )
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(overdue_pdc, use_container_width=True, hide_index=True)

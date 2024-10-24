from io import BytesIO
import io

import boto3
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time


df = st.session_state["df"]

st.title("Bill Analysis")

if df is None:
    st.markdown("### No Data Available")
else:
    st.divider()

    if 'LBP' in df.columns and 'LBS' in df.columns and 'Customer Name' in df.columns:
                st.subheader("LBP (Last Bill Paid) and LBS (Last Bill Sent) Analysis")
                
                lbp_lbs = df[['Customer Name', 'LBP', 'LBS']].sort_values(by='LBS', ascending=False)
                

                chart = alt.Chart(lbp_lbs).mark_bar().encode(
                    x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('Days Since Last Payment:Q', axis=alt.Axis(title='Days')),
                    color=alt.Color('Days Since Last Payment:Q', scale=alt.Scale(scheme='viridis')),
                    tooltip=['Customer Name', 'LBP', 'LBS']
                ).properties(
                    title='Days Since Last Payment by Customer',
                    width=600,
                    height=400
                )
                
                st.dataframe(lbp_lbs, use_container_width=True, hide_index=True)
                
    if 'PDC Max Age' in df.columns and 'Customer Name' in df.columns:
            st.subheader("Post-Dated Cheque (PDC) Analysis")
            
            # PDC Max Age Analysis
            pdc_age = df[['Customer Name', 'PDC Max Age']].sort_values(by='PDC Max Age', ascending=False)
            
            chart = alt.Chart(pdc_age).mark_bar().encode(
                x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('PDC Max Age:Q', axis=alt.Axis(title='PDC Max Age (Days)')),
                color=alt.Color('PDC Max Age:Q', scale=alt.Scale(scheme='reds')),
                tooltip=['Customer Name', 'PDC Max Age']
            ).properties(
                title='PDC Max Age by Customer',
                width=600,
                height=400
            )
            
            st.dataframe(pdc_age, use_container_width=True, hide_index=True)

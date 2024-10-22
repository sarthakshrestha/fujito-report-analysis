from io import BytesIO
import io

import boto3
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time


df = st.session_state["df"]

st.subheader("Bill Analysis")


if 'LBP' in df.columns and 'LBS' in df.columns and 'Customer Name' in df.columns:
            st.subheader("LBP (Last Bill Paid) and LBS (Last Bill Sent) Analysis")
            
            lbp_lbs = df[['Customer Name', 'LBP', 'LBS']].sort_values(by='LBS', ascending=False)
            
            # Calculate the difference between LBS and LBP
            lbp_lbs['Days Since Last Payment'] = lbp_lbs['LBS'] - lbp_lbs['LBP']
            
            chart = alt.Chart(lbp_lbs).mark_bar().encode(
                x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Days Since Last Payment:Q', axis=alt.Axis(title='Days')),
                color=alt.Color('Days Since Last Payment:Q', scale=alt.Scale(scheme='viridis')),
                tooltip=['Customer Name', 'LBP', 'LBS', 'Days Since Last Payment']
            ).properties(
                title='Days Since Last Payment by Customer',
                width=600,
                height=400
            )
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(lbp_lbs, use_container_width=True)
            
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
        
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(pdc_age, use_container_width=True)

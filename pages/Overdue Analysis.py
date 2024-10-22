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


st.subheader('Overdue Analysis')


if 'Reason' in df.columns and 'Customer Name' in df.columns:

        def get_overdue_reasons(row):
            reasons = []
            
            if row['Active/ Non-Active'] == 'Active':
                # Convert Payment Terms to string
                payment_terms = str(row['Payment Terms'])
                
                if payment_terms.startswith('LC'):
                    if row['Balance (Latest)'] < row['LC Value'] * 1.1:
                        reasons.append('Green')
                    else:
                        reasons.append('Need LC')
                elif row['Remaining Balance to Collect'] < 2500:
                    reasons.append('Green')
                elif row['Total Overdue Bills'] == row['Balance (Latest)']:
                    reasons.append('All Bills are Overdue against credit days')
                elif row['Balance (Latest)'] > 0:
                    if payment_terms.startswith('PDC'):
                        if row['Minimum PDC Requirement'] > 0:
                            reasons.append('Required PDC')
                        if row['PDC Max Age'] >= 14:
                            reasons.append('Overdue PDC older than 14 days')
                        elif 0 < row['PDC Max Age'] < 14:
                            reasons.append('Overdue PDC days between 0-14 days')
                        if row['Total (PDC) in hand'] >= row['Bill > 7 Days']:
                            reasons.append('Green')
                        elif row['Total (PDC) in hand'] >= row['Bill > 7 Days'] * 0.5:
                            reasons.append('Yellow')
                        else:
                            reasons.append('Red')
                    elif payment_terms == 'Non-PDC':
                        if row['No. of Overdue Bills'] > 2 and row['Total Overdue Bills'] > 2500:
                            reasons.append(f"No. of overdue bills above credit days - {row['No. of Overdue Bills']}")
                        elif 0 < row['No. of Overdue Bills'] <= 2 and row['Total Overdue Bills'] > 2500:
                            reasons.append('No. of overdue bills between 1-2')
                        elif row['Balance (Latest)'] <= row['Credit Limit']:
                            reasons.append('Green')
                        elif row['Balance (Latest)'] <= row['Credit Limit'] * 1.25:
                            reasons.append('Balance is less than 125% of limit')
                        else:
                            reasons.append('Balance is more than limit')
                    elif payment_terms == 'Cash':
                        if row['Balance (Latest)'] > 0:
                            reasons.append('Cash needed')
                        else:
                            reasons.append('Green')
                else:
                    reasons.append('Green')
            else:
                reasons.append('Inactive')
            
            return ' | '.join(reasons)
        
        df['Reasons'] = df.apply(get_overdue_reasons, axis=1)
        overdue_reasons = df[df['Remaining Balance to Collect'] > 0][['Customer Name', 'Reasons', 'Remaining Balance to Collect',  'To change to green']]
        overdue_reasons = overdue_reasons.sort_values(by='Remaining Balance to Collect', ascending=False)
        st.caption("Remaining Balance with th reason to change to green")

        st.dataframe(overdue_reasons, use_container_width=True)

        # Apply the function to get overdue reasons
        df['Reasons'] = df.apply(get_overdue_reasons, axis=1)

        # Filter rows where 'Reasons' is not empty
        overdue_reasons = df[df['Reasons'].str.strip() != ''][['Customer Name', 'Reasons', 'To change to green']]
        overdue_reasons = overdue_reasons.sort_values(by='Customer Name', ascending=False)

        # Display the DataFrame with specified column configurations
        # st.divider()
        # st.subheader("Customer with various reasons")

        # st.dataframe(
        #     overdue_reasons,
        #     use_container_width=True,
        #     column_config={
        #         "Customer Name": st.column_config.TextColumn(width="medium"),
        #         "Reasons": st.column_config.TextColumn(width="large"),
        #         "To change to green": st.column_config.TextColumn(width="medium")
        #     }
        # )




# Top customers with most Overdue PDCs
st.subheader("Overdue PDCs")
if 'No. of Overdue PDCs' in df.columns and 'Customer Name' in df.columns and 'PDC Max Age' in df.columns:
        overdue_pdc = df[df['No. of Overdue PDCs'] > 0][['Customer Name', 'No. of Overdue PDCs', 'PDC Max Age']].sort_values(by='No. of Overdue PDCs', ascending=False)
        st.dataframe(overdue_pdc, use_container_width=True)

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
        st.dataframe(overdue_pdc, use_container_width=True)

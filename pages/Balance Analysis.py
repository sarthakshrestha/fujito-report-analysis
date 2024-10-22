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


st.subheader("Overdue Balance Analysis")

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


if 'Balance Cash' in df.columns and 'PDC' in df.columns and 'Customer Name' in df.columns:
    with st.expander("Balance Cash and PDC Analysis", expanded=True):
        st.subheader("Balance Cash and PDC Analysis")
        
        balance_pdc = df[['Customer Name', 'Balance Cash', 'PDC']].sort_values(by='Balance Cash', ascending=False)
        
        # Melt the dataframe to create a long format for stacked bar chart
        balance_pdc_melted = pd.melt(balance_pdc, id_vars=['Customer Name'], var_name='Type', value_name='Amount')
        
        chart = alt.Chart(balance_pdc_melted).mark_bar().encode(
            x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Amount:Q', stack='zero'),
            color=alt.Color('Type:N', scale=alt.Scale(domain=['Balance Cash', 'PDC'], range=['#1f77b4', '#ff7f0e'])),
            tooltip=['Customer Name', 'Type', 'Amount']
        ).properties(
            title='Balance Cash and PDC by Customer',
            width=600,
            height=400
        )
        
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(balance_pdc, use_container_width=True)


    if 'Balance (Latest)' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Average Balance of Customers ", expanded=True):
            st.subheader("Average Balance of Customers")
            
            # Calculate average balance and sort by balance amount
            average_balance = df.groupby('Customer Name')['Balance (Latest)'].mean().reset_index()
            average_balance.columns = ['Customer Name', 'Average Balance']
            average_balance = average_balance.sort_values(by='Average Balance', ascending=True)

            # Create two columns for the visualizations
          
            
          

            bar_chart = alt.Chart(average_balance).mark_bar().encode(
                x=alt.X('Customer Name', sort=None, title='Customer'),
                y=alt.Y('Average Balance', title='Average Balance'),
                color=alt.condition(
                    alt.datum['Average Balance'] > 10000,  # Example threshold
                    alt.value('green'),  # Color for balances above threshold
                    alt.value('red')     # Color for balances below threshold
                ),
                tooltip=[
                    alt.Tooltip('Customer Name', title='Customer'),
                    alt.Tooltip('Average Balance', title='Balance', format=',.2f')
                ]
            ).properties(
                height=400,
                title='Customer Average Balances Distribution'
            )

            st.altair_chart(bar_chart, use_container_width=True)


            line_chart = alt.Chart(average_balance).mark_line(
                point=alt.OverlayMarkDef(color="red", size=100)
            ).encode(
                x=alt.X('Customer Name', sort=None, title='Customer'),
                y=alt.Y('Average Balance', title='Average Balance'),
                tooltip=[
                    alt.Tooltip('Customer Name', title='Customer'),
                    alt.Tooltip('Average Balance', title='Balance', format=',.2f')
                ]
            ).properties(
                height=400,
                title='Customer Average Balances Distribution'
            ).configure_axis(
                labelAngle=-45
            )
            st.altair_chart(line_chart, use_container_width=True)

            st.markdown("**Detailed Balance Data**")
            st.dataframe(
                average_balance.style.format({'Average Balance': '{:,.2f}'}),
                use_container_width=True,
                height=400
            )

            
                # Add statistics
            st.markdown("**Summary Statistics:**")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                highest_balance = average_balance['Average Balance'].max()
                st.caption("Highest Average Balance")
                st.markdown(f"Rs. {highest_balance:,.2f}")
            with col_stats2:
                mean_balance = average_balance['Average Balance'].mean()
                st.caption(" Average Balance")
                st.markdown(f"Rs. {mean_balance:,.2f}")

            with col_stats3:
                lowest_balance = average_balance['Average Balance'].min()
                st.caption("Lowest Balance")
                st.markdown(f"Rs. {lowest_balance:,.2f}")
            
            
            
            # Add top and bottom 5 customers
            col_top, col_bottom = st.columns(2)
            
            with col_top:
                st.markdown("**Top 5 Customers by Balance**")
                top_5 = average_balance.nlargest(5, 'Average Balance')
                st.dataframe(
                    top_5.style.format({'Average Balance': '{:,.2f}'}),
                    use_container_width=True
                )
            
            with col_bottom:
                st.markdown("**Bottom 5 Customers by Balance**")
                bottom_5 = average_balance.nsmallest(5, 'Average Balance')
                st.dataframe(
                    bottom_5.style.format({'Average Balance': '{:,.2f}'}),
                    use_container_width=True
                )
            col_new = st.columns(1)

    st.divider()
   
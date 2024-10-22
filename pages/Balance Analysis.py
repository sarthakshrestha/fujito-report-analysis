import streamlit as st
from io import BytesIO
import pandas as pd
import altair as alt

# Check if 'df' is in session state; if not, initialize it
if 'df' not in st.session_state:
    st.session_state['df'] = None

# Access the DataFrame from session state
df = st.session_state['df']
st.title("Balance Analysis")

if df is None:
    st.markdown("### No Data Available")
else:
    st.divider()

    if 'Balance Cash' in df.columns and 'PDC' in df.columns and 'Customer Name' in df.columns:
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

st.divider()
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

        st.dataframe(balance_pdc, use_container_width=True, hide_index=True)

   
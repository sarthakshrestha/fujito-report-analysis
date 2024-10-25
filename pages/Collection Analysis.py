import streamlit as st
import pandas as pd
import altair as alt

# Assume the dataframe 'df' is loaded in session state
df = st.session_state["df"]

st.title("Collection Analysis")

if df is None:
    st.markdown("### No Data Available")
else:
    st.divider()
    
    # Remaining Balance Analysis
    if 'Remaining Balance to Collect' in df.columns and 'Customer Name' in df.columns:
        
        with st.expander("Customers with the Most Remaining Balance", expanded=True):
            
            # Dropdown for selecting the number of top customers to display
            top_x_options = [5, 10, 15, 20, 25]
            top_x = st.selectbox("Select the number of top customers to display", top_x_options, index=1)
            
            # Get the top X customers based on the selected option
            remaining_balance = df[df['Remaining Balance to Collect'] > 0][['Customer Name', 'Remaining Balance to Collect']].sort_values(by='Remaining Balance to Collect', ascending=False).head(top_x)
            
            # Create the bar chart
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
                title=f'Top {top_x} Customers by Remaining Balance',
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
            
            # Display the dataframe of top X customers
            st.dataframe(remaining_balance, use_container_width=True, hide_index=True)

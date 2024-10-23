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
    st.title("Customer Analysis")
    st.markdown("### No Data Available")
else:
    # Active/Non-Active Analysis
    st.title("Customer Analysis")
    st.divider()
    if "Active/ Non-Active" in df.columns:
        active_count = df[df["Active/ Non-Active"] == "Active"].shape[0]
        non_active_count = df[df["Active/ Non-Active"] == "Non-Active"].shape[0]
        
        st.success(f"Number of Active Accounts: {active_count}")
        st.warning(f"Number of Non-active Accounts: {non_active_count}")
        
        pie_data = pd.DataFrame({
            'Account Status': ['Active', 'Non-Active'],
            'Count': [active_count, non_active_count]
        })
        
        pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Account Status", type="nominal", scale=alt.Scale(domain=["Active", "Non-Active"], range=['#2ecc71', '#e74c3c']), legend=alt.Legend(title="Account Status")),
            tooltip=["Account Status", "Count"]
        ).properties(
            width=400,
            height=400,
            title="Ratio of Active vs Non-Active Accounts"
        )
        
        st.subheader("Customer Account Status")
        st.altair_chart(pie_chart, use_container_width=True)

        active_customers = df[df["Active/ Non-Active"] == "Active"][['Customer Name']]
        non_active_customers = df[df["Active/ Non-Active"] == "Non-Active"][['Customer Name']]

        with st.expander("Customer Accounts Overview of Active/Non-Active Accounts", expanded=True):
            col1, col2 = st.columns([3, 3])

            with col1:
                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                st.write("**Customers with Active Accounts:**")
                st.dataframe(active_customers, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                st.write("**Customers with Non-Active Accounts:**")
                st.dataframe(non_active_customers, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # Latest Status Analysis
    if 'Latest Status' in df.columns:
        green_count = df[df['Latest Status'] == 'Green'].shape[0]
        inactive_count = df[df['Latest Status'] == 'Inactive'].shape[0]
        red_count = df[df['Latest Status'] == 'Red'].shape[0]
        yellow_count = df[df['Latest Status'] == 'Yellow'].shape[0]

        status_counts_df = pd.DataFrame({
            'Status': ['Green', 'Inactive', 'Red', 'Yellow'],
            'Count': [green_count, inactive_count, red_count, yellow_count]
        })

        st.divider()

        st.subheader("**Count of Customers by Latest Status:**")

        st.markdown(f"**Green Status:** {green_count}")
        st.markdown(f"**Inactive Status:** {inactive_count}")
        st.markdown(f"**Red Status:** {red_count}")
        st.markdown(f"**Yellow Status:** {yellow_count}")


        status_counts = df.groupby("Latest Status")[['Customer Name', 'Agent']].apply(lambda x: x.values.tolist()).reset_index(name='Data')
        status_counts['Count'] = status_counts['Data'].apply(len)

        status_data = pd.DataFrame({
            'Status': status_counts['Latest Status'],
            'Count': status_counts['Count'],
            'Data': status_counts['Data']
        })
        
        status_bar_chart = alt.Chart(status_data).mark_bar().encode(
            x=alt.X('Status', title='Status'),
            y=alt.Y('Count', title='Count'),
            color=alt.Color(
                'Status:N',
                scale=alt.Scale(
                    domain=['Green', 'Inactive', 'Red', 'Yellow'],
                    range=['lightgreen', 'lightpink', 'lightcoral', 'lightyellow']
                ),
                legend=alt.Legend(title="Status")
            ),
            tooltip=[alt.Tooltip("Status", title="Status"), 
                    alt.Tooltip("Count", title="Count")]
        ).properties(
            width=400,
            height=400,
            title="Distribution of Latest Status"
        )
        
        st.subheader("Customer Account Status")
        st.altair_chart(status_bar_chart, use_container_width=True)

        st.divider()
        st.subheader("Agent Filtering with Status")

        # Define status_colors here
        status_colors = {
            'Green': 'darkgreen',
            'Inactive': 'darkblue',
            'Red': 'darkred',
            'Yellow': 'darkorange'
        }

        # Get unique Agents
        unique_agents = df['Agent'].unique()

        # Add Agent filter
        selected_agent = st.selectbox("Select Agent", 
                                    ['All Agents'] + list(unique_agents),
                                    key='agent_filter')

        selected_status = st.selectbox("Select Customer Status",
                                    status_data['Status'].unique(),
                                    key='customer_status')

        if selected_status in status_colors:
            st.markdown(
                f"<div style='background-color: {status_colors[selected_status]}; padding: 10px; border-radius: 5px; margin-top:10px; margin-bottom: 10px'>"
                f"<strong>Selected Status: {selected_status}</strong></div>",
                unsafe_allow_html=True
            )

        filtered_data = status_data[status_data['Status'] == selected_status]['Data'].values[0]

        # Apply Agent filter
        if selected_agent != 'All Agents':
            filtered_data = [item for item in filtered_data if item[1] == selected_agent]

        search_term = st.text_input("Search Customers or Agents 🔍", "", key='search')

        if search_term:
            filtered_data = [item for item in filtered_data
                            if search_term.lower() in item[0].lower() or search_term.lower() in item[1].lower()]

        st.write(f"**Customers and Agents for {selected_status}:**")
        if filtered_data:
            df_filtered = pd.DataFrame(filtered_data, columns=['Customer Name', 'Agent'])
            # Add the 'Latest Status' column
            df_filtered['Latest Status'] = selected_status
            # Reorder columns to have 'Latest Status' after 'Customer Name'
            df_filtered = df_filtered[['Customer Name', 'Latest Status', 'Agent']]
            st.dataframe(df_filtered, use_container_width=True, height=300)
        else:
            st.write("No customers or agents found.")


    # Separate section for Agents only


    # Separate section for Agents only

        st.subheader("Customer Visit Days Distribution")

        visit_days_cleaned = df['Visit Date'].dropna()
        visit_day_counts = visit_days_cleaned.value_counts().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ).reset_index()

        visit_day_counts.columns = ['Day', 'Count']

        bar_chart = alt.Chart(visit_day_counts).mark_bar().encode(
            x=alt.X('Day:N', title="Day of the Week", sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
            y=alt.Y('Count:Q', title="Number of Visits"),
            color=alt.Color('Day:N', legend=None),
            tooltip=['Day', 'Count']
        ).properties(
            title="Number of Visits per Day of the Week",
            width=700,
            height=400
        )

        st.altair_chart(bar_chart, use_container_width=True)

        selected_day = st.selectbox("Select a Day to see customers", visit_day_counts['Day'])

        if selected_day:
            customers_visiting = df[df['Visit Date'] == selected_day]['Customer Name']
            
            st.subheader(f"Customers visiting on {selected_day}")
            if not customers_visiting.empty:
                st.write(customers_visiting.reset_index(drop=True))
            else:
                st.write(f"No customers are visiting on {selected_day}.")
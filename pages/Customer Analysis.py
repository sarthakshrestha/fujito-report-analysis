
from io import BytesIO
import io

import boto3
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time


df = st.session_state["df"]

# Active/Non-Active Analysis
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

    st.subheader("**Status of Customers:**")


    st.markdown(f"**Green Status:** {green_count}")
    st.markdown(f"**Inactive Status:** {inactive_count}")
    st.markdown(f"**Red Status:** {red_count}")
    st.markdown(f"**Yellow Status:** {yellow_count}")

    def highlight_status(row):
        color_map = {
            'Green': 'darkgreen',
            'Inactive': 'darkblue',
            'Red': 'lightcoral',
            'Yellow': 'darkorange'
        }
        return [f'background-color: {color_map[row["Status"]]}' for _ in row]

    # st.dataframe(status_counts_df.style.apply(highlight_status, axis=1), use_container_width=True, hide_index=True)

    status_counts = df.groupby("Latest Status")['Customer Name'].apply(list).reset_index(name='Customers')
    status_counts['Count'] = status_counts['Customers'].apply(len)
    status_counts['Count'] = pd.to_numeric(status_counts['Count'], errors='coerce')

    status_data = pd.DataFrame({
        'Status': status_counts['Latest Status'],
        'Count': status_counts['Count'],
        'Customers': status_counts['Customers']
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
    st.subheader("Balance Analysis")


    with st.expander("View the Latest Status of Customers 📊", expanded=True):
        selected_status = st.selectbox("Select a Status", status_data['Status'].unique())

        status_colors = {
            'Green': 'lightgreen',
            'Inactive': 'lightblue',
            'Red': 'lightcoral',
            'Yellow': 'lightorange'
        }

        if selected_status in status_colors:
            st.markdown(f"<div style='background-color: {status_colors[selected_status]}; padding: 10px; border-radius: 5px; margin-top:10px; margin-bottom: 10px'>"
                f"<strong>Selected Status: {selected_status}</strong></div>", unsafe_allow_html=True)

        filtered_customers = status_data[status_data['Status'] == selected_status]['Customers'].values[0]
        search_term = st.text_input("Search Customers 🔍", "")

        if search_term:
            filtered_customers = [customer for customer in filtered_customers if search_term.lower() in customer.lower()]

        st.write(f"**Customers for {selected_status}:**")
        if filtered_customers:
            st.text_area("Filtered Customers", "\n".join(filtered_customers), height=300)
        else:
            st.write("No customers found.")

        # Assuming 'Visit Date' and 'Customer Name' exist in your dataframe
    if 'Visit Date' in df.columns and 'Customer Name' in df.columns:
        st.subheader("Customer Visit Days Distribution")

        # Drop null values (if any) from 'Visit Day'
        visit_days_cleaned = df['Visit Date'].dropna()

        # Count occurrences of each day of the week
        visit_day_counts = visit_days_cleaned.value_counts().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ).reset_index()

        visit_day_counts.columns = ['Day', 'Count']  # Rename columns for clarity

        # Create a bar chart using Altair
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

        # Display the chart in Streamlit
        st.altair_chart(bar_chart, use_container_width=True)

        # Select a day to filter customers visiting on that day
        selected_day = st.selectbox("Select a Day to see customers", visit_day_counts['Day'])

        if selected_day:
            # Filter the dataframe to show only customers visiting on the selected dayf
            customers_visiting = df[df['Visit Date'] == selected_day]['Customer Name']
            
            st.subheader(f"Customers visiting on {selected_day}")
            if not customers_visiting.empty:
                st.write(customers_visiting.reset_index(drop=True))  # Show the customers
            else:
                st.write(f"No customers are visiting on {selected_day}.")
   
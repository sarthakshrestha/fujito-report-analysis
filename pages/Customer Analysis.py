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
     st.subheader("Agent Filtering with Status")

     status_colors = {
            'Green': 'darkgreen',
            'Inactive': 'darkblue',
            'Red': 'darkred',
            'Yellow': 'darkorange'
        }

    # Define status_colors here
    

    # Define the get_overdue_reasons function
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

    # Apply the get_overdue_reasons function to create the 'Reasons' column


if 'Reasons' not in df.columns:
        df['Reasons'] = df.apply(get_overdue_reasons, axis=1)

# Get unique Agents
unique_agents = df['Agent'].unique()

    # Add Agent filter
selected_agent = st.selectbox("Select Agent", 
                            ['All Agents'] + list(unique_agents),
                            key='agent_filter')

selected_status = st.selectbox("Select Customer Status",
                            df['Latest Status'].unique(),
                            key='customer_status')

if selected_status in status_colors:
    st.markdown(
        f"<div style='background-color: {status_colors[selected_status]}; padding: 10px; border-radius: 5px; margin-top:10px; margin-bottom: 10px'>"
        f"<strong>Selected Status: {selected_status}</strong></div>",
        unsafe_allow_html=True
    )

# Filter data based on selected status and agent
filtered_df = df[df['Latest Status'] == selected_status]
if selected_agent != 'All Agents':
    filtered_df = filtered_df[filtered_df['Agent'] == selected_agent]

search_term = st.text_input("Search Customers or Agents 🔍", "", key='search')

if search_term:
    filtered_df = filtered_df[
        filtered_df['Customer Name'].str.contains(search_term, case=False) |
        filtered_df['Agent'].str.contains(search_term, case=False)
    ]

st.write(f"**Customers and Agents for {selected_status}:**")
if not filtered_df.empty:
    df_display = filtered_df[['Customer Name', 'Latest Status', 'Agent', 'Reasons', 'To change to green']]
    st.dataframe(df_display, use_container_width=True, height=300, hide_index=True)
else:
    st.write("No customers or agents found.")


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
status_comparison = df[['Customer Name', 'Agent', 'Last Week Status', 'Latest Status']].copy()

# Add a new column to indicate if the status has changed
status_comparison['Status Changed'] = status_comparison['Last Week Status'] != status_comparison['Latest Status']

# Create the expander for status comparison

st.subheader("Comparison of Last Week Status and Latest Status")

# Add a status filter
status_filter = st.selectbox("Filter by Status Change", ["All", "Changed", "Unchanged"])

# Add a search box
search_term = st.text_input("Search Customers or Agents 🔍", "", key='status_search')

# Filter the dataframe based on the status filter and search term
if status_filter == "Changed":
    filtered_df = status_comparison[status_comparison['Status Changed']]
elif status_filter == "Unchanged":
    filtered_df = status_comparison[~status_comparison['Status Changed']]
else:
    filtered_df = status_comparison

if search_term:
    filtered_df = filtered_df[
        filtered_df['Customer Name'].str.contains(search_term, case=False) |
        filtered_df['Agent'].str.contains(search_term, case=False)
    ]

# Display the filtered dataframe
st.write(f"**Status Comparison ({status_filter}):**")
if not filtered_df.empty:
    # Function to highlight changed status
    def highlight_changed(row):
        if row['Status Changed']:
            return ['margin: 0'] * len(row)
        return [''] * len(row)

    # Display the dataframe with highlighting
    display_df = filtered_df.drop(columns=['Status Changed'])
    st.dataframe(filtered_df.style.apply(highlight_changed, axis=1), use_container_width=True, height=400, hide_index=True)

    # Display summary statistics
    total_customers = len(filtered_df)
    changed_status = filtered_df['Status Changed'].sum()
    unchanged_status = total_customers - changed_status

    st.write(f"Total Customers: {total_customers}")
    st.write(f"Customers with Changed Status: {changed_status}")
    st.write(f"Customers with Unchanged Status: {unchanged_status}")
else:
    st.write("No customers or agents found.")

# Option to download the filtered data
if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="status_comparison.csv",
        mime="text/csv",
    )


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
            st.dataframe(active_customers, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.write("**Customers with Non-Active Accounts:**")
            st.dataframe(non_active_customers, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)


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
            st.dataframe(customers_visiting.reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.write(f"No customers are visiting on {selected_day}.")
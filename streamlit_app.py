import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time

# Page configuration (must be the first Streamlit command)
st.set_page_config(page_title='Fujito Report Analysis', page_icon='📊', layout='wide')

with open("styles.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Page title
st.title('Fujito Report Analysis')

with st.expander('About this app'):
    st.markdown('**What can this app do?**')
    st.info('This app allows users to upload an Excel file containing report data and performs a basic analysis on it.')
    
    st.markdown('**How to use the app?**')
    st.warning('To use the app, upload an Excel file using the file uploader in the sidebar. The app will then display various analyses and visualizations based on the uploaded data.')
    
    st.markdown('**Under the hood**')
    st.markdown('Libraries used:')
    st.code('''
    - Pandas for data wrangling
    - Numpy for numerical operations
    - Altair for chart creation
    - Streamlit for user interface
    ''', language='markdown')

# Sidebar for accepting input parameters
with st.sidebar:
    st.title('Upload Data')
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# Main content
if uploaded_file is not None:
    with st.status("Analyzing report...", expanded=True) as status:
        # Skip rows if necessary and use the appropriate row as the header
        df = pd.read_excel(uploaded_file, sheet_name="Main", skiprows=1)
        
        # Drop the first column (if it's unwanted)
        df = df.drop(df.columns[0], axis=1)
        
        st.write("**Preview of the Data**")
        st.write(df.head(5))

    # Check if "Active/Non-Active" column exists
    if "Active/ Non-Active" in df.columns:
        # Count the number of active and non-active accounts
        active_count = df[df["Active/ Non-Active"] == "Active"].shape[0]
        non_active_count = df[df["Active/ Non-Active"] == "Non-Active"].shape[0]
        
        # Show success message with the active count
        st.success(f"Number of Active Accounts: {active_count}")
        
        # Create a pie chart showing the ratio of Active to Non-Active accounts
        pie_data = pd.DataFrame({
            'Account Status': ['Active', 'Non-Active'],
            'Count': [active_count, non_active_count]
        })
        
        pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Account Status", type="nominal", legend=alt.Legend(title="Account Status")),
            tooltip=["Account Status", "Count"]
        ).properties(
            width=400,
            height=400,
            title="Ratio of Active vs Non-Active Accounts"
        )
        
        st.altair_chart(pie_chart, use_container_width=True)
    
    # Check if 'Latest Status' column exists
    if 'Latest Status' in df.columns:
        # Count the occurrences of each status and get corresponding customer names from column D
        status_counts = df.groupby("Latest Status")['Customer Name'].apply(list).reset_index(name='Customers')
        status_counts['Count'] = status_counts['Customers'].apply(len)

        # Ensure 'Count' is treated as numeric
        status_counts['Count'] = pd.to_numeric(status_counts['Count'], errors='coerce')

        # Create a DataFrame for the bar chart
        status_data = pd.DataFrame({
            'Status': status_counts['Latest Status'],
            'Count': status_counts['Count'],
            'Customers': status_counts['Customers']
        })
        
        # Create a bar chart showing the distribution of Latest Status
        status_bar_chart = alt.Chart(status_data).mark_bar().encode(
            x=alt.X('Status', title='Status'),
            y=alt.Y('Count', title='Count'),
            color=alt.Color(
                'Status:N',
                scale=alt.Scale(
                    domain=['Green', 'Inactive', 'Red', 'Yellow'],  # Define the statuses
                    range=['green', 'blue', 'red', 'yellow']    # Corresponding colors
                ),
                legend=alt.Legend(title="Status")
            ),
            tooltip=[alt.Tooltip("Status", title="Status"), 
                     alt.Tooltip("Count", title="Count")
                     ]
        ).properties(
            width=400,
            height=400,
            title="Distribution of Latest Status"
        )
        
        st.altair_chart(status_bar_chart, use_container_width=True)

        # Show a preview of the Latest Status of customers in an expander
        with st.expander("Preview of the Latest Status of Customers"):
            # Create a select box for statuses
            selected_status = st.selectbox("Select a Status", status_data['Status'].unique())

            # Filter the customers based on the selected status
            filtered_customers = status_data[status_data['Status'] == selected_status]['Customers'].values[0]

            # Create a search box for customer names
            search_term = st.text_input("Search Customers", "")

            # Filter customers based on the search term
            if search_term:
                filtered_customers = [customer for customer in filtered_customers if search_term.lower() in customer.lower()]

            # Display the filtered customer names in a text area
            st.write(f"**Customers for {selected_status}:**")
            if filtered_customers:
                st.text_area("Filtered Customers", "\n".join(filtered_customers), height=300)  # Updated to use text area
            else:
                st.write("No customers found.")
    
    # New section to calculate and display average balances
    if 'Balance (Latest)' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Average Balance of Customers"):
            st.subheader("Average Balance of Customers")
            average_balance = df.groupby('Customer Name')['Balance (Latest)'].mean().reset_index()
            average_balance.columns = ['Customer Name', 'Average Balance']
            
            # Display the average balance data
            st.write(average_balance, use_container_width=True)

    # New section to show top customers with the most Overdue PDCs
    if 'No. of Overdue PDCs' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Top Customers with Overdue PDCs"):
            overdue_pdc = df[df['No. of Overdue PDCs'] > 0][['Customer Name', 'No. of Overdue PDCs']].sort_values(by='No. of Overdue PDCs', ascending=False)
            st.subheader("Customers with Most Overdue PDCs")
            st.write(overdue_pdc, use_container_width=True)

    else:
        st.error("The 'Latest Status' column was not found in the 'Main' sheet.")

    status.update(label="Analysis complete", state="complete", expanded=False)
else:
    st.warning('👈 Upload the DPR File for Analysis.')
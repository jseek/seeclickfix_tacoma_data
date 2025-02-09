import streamlit as st

def issue_data_table(df):
    st.subheader("Issue Data Table")
    st.markdown("Details on each issue.")

    # Allow the user to select the number of rows per page
    page_size = st.selectbox("Select page size", options=[5, 10, 20, 50], index=1)

    # Initialize the current page in session state if it doesn't exist
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1

    total_rows = len(df)
    total_pages = (total_rows - 1) // page_size + 1

    # Create navigation buttons for pagination
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous") and st.session_state.page_number > 1:
            st.session_state.page_number -= 1

    with col3:
        if st.button("Next") and st.session_state.page_number < total_pages:
            st.session_state.page_number += 1

    # Display the current page number and total pages
    st.write(f"Page {st.session_state.page_number} of {total_pages}")

    # Calculate the index range for the current page and display the subset of the DataFrame
    start_idx = (st.session_state.page_number - 1) * page_size
    end_idx = start_idx + page_size
    df_page = df.iloc[start_idx:end_idx]

    st.dataframe(df_page)

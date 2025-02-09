import streamlit as st

def display_311_impact():
    """Function to display the importance of Tacoma's 311 system."""
    st.markdown(
        """
        Tacoma’s 311 system serves as a critical channel for residents to report non-emergency issues, 
        such as potholes, graffiti, illegal dumping, and homelessness-related concerns. 
        Effectively tracking and analyzing these reports is essential for improving city services, 
        increasing government accountability, and ensuring that all neighborhoods receive equitable attention.

        1. **Identifying Overburdened Areas**  
        By tracking 311 issues, city officials and community organizations can pinpoint areas that experience a 
        disproportionate share of reported problems. Some neighborhoods may face persistent infrastructure challenges 
        or environmental concerns, and data analysis helps highlight where resources should be allocated to improve conditions.

        2. **Holding Agencies Accountable**  
        Analyzing 311 response data allows residents and policymakers to assess how effectively different 
        departments and agencies address reported issues. By measuring response times and resolution rates, 
        the city can identify bottlenecks, improve efficiency, and ensure that problems are being addressed in a timely manner.

        3. **Detecting Chronic Issues & Repeat Offenders**  
        Tracking reports over time enables the identification of recurring problems in specific locations. 
        If certain areas repeatedly report the same issues—such as illegal dumping at the same site or 
        persistent potholes on key roads—this suggests the need for long-term solutions rather than temporary fixes.

        4. **Promoting Equitable City Services**  
        A data-driven approach to 311 issues allows for an analysis of disparities in service delivery across 
        different communities. If some neighborhoods experience significantly slower response times or lack adequate resolutions, 
        city officials can investigate and work toward more equitable distribution of resources.

        5. **Enhancing Public Engagement & Transparency**  
        Providing residents with access to 311 data fosters civic engagement and trust in local government. 
        When people see that their concerns are acknowledged and addressed, they are more likely to participate 
        in local governance and advocate for improvements in their communities.

        6. **Supporting Data-Driven Policy Decisions**  
        City planners and policymakers can use 311 data to inform infrastructure investments, budget allocations, 
        and strategic planning efforts. Data trends can help prioritize high-impact projects, ensuring that funds are spent 
        where they are needed most.
        """,
        unsafe_allow_html=True
    )

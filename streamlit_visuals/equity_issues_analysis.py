import streamlit as st
import plotly.express as px
import pandas as pd

def display_equity_issues_analysis(filtered_df, equity_population_df):
    """Function to compute and display issues vs. population by equity ID."""
    st.subheader("Issues and Population by Equity ID")

    # Group issues by equity ID
    issues_by_equity = filtered_df.groupby("equity_objectid")["id"].count().reset_index()
    issues_by_equity.columns = ["equity_objectid", "issue_count"]

    # Sum population by equity ID
    population_by_equity = equity_population_df.groupby("equity_objectid")["population"].sum().reset_index()

    # Merge issue counts and population data
    equity_issues_population = pd.merge(issues_by_equity, population_by_equity, on="equity_objectid", how="outer").fillna(0)

    # Create scatter plot
    fig = px.scatter(
        equity_issues_population,
        x="population",
        y="issue_count",
        text="equity_objectid",
        labels={"population": "Population", "issue_count": "Number of Issues"},
        title="Issues vs. Population by Equity ID"
    )
    fig.update_traces(textposition="top center")

    # Display plot in Streamlit
    st.plotly_chart(fig)

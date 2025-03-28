import streamlit as st
import pandas as pd
from datetime import timedelta, date
import plotly.express as px
from streamlit_app.visuals import issues_created_by_time_period

def heads_up(filtered_df):
    # Convert string dates to date objects
    filtered_df['created_at_date'] = pd.to_datetime(filtered_df['created_at'], errors='coerce').dt.date
    filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at'], errors='coerce').dt.date

    # Determine the current date as the max date in the created_at_date column
    current_date = filtered_df['created_at_date'].max()
        
    # Get the maximum created_at value from filtered_df and convert it to a date
    max_created_at = filtered_df['created_at'].max()
    current_date = max_created_at.date()

    # Define rolling 7-day periods:
    # Current period: from (current_date - 6 days) to current_date (inclusive)
    current_rolling_start = current_date - timedelta(days=6)
    # Previous period: from (current_date - 13 days) to (current_date - 7 days)
    previous_rolling_start = current_rolling_start - timedelta(days=7)
    previous_rolling_end = current_date - timedelta(days=7)

    # Filter the DataFrame for created and resolved issues in each rolling period,
    # excluding the current date from the current period
    created_at_current_df = filtered_df[
        (filtered_df['created_at_date'] >= current_rolling_start) & 
        (filtered_df['created_at_date'] < current_date)
    ]
    resolved_at_current_df = filtered_df[
        (filtered_df['resolved_at_date'] >= current_rolling_start) & 
        (filtered_df['resolved_at_date'] < current_date)
    ]
    created_at_previous_df = filtered_df[
        (filtered_df['created_at_date'] >= previous_rolling_start) & 
        (filtered_df['created_at_date'] <= previous_rolling_end)
    ]
    resolved_at_previous_df = filtered_df[
        (filtered_df['resolved_at_date'] >= previous_rolling_start) & 
        (filtered_df['resolved_at_date'] <= previous_rolling_end)
    ]
    
    value_column = 'summary'
    
    st.markdown("**Created (Last 7 Days vs Previous 7 Days)**")
    st.markdown(
        f"Comparing dates: **Last 7 Days:** {current_rolling_start} to {current_date} | **Previous 7 Days:** {previous_rolling_start} to {previous_rolling_end}"
    )
    created_card(
        created_at_current_df, 
        created_at_previous_df, 
        label_current="Issues Created (Last 7 Days)", 
        label_previous="Issues Created (Previous 7 Days)"
    )
    top_current_value = get_top_value(created_at_current_df, value_column)
    st.write(f"*Top Issue in Last 7 Days: {top_current_value} ({top_value_percent_of_whole(top_current_value, value_column, created_at_current_df)})*")
    
    st.write("---")
    
    st.markdown("**Resolved (Last 7 Days vs Previous 7 Days)**")
    st.markdown(
        f"Comparing dates: **Last 7 Days:** {current_rolling_start} to {current_date} | **Previous 7 Days:** {previous_rolling_start} to {previous_rolling_end}"
    )
    resolved_card(
        resolved_at_current_df, 
        resolved_at_previous_df, 
        label_current="Issues Resolved (Last 7 Days)", 
        label_previous="Issues Resolved (Previous 7 Days)"
    )
    top_resolved_value = get_top_value(resolved_at_current_df, value_column)
    st.write(f"*Top Issue Resolved in Last 7 Days: {top_resolved_value} ({top_value_percent_of_whole(top_resolved_value, value_column, resolved_at_current_df)})*")
    
    st.write("---")

    st.plotly_chart(plot_homeless_stacked_horizontal_bar_chart(created_at_current_df))

    st.write("---")

    st.plotly_chart(plot_summary_treemap(created_at_current_df))


def created_card(this_df, previous_df, label_current="Current Period", label_previous="Previous Period"):
    col1, col2, col3 = st.columns(3)
    with col1:
        card_metric(this_df, label_current)
    with col2:
        card_metric(previous_df, label_previous)
    with col3:
        card_delta_percent(this_df, previous_df, "Created")

def resolved_card(this_df, previous_df, label_current="Current Period", label_previous="Previous Period"):
    col1, col2, col3 = st.columns(3)
    with col1:
        card_metric(this_df, label_current)
    with col2:
        card_metric(previous_df, label_previous)
    with col3:
        card_delta_percent(this_df, previous_df, "Resolved")

def card_metric(df, label):
    count = df.shape[0]
    st.metric(label=label, value=count)

def card_delta_percent(current_df, previous_df, action):
    current_count = current_df.shape[0]
    previous_count = previous_df.shape[0]
    if previous_count == 0:
        delta_str = "N/A"
    else:
        delta = ((current_count - previous_count) / previous_count) * 100
        delta_str = f"{delta:.2f}% {'↑' if delta > 0 else '↓'}"
    st.metric(label=f"Delta % ({action}: Current vs Previous)", value=delta_str)

def get_top_value(df: pd.DataFrame, column: str = "summary") -> str:
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    return df[column].value_counts().idxmax()

def top_value_percent_of_whole(value, value_column, df):
    total_count = df[value_column].count()
    value_count = df[df[value_column] == value][value_column].count()
    return f"{value_count:,}, {(value_count / total_count) * 100:.2f}%"


def plot_homeless_stacked_horizontal_bar_chart(df, col='homeless_related'):
    """
    Creates a single horizontal stacked bar chart representing 100% of the data,
    partitioned by the percentage distribution of the values in the specified column.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing your data.
        col (str): The column to analyze. Default is 'homeless_related'.
        
    Returns:
        fig (plotly.graph_objects.Figure): A Plotly figure object.
        
    Usage:
        fig = plot_homeless_stacked_horizontal_bar_chart(your_dataframe)
        st.plotly_chart(fig)
    """
    # Count the values in the specified column.
    counts = df[col].value_counts()
    total = counts.sum()
    
    # Calculate percentages for each category.
    percentages = (counts / total * 100).round(2)
    
    # Create a DataFrame for plotting.
    # We'll use a dummy category so that all segments are in one stacked bar.
    data = pd.DataFrame({
        'Category': counts.index.astype(str),
        'Count': counts.values,
        'Percentage': percentages.values,
        'Dummy': 'All Records'
    })
    
    # Create the horizontal stacked bar chart.
    fig = px.bar(
        data,
        x='Percentage',
        y='Dummy',
        color='Category',
        orientation='h',
        text='Percentage',
        title='Homeless Related Distribution This Week'
    )
    
    # Update the trace to show percentage labels on each segment.
    fig.update_traces(texttemplate='%{text}%', textposition='inside')
    
    # Configure layout: stack bars and set the x-axis from 0 to 100.
    fig.update_layout(
        barmode='stack',
        xaxis_title='Percentage',
        yaxis_title='',
        xaxis_range=[0, 100],
        showlegend=True
    )
    
    return fig


def plot_summary_treemap(df, col='summary', threshold=5):
    """
    Creates a hierarchical treemap representing the distribution of values in the specified summary column.
    Categories with a percentage below the threshold are grouped under an "Other" node.
    When clicking "Other", the treemap expands to show the individual small categories.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing your data.
        col (str): The column to analyze. Default is 'summary'.
        threshold (float): Percentage threshold below which categories are grouped under "Other". Default is 5%.
        
    Returns:
        fig (plotly.graph_objects.Figure): A Plotly treemap figure.
    
    Usage:
        fig = plot_summary_treemap(your_dataframe)
        st.plotly_chart(fig)
    """
    import plotly.graph_objects as go
    import pandas as pd

    # Count the unique values and calculate percentages.
    counts = df[col].value_counts()
    total = counts.sum()
    percentages = (counts / total * 100).round(2)

    # Separate significant and small categories.
    significant = counts[percentages >= threshold]
    small = counts[percentages < threshold]
    significant_pct = percentages[percentages >= threshold]
    small_pct = percentages[percentages < threshold]

    # Build lists for the treemap hierarchy.
    ids = []
    labels = []
    parents = []
    values = []
    percents = []  # To hold percentage of the whole for hover display.

    # Root node.
    ids.append("All Records")
    labels.append("All Records")
    parents.append("")
    values.append(total)
    percents.append(100)

    # Add significant categories as direct children of the root.
    for cat in significant.index:
        ids.append(cat)
        labels.append(cat)
        parents.append("All Records")
        values.append(significant[cat])
        percents.append(significant_pct[cat])

    # For small categories, create an aggregated "Other" node.
    if not small.empty:
        other_value = small.sum()
        other_pct = small_pct.sum()
        ids.append("Other")
        labels.append("Other")
        parents.append("All Records")
        values.append(other_value)
        percents.append(other_pct)
        # Then add each small category as a child of "Other".
        for cat in small.index:
            # Create a unique id for each small category.
            ids.append("Other_" + cat)
            labels.append(cat)
            parents.append("Other")
            values.append(small[cat])
            percents.append(small_pct[cat])

    # Create the treemap figure using graph_objects.
    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        # Use customdata to pass the percentage value and show it in the hover.
        customdata=percents,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage of total: %{customdata:.2f}%<extra></extra>',
    ))
    fig.update_layout(title="Issue Distribution This Week")
    
    return fig
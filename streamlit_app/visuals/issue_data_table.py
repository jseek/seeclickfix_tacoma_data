import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def issue_data_table(df):
    st.subheader("Issue Data Table")
    st.markdown("Details on each issue.")

    # Generate word cloud
    st.subheader("Word Cloud of Issue Descriptions")
    text = " ".join(df["description"].dropna())  # Combine all descriptions
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

    # Display word cloud
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # Display data table
    st.dataframe(df)
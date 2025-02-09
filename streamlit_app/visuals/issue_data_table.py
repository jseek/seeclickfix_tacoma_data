import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

def issue_data_table(df):
    st.subheader("Issue Data Table")
    st.markdown("Details on each issue.")

    # Generate word cloud if description column exists and is not empty
    if "description" in df.columns and not df["description"].dropna().empty:
        st.subheader("Word Cloud of Issue Descriptions")

        # Combine all descriptions into a single string, excluding NaNs
        text = " ".join(df["description"].dropna())

        # Define stopwords
        stopwords = set(STOPWORDS)

        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color="white", 
            stopwords=stopwords, 
            colormap="viridis"
        ).generate(text)

        # Display word cloud
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("No valid descriptions available to generate a word cloud.")

    # Display data table
    st.dataframe(df)
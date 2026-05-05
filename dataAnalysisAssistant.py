import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

if "GEMINI_KEY" not in st.secrets:
    st.error("Missing API key. Add GEMINI_KEY to .streamlit/secrets.toml")
    st.stop()
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
st.title("🤔 Data Analysis Assistant")
try:
    uploaded = st.file_uploader("Upload CSV", type="csv")

    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head())
        data_summary = f"""Dataset: {uploaded.name}
    Rows: {len(df)}, Columns: {len(df.columns)}
    Column names: {', '.join(df.columns)}
    Data types:
    {df.dtypes.to_string()}
    Summary statistics:
    {df.describe().to_string()}
    First 5 rows:
    {df.head().to_string()}
    Missing values:
    {df.isnull().sum().to_string()}"""
         #  Chat interface 
    question = st.text_input("Ask about the data")
    step_by_step = st.checkbox(
        "Show reasoning (chain-of-thought)")
    if question:
        if step_by_step:
            prompt = (f"""{data_summary} 
                {question}\n\n
                Think step by step:\n
                1) What data is relevant?\n
                2) What patterns do you see?\n
                3) What are the limitations?\n
                4) Give your conclusion.""")
        else:
            prompt = question

        with st.spinner("Analyzing..."):
            r = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
            )
        st.markdown(r.text)

  
except Exception as e:
    print (f"Oops! Something went wrong: {str(e)}. Try again!")
    st.error(f"Oops! Something went wrong: {str(e)}. Try again!")
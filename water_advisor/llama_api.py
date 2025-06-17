import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
from dotenv import load_dotenv

def query_llama(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets["TOGETHER_API_KEY"]}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.status_code}\n{response.text}"
def build_prompt(user_query, basic_info):
    name = basic_info.get("name", "User")
    members = basic_info.get("family_members", "an unknown number of")
    
    return f"""
You are a household water conservation advisor.

This user is named {name}, has {members} family members.
you have to start the conversation like:
Hi {name}

Now respond to their question: "{user_query}"
"""

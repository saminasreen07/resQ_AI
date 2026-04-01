"""
ResQAI TN — Supabase Client
Single source of truth for the DB connection.
Usage: from supabase_client import get_client
"""
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

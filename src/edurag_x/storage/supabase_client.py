import os
from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from supabase import create_client


def get_supabase_client():

    try:
        supabase_url = st.secrets.get(
            "SUPABASE_URL",
            os.getenv("SUPABASE_URL")
        )

        supabase_key = st.secrets.get(
            "SUPABASE_KEY",
            os.getenv("SUPABASE_KEY")
        )

    except Exception:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase credentials are missing."
        )

    return create_client(
        supabase_url,
        supabase_key
    )
import streamlit as st
from sqlmodel import Session, select
from app.db import engine, User

st.title("Users & Tokens Dashboard")
with Session(engine) as s:
    users = s.exec(select(User)).all()
    st.table([{"username": u.username, "tokens": u.tokens} for u in users])

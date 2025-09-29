import streamlit as st
from sqlmodel import Session, select
from app.db import engine, User

st.set_page_config(page_title="Users & Tokens Admin", layout="centered")
st.title("Users & Tokens Dashboard")

# Table
with Session(engine) as s:
    users = s.exec(select(User)).all()
st.subheader("Current Users")
st.table([{"username": u.username, "tokens": u.tokens} for u in users])

# Add tokens
st.subheader("Add Tokens")
with st.form("add_tokens"):
    uname = st.text_input("Username")
    amount = st.number_input("Amount", min_value=1, step=1, value=5)
    submitted = st.form_submit_button("Add")
    if submitted:
        with Session(engine) as s:
            u = s.exec(select(User).where(User.username == uname)).first()
            if not u:
                st.error("User not found")
            else:
                u.tokens += int(amount)
                s.add(u); s.commit()
                st.success(f"Added {amount} tokens to {uname}")

# Delete user
st.subheader("Delete User")
with st.form("delete_user"):
    uname2 = st.text_input("Username to delete")
    confirm = st.checkbox("I understand this will permanently delete the user")
    submitted2 = st.form_submit_button("Delete")
    if submitted2:
        if not confirm:
            st.warning("Please confirm")
        else:
            with Session(engine) as s:
                u = s.exec(select(User).where(User.username == uname2)).first()
                if not u:
                    st.error("User not found")
                else:
                    s.delete(u); s.commit()
                    st.success(f"Deleted {uname2}")

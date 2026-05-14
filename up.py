# Sesiunea 26 – Integrare Streamlit cu baze de date, autentificare și deployment pe cloud

# site pt exersat sql: https://www.w3schools.com/sql/sql_intro.asp

# 1. Creare bază de date + conexiune SQLite
# Pas 1: Creăm fișierul bazei de date
import sqlite3

conn = sqlite3.connect('users_data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS raport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    valoare INTEGER,
    categorie TEXT
)
''')
conn.commit()

# Pas 2: Funcții de autentificare (login/register)
def register_user(username, password):
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()


def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

# 2. Interfața cu login și dashboard personalizat
import streamlit as st
import pandas as pd

st.title("Sistem securizat Streamlit + SQLite")
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Meniu", menu)

if choice == "Register":
    st.subheader("Creare cont")
    user = st.text_input("Username")
    pw = st.text_input("Parolă", type="password")

    if st.button("Creează cont"):
        register_user(user, pw)
        st.success("Cont creat cu succes!")

elif choice == "Login":
    st.subheader("Autentificare")
    user = st.text_input("Username")
    pw = st.text_input("Parolă", type="password")

    if st.button("Intră"):
        rezultat = login_user(user, pw)

        if rezultat:
            st.session_state['user'] = user
        else:
            st.error("Utilizator sau parolă greșită")

    # Dashboard – în AFARA if-ului de login
    if 'user' in st.session_state:
        st.success(f"Bine ai revenit, {user}!")
        st.session_state['user'] = user

        # Dashboard
        st.subheader("Dashboard")
        val = st.number_input("Introdu valoare")
        cat = st.selectbox("Categorie", ["Alimente", "Transport", "Distracție"])

        if st.button("Salvează"):
            cursor.execute("INSERT INTO raport (user, valoare, categorie) VALUES (?, ?, ?)", (user, val, cat))
            conn.commit()
            st.success("Date salvate!")

        # Vizualizare
        st.subheader("Istoric cheltuieli")
        df = pd.read_sql_query(f"SELECT * FROM raport WHERE user='{user}'", conn)
        st.dataframe(df)

        # Grafic
        if not df.empty:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            df.groupby('categorie')['valoare'].sum().plot(kind='bar', ax=ax)
            st.pyplot(fig)

        # Export
        st.download_button("Exportă CSV", df.to_csv(index=False), file_name="raport.csv")

    else:
        st.error("Utilizator sau parolă greșită")
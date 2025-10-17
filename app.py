import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- Koneksi ke database SQLite ---
conn = sqlite3.connect('stationery.db')
c = conn.cursor()

# Buat tabel kalau belum ada
c.execute('''CREATE TABLE IF NOT EXISTS requests
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              nama TEXT,
              departemen TEXT,
              tanggal TEXT,
              item TEXT,
              jumlah INTEGER,
              keterangan TEXT)''')
conn.commit()

# --- Bagian Input Form ---
st.title("🖊️ Centralized Stationery Request System")
st.write("Silakan isi form berikut untuk permintaan ATK.")

with st.form("form_request"):
    nama = st.text_input("Nama")
    departemen = st.selectbox("Departemen", [
        "Produksi", "Quality Assurance", "Quality Control",
        "Engineering", "HRGA", "Finance", "R&D", "Supply Chain"
    ])
    tanggal = datetime.now().strftime("%Y-%m-%d")
    item = st.text_input("Nama Barang")
    jumlah = st.number_input("Jumlah", min_value=1, step=1)
    keterangan = st.text_area("Keterangan tambahan", "")
    submit = st.form_submit_button("Kirim Permintaan")

if submit:
    c.execute("INSERT INTO requests (nama, departemen, tanggal, item, jumlah, keterangan) VALUES (?,?,?,?,?,?)",
              (nama, departemen, tanggal, item, jumlah, keterangan))
    conn.commit()
    st.success(f"Permintaan {item} ({jumlah}) oleh {nama} berhasil disimpan!")

# --- Tampilkan Data ---
st.subheader("📦 Data Permintaan Terkini")
df = pd.read_sql_query("SELECT * FROM requests ORDER BY id DESC", conn)
st.dataframe(df)

# --- Dashboard Sederhana ---
st.subheader("📊 Ringkasan Permintaan per Departemen")
if not df.empty:
    summary = df.groupby("departemen")["jumlah"].sum().reset_index()
    st.bar_chart(summary, x="departemen", y="jumlah")
else:
    st.info("Belum ada data permintaan.")

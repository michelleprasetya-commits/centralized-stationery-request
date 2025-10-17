# app.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO

# --- SETUP DATABASE ---
conn = sqlite3.connect("stationery.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    departemen TEXT,
    item TEXT,
    jumlah INTEGER,
    tanggal TEXT,
    keterangan TEXT
)
""")
conn.commit()

c.execute("""
CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    departemen TEXT,
    item TEXT,
    jumlah INTEGER,
    tanggal TEXT,
    keterangan TEXT
)
""")
conn.commit()

# --- LOAD ITEM MASTER ---
@st.cache_data
def load_items():
    df = pd.read_csv("items_master.csv")
    df["item_display"] = df["part_number"] + " - " + df["item_name"]
    return df

items = load_items()

# --- FUNGSI TAMBAH DATA ---
def add_request(nama, departemen, item, jumlah, keterangan):
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO requests (nama, departemen, item, jumlah, tanggal, keterangan) VALUES (?,?,?,?,?,?)",
              (nama, departemen, item, jumlah, tanggal, keterangan))
    conn.commit()

def add_usage(nama, departemen, item, jumlah, keterangan):
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO usage (nama, departemen, item, jumlah, tanggal, keterangan) VALUES (?,?,?,?,?,?)",
              (nama, departemen, item, jumlah, tanggal, keterangan))
    conn.commit()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stationery Request System", layout="wide")
st.title("📦 Centralized Stationery Request & Usage System")

menu = st.sidebar.radio("Pilih Menu:", ["📝 Form Permintaan", "🧰 Form Pemakaian", "📊 Dashboard", "🧾 Data Rekap"])

# ---------------- FORM PERMINTAAN ----------------
if menu == "📝 Form Permintaan":
    st.subheader("📝 Form Permintaan Barang Stationery")
    with st.form("form_request"):
        nama = st.text_input("Nama Pemohon")
        departemen = st.selectbox("Departemen", ["HRGA", "Production", "QC", "QA", "Engineering", "Finance", "Warehouse", "PPIC"])
        item_pilih = st.selectbox("Pilih Barang", items["item_display"])
        jumlah = st.number_input("Jumlah Diminta", min_value=1, step=1)
        keterangan = st.text_area("Keterangan Tambahan (opsional)")
        submit = st.form_submit_button("Kirim Permintaan")
        if submit:
            add_request(nama, departemen, item_pilih, jumlah, keterangan)
            st.success("✅ Permintaan berhasil dikirim!")

# ---------------- FORM PEMAKAIAN ----------------
elif menu == "🧰 Form Pemakaian":
    st.subheader("🧰 Form Pemakaian / Pengambilan Barang")
    with st.form("form_usage"):
        nama = st.text_input("Nama Pengambil")
        departemen = st.selectbox("Departemen", ["HRGA", "Production", "QC", "QA", "Engineering", "Finance", "Warehouse", "PPIC"])
        item_pilih = st.selectbox("Pilih Barang", items["item_display"])
        jumlah = st.number_input("Jumlah Dipakai", min_value=1, step=1)
        keterangan = st.text_area("Keterangan (opsional)")
        submit = st.form_submit_button("Simpan Pemakaian")
        if submit:
            add_usage(nama, departemen, item_pilih, jumlah, keterangan)
            st.success("✅ Data pemakaian berhasil disimpan!")

# ---------------- DASHBOARD ----------------
elif menu == "📊 Dashboard":
    st.subheader("📊 Dashboard Pemakaian & Permintaan")

    df_req = pd.read_sql("SELECT * FROM requests", conn)
    df_use = pd.read_sql("SELECT * FROM usage", conn)

    if df_req.empty and df_use.empty:
        st.info("Belum ada data.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.write("### Total Permintaan per Departemen")
            if not df_req.empty:
                chart_req = df_req.groupby("departemen")["jumlah"].sum()
                st.bar_chart(chart_req)
            else:
                st.write("Belum ada data permintaan.")

        with col2:
            st.write("### Total Pemakaian per Departemen")
            if not df_use.empty:
                chart_use = df_use.groupby("departemen")["jumlah"].sum()
                st.bar_chart(chart_use)
            else:
                st.write("Belum ada data pemakaian.")

        st.markdown("### 🔝 Top 10 Barang Paling Sering Diminta")
        if not df_req.empty:
            top_items = df_req.groupby("item")["jumlah"].sum().sort_values(ascending=False).head(10)
            st.dataframe(top_items)

# ---------------- REKAP DATA ----------------
elif menu == "🧾 Data Rekap":
    st.subheader("🧾 Data Permintaan & Pemakaian Lengkap")
    df_req = pd.read_sql("SELECT * FROM requests", conn)
    df_use = pd.read_sql("SELECT * FROM usage", conn)

    tab1, tab2 = st.tabs(["📋 Permintaan", "🧰 Pemakaian"])
    with tab1:
        st.dataframe(df_req)
    with tab2:
        st.dataframe(df_use)

    # tombol download
    if st.button("⬇️ Download Rekap Excel"):
        with BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_req.to_excel(writer, sheet_name="Requests", index=False)
                df_use.to_excel(writer, sheet_name="Usage", index=False)
            st.download_button("Download File Excel", buffer.getvalue(), file_name="rekap_stationery.xlsx")

conn.close()

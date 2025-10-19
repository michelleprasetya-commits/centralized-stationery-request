import streamlit as st
import pandas as pd

st.set_page_config(page_title="Centralized Stationery Request System", layout="wide")

# --- Load item master ---
@st.cache_data
def load_master():
    df = pd.read_csv("BPA_Ekstraksi_Part_Number_FINAL.csv")
    df.columns = df.columns.str.strip()  # bersihkan spasi header
    return df

master = load_master()

st.title("📦 Centralized Stationery Request System")
st.write("Silakan isi form berikut untuk pengajuan kebutuhan stationery.")

# --- Form Input ---
with st.form("request_form"):
    col1, col2 = st.columns(2)

    with col1:
        dept = st.selectbox("Departemen", ["QA", "Production", "HRGA", "Finance", "PPIC", "R&D", "Engineering", "Warehouse"])
        requester = st.text_input("Nama PIC")

    with col2:
        date_req = st.date_input("Tanggal Permintaan")
        remarks = st.text_area("Keterangan Tambahan (opsional)")

    st.subheader("🛒 Daftar Barang")
    selected_item = st.selectbox("Cari Nama Barang", master["Description"].sort_values().unique())

    # Ambil detail otomatis
    item_info = master.loc[master["Description"] == selected_item].iloc[0]
    uom = item_info.get("UOM", "")
    price = item_info.get("Unit Price", "")

    qty = st.number_input("Jumlah", min_value=1, step=1)

    # Tampilkan auto-fill info
    st.write(f"**Part Number:** {item_info['Part Number']}")
    st.write(f"**UOM:** {uom}")
    st.write(f"**Unit Price (IDR):** {price:,}")

    submit = st.form_submit_button("💾 Simpan Request")

if submit:
    # Simpan ke CSV rekap
    new_row = {
        "Tanggal": date_req,
        "Departemen": dept,
        "PIC": requester,
        "Part Number": item_info["Part Number"],
        "Deskripsi Barang": selected_item,
        "UOM": uom,
        "Harga Satuan": price,
        "Jumlah": qty,
        "Total Harga": price * qty if isinstance(price, (int, float)) else "",
        "Keterangan": remarks
    }

    try:
        rekap = pd.read_csv("rekap_request.csv")
    except FileNotFoundError:
        rekap = pd.DataFrame(columns=new_row.keys())

    rekap = pd.concat([rekap, pd.DataFrame([new_row])], ignore_index=True)
    rekap.to_csv("rekap_request.csv", index=False)

    st.success("✅ Data berhasil disimpan ke rekap_request.csv")

    st.dataframe(rekap.tail(10), use_container_width=True)

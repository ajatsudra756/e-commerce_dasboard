import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# CONFIG HALAMAN
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# LOAD DATASET
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_dataset.csv") 
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['total_revenue'] = df['price'] + df['freight_value']
    return df

try:
    df = load_data()

    # SIDEBAR
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>⚙️ Kontrol Panel</h2>", unsafe_allow_html=True)
        min_date, max_date = df["order_purchase_timestamp"].min(), df["order_purchase_timestamp"].max()
        start_date, end_date = st.date_input("Filter Rentang Waktu", [min_date, max_date], min_date, max_date)

    # Filtering Data
    main_df = df[(df["order_purchase_timestamp"] >= str(start_date)) & 
                 (df["order_purchase_timestamp"] <= str(end_date))]

    # HEADER
    st.markdown("<h1 style='text-align: left;'>📊 E-Commerce Performance Dashboard 2018</h1>", unsafe_allow_html=True)
    st.markdown("---")

   # ROW 1: KPI METRICS
    # Membuat 4 kolom untuk menambahkan metrik baru
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = main_df.order_id.nunique()
        st.metric("Total Unit Terjual", f"{total_orders:,} Unit")
        
    with col2:
        total_rev = main_df.total_revenue.sum()
        st.metric("Total Pendapatan", f"BRL {total_rev:,.0f}")
        
    with col3:
        # Rata-rata Nilai Transaksi (AOV)
        avg_rev = total_rev / total_orders if total_orders > 0 else 0
        st.metric("Rata-rata nilai transaksi", f"BRL {avg_rev:,.2f}")
        
    with col4:
        # Rata-rata Produk per Order
        # Menghitung total baris (item) dibagi total order unik
        avg_items = len(main_df) / total_orders if total_orders > 0 else 0
        st.metric("Rata-rata Penjualan Produk", f"{avg_items:.2f} Item")

    # --- ROW 2: TREN PENDAPATAN & PENJUALAN ---
    # Judul Bagian Rata Kiri
    st.markdown("<h3 style='text-align: left;'>📈 Analisis Tren Bulanan</h3>", unsafe_allow_html=True)
    
    monthly_df = main_df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "total_revenue": "sum"
    }).reset_index()
    monthly_df['month'] = monthly_df['order_purchase_timestamp'].dt.strftime('%B')
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 16))
    plt.subplots_adjust(hspace=0.8)
    
    # 1. Grafik Total Pendapatan
    ax1.plot(monthly_df['month'], monthly_df['total_revenue'], marker='o', color="#1f77b4", linewidth=4, markersize=12, markerfacecolor="white", markeredgewidth=3)
    ax1.set_title("Total Pendapatan Per Bulan", loc="center", fontsize=20, fontweight='bold', pad=40)
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    ax1.set_xlim(-0.7, len(monthly_df)-0.3)
    ax1.set_ylim(0, monthly_df['total_revenue'].max() * 1.3) 
    
    for i, val in enumerate(monthly_df['total_revenue']):
        is_dropping = i < len(monthly_df)-1 and monthly_df['total_revenue'][i+1] < val
        y_pos = -35 if is_dropping else 25
        v_align = 'top' if is_dropping else 'bottom'
        
        ax1.annotate(f"BRL {val:,.0f}", (monthly_df['month'][i], val), 
                     textcoords="offset points", xytext=(0, y_pos), 
                     ha='center', va=v_align, fontweight='bold', color="#1f77b4", fontsize=11)

    # 2. Grafik Kuantitas Terjual
    ax2.plot(monthly_df['month'], monthly_df['order_id'], marker='s', color="#d62728", linewidth=4, markersize=12, markerfacecolor="white", markeredgewidth=3)
    ax2.set_title("Kuantitas Terjual per Bulan", loc="center", fontsize=20, fontweight='bold', pad=40)

    ax2.set_xlim(-0.7, len(monthly_df)-0.3)
    ax2.set_ylim(0, monthly_df['order_id'].max() * 1.3)

    for i, val in enumerate(monthly_df['order_id']):
        is_dropping = i < len(monthly_df)-1 and monthly_df['order_id'][i+1] < val
        y_pos = -35 if is_dropping else 25
        v_align = 'top' if is_dropping else 'bottom'

        ax2.annotate(f"{val:,} Unit", (monthly_df['month'][i], val), 
                     textcoords="offset points", xytext=(0, y_pos), 
                     ha='center', va=v_align, fontweight='bold', color="#d62728", fontsize=11)
    
    st.pyplot(fig)

    # ROW 3: KATEGORI 5 PRODUK TERLARIS & TIDAK LARIS
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Analisis Kategori Produk</h3>", unsafe_allow_html=True)
    prod_col1, prod_col2 = st.columns(2)

    with prod_col1:
        st.markdown("<p style='text-align: center;'><b>5 Kategori Produk Terlaris</b></p>", unsafe_allow_html=True)
        top_5 = main_df.groupby("product_category").order_id.nunique().sort_values(ascending=False).head(5)
        colors_top = ["#1f77b4"] + ["#D3D3D3"] * 4
        fig_top, ax_top = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_5.values, y=top_5.index, palette=colors_top, ax=ax_top)
        for i, v in enumerate(top_5.values):
            ax_top.text(v + (max(top_5.values)*0.02), i, f"{v:,} Unit", va='center', fontweight='bold', fontsize=11)
        ax_top.set_xlim(0, max(top_5.values) * 1.25)
        ax_top.spines['top'].set_visible(False)
        ax_top.spines['right'].set_visible(False)
        st.pyplot(fig_top)

    with prod_col2:
        st.markdown("<p style='text-align: center;'><b>5 Kategori Produk Paling Tidak Laris</b></p>", unsafe_allow_html=True)
        bottom_5 = main_df.groupby("product_category").order_id.nunique().sort_values(ascending=True).head(5)
        colors_bot = ["#d62728"] + ["#D3D3D3"] * 4
        fig_bot, ax_bot = plt.subplots(figsize=(10, 6))
        sns.barplot(x=bottom_5.values, y=bottom_5.index, palette=colors_bot, ax=ax_bot)
        for i, v in enumerate(bottom_5.values):
            ax_bot.text(v + (max(bottom_5.values)*0.05), i, f"{v:,} Unit", va='center', fontweight='bold', fontsize=11)
        ax_bot.set_xlim(0, max(bottom_5.values) * 1.5)
        ax_bot.spines['top'].set_visible(False)
        ax_bot.spines['right'].set_visible(False)
        st.pyplot(fig_bot)

    # ROW 4: SEGMENTASI PELANGGAN
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>👥 Segmentasi Pelanggan (RFM)</h3>", unsafe_allow_html=True)
    
    segments = ['Loyal Customers', 'At Risk', 'Top Customers', 'Lost Customers']
    counts = [39.4, 34.4, 17.4, 8.8] 
    colors_rfm = ["#4A90E2", "#F5A623", "#7ED321", "#D0021B"]
    custom_labels = [f"{seg}\n({val}%)" for seg, val in zip(segments, counts)]
    
    fig_rfm, ax_rfm = plt.subplots(figsize=(8, 8))
    ax_rfm.pie(counts, labels=custom_labels, colors=colors_rfm, startangle=140, 
               textprops={'fontsize': 13, 'fontweight': 'bold'}, labeldistance=1.1,
               wedgeprops={'width': 0.35, 'edgecolor': 'w', 'linewidth': 5})
    st.pyplot(fig_rfm)

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")

st.markdown("<p style='text-align: center; color: grey;'>Dashboard by Sudrajat | Proyek Analisis Data 2026</p>", unsafe_allow_html=True)

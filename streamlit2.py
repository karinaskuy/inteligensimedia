import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Interactive Media Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fungsi Pembantu ---

@st.cache_data
def clean_data(df_raw):
    """
    Membersihkan data:
    - Mengubah 'Date' ke format datetime.
    - Mengisi 'Engagements' yang kosong dengan 0.
    """
    df = df_raw.copy() # Bekerja dengan salinan untuk menghindari SettingWithCopyWarning

    if 'Date' in df.columns:
        # Mengonversi 'Date' ke datetime, memaksa error menjadi NaT
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Menghapus baris di mana konversi Date gagal
        df.dropna(subset=['Date'], inplace=True)
    else:
        st.error("Kolom 'Date' tidak ditemukan dalam file CSV Anda. Mohon periksa format CSV.")
        return pd.DataFrame() # Mengembalikan DataFrame kosong jika kolom penting tidak ada

    if 'Engagements' in df.columns:
        # Mengonversi 'Engagements' ke numerik, mengisi NaN dengan 0, lalu ke integer
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0).astype(int)
    else:
        st.error("Kolom 'Engagements' tidak ditemukan dalam file CSV Anda. Mengisi dengan 0.")
        df['Engagements'] = 0 # Tambahkan kolom Engagements jika tidak ada dan isi dengan 0

    # Pastikan kolom-kolom lain yang diharapkan ada
    required_cols = ['Platform', 'Sentiment', 'MediaType', 'Location']
    for col in required_cols:
        if col not in df.columns:
            st.warning(f"Kolom '{col}' tidak ditemukan. Beberapa visualisasi mungkin tidak berfungsi dengan benar.")
            # st.write(f"Menambahkan kolom '{col}' dengan nilai default kosong.")
            df[col] = "Tidak Diketahui" # Memberikan nilai default agar tidak error

    return df

# Fungsi untuk membuat dan menampilkan grafik Plotly
def create_chart(chart_type, df_chart, x=None, y=None, names=None, title="", color=None, sort_values=False, top_n=None):
    """
    Membuat grafik Plotly berdasarkan tipe yang diminta.
    """
    fig = None
    try:
        if chart_type == "pie":
            fig = px.pie(df_chart, names=names, title=title, hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel) # Menggunakan Pastel dari Plotly
        elif chart_type == "line":
            if sort_values:
                df_chart = df_chart.sort_values(by=x)
            fig = px.line(df_chart, x=x, y=y, title=title, markers=True,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        elif chart_type == "bar":
            if top_n:
                # Pastikan ada cukup data untuk top_n
                if not df_chart.empty and y in df_chart.columns:
                    df_chart = df_chart.nlargest(top_n, y, keep='first') # Ambil N teratas
                else:
                    st.warning(f"Tidak dapat membuat grafik '{title}': Data kosong atau kolom '{y}' tidak ada.")
                    return # Keluar dari fungsi jika data tidak valid
            fig = px.bar(df_chart, x=x, y=y, title=title,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        
        if fig:
            fig.update_layout(
                margin=dict(t=50, b=0, l=0, r=0),
                title_x=0.5,
                font=dict(family="Inter", size=12, color="#333"),
                hoverlabel=dict(font_size=12, font_family="Inter"),
                paper_bgcolor="#F0F8FF", # Alice Blue
                plot_bgcolor="rgba(0,0,0,0)", # Transparan
                height=350 # Tinggi default untuk konsistensi
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membuat grafik '{title}': {e}")
        st.write("Mohon periksa apakah kolom yang dibutuhkan untuk grafik ini ada dan memiliki data yang valid.")


# --- Judul Dashboard ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    body {
        font-family: 'Inter', sans-serif;
        background-color: #F0F8FF; /* Alice Blue - very light pastel blue */
        color: #333;
    }
    .header-gradient {
        background: linear-gradient(to right, #B3E0FF, #8CD6FF);
        padding: 1rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 2rem;
    }
    .header-gradient h1 {
        color: #FFFFFF;
        font-size: 2.5rem;
        font-weight: bold;
        font-family: 'Inter', sans-serif;
    }
    .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"], .stDateInput div[data-baseweb="baseinput"] {
        border-radius: 0.5rem;
        border-color: #BFDBFE;
    }
    .stButton > button {
        background-color: #4A90E2; /* Blue-500 */
        color: white;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background-color: #357ABD; /* Darker Blue-600 */
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    .chart-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        height: 100%;
        margin-bottom: 1.5rem; /* Consistent spacing */
    }
    .insights-box {
        background-color: #E0F2F7; /* Light blue pastel */
        padding: 1rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        color: #2A5280; /* Darker blue for text */
        margin-top: 1rem;
    }
    .insights-box ul {
        list-style-type: disc;
        margin-left: 1.25rem;
    }
    .insights-box li {
        margin-bottom: 0.25rem;
    }
    </style>
    <div class="header-gradient">
        <h1>Interactive Media Intelligence Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("---")

# --- Masukan Data ---
st.sidebar.header("Masukan Data")
uploaded_file = st.sidebar.file_uploader("Unggah File CSV", type=["csv"])

df = pd.DataFrame() # Inisialisasi DataFrame kosong

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("File CSV berhasil diunggah!")
        
        # 2. Pembersihan Data
        cleaned_df = clean_data(df.copy()) # Gunakan copy agar tidak mengubah DataFrame asli
        
        if cleaned_df.empty:
            st.error("Data tidak dapat diproses. Mohon periksa file CSV dan pastikan memiliki kolom 'Date'.")
        else:
            st.sidebar.success("Data berhasil dibersihkan!")
            st.sidebar.dataframe(cleaned_df.head(), use_container_width=True) # Tampilkan beberapa baris data yang telah dibersihkan
            
            # Kumpulkan nilai unik untuk filter secara dinamis
            all_platforms = ['Semua Platform']
            if 'Platform' in cleaned_df.columns:
                all_platforms.extend(sorted(cleaned_df['Platform'].unique().tolist()))
            
            all_media_types = ['Semua Tipe Media']
            if 'MediaType' in cleaned_df.columns:
                all_media_types.extend(sorted(cleaned_df['MediaType'].unique().tolist()))

            all_locations = ['Semua Lokasi']
            if 'Location' in cleaned_df.columns:
                all_locations.extend(sorted(cleaned_df['Location'].unique().tolist()))

            # --- Filter Data ---
            st.sidebar.write("---")
            st.sidebar.header("Filter Data")

            selected_platform = st.sidebar.selectbox("Platform", all_platforms)
            selected_sentiment = st.sidebar.selectbox("Sentimen", ["Semua Sentimen", "Positive", "Neutral", "Negative"])
            selected_media_type = st.sidebar.selectbox("Tipe Media", all_media_types)
            selected_location = st.sidebar.selectbox("Lokasi", all_locations)

            # Inisialisasi tanggal default
            min_date_val = cleaned_df['Date'].min().date() if not cleaned_df.empty and 'Date' in cleaned_df.columns else None
            max_date_val = cleaned_df['Date'].max().date() if not cleaned_df.empty and 'Date' in cleaned_df.columns else None

            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input("Rentang Tanggal (Mulai)", 
                                            value=min_date_val,
                                            min_value=min_date_val,
                                            max_value=max_date_val
                                            )
            with col2:
                end_date = st.date_input("Rentang Tanggal (Selesai)", 
                                          value=max_date_val,
                                          min_value=min_date_val,
                                          max_value=max_date_val
                                          )
            
            # Terapkan Filter
            filtered_df = cleaned_df.copy()

            if selected_platform != "Semua Platform":
                if 'Platform' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Platform'] == selected_platform]
            if selected_sentiment != "Semua Sentimen":
                if 'Sentiment' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Sentiment'] == selected_sentiment]
            if selected_media_type != "Semua Tipe Media":
                if 'MediaType' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['MediaType'] == selected_media_type]
            if selected_location != "Semua Lokasi":
                if 'Location' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Location'] == selected_location]
            
            # Filter tanggal
            if start_date and 'Date' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Date'].dt.date >= start_date]
            if end_date and 'Date' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Date'].dt.date <= end_date]

            # --- Visualisasi Data & Insights ---
            st.write("---")
            st.header("Visualisasi Data & Insights")

            if filtered_df.empty:
                st.warning("Tidak ada data yang tersedia setelah menerapkan filter. Coba sesuaikan filter atau unggah file CSV yang berbeda.")
                st.dataframe(cleaned_df.head(), use_container_width=True) # Tampilkan data awal jika filter terlalu ketat
            else:
                # Baris 1: Sentiment Breakdown & Platform Engagements
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                    st.subheader("Sentiment Breakdown")
                    if 'Sentiment' in filtered_df.columns:
                        sentiment_counts = filtered_df['Sentiment'].value_counts().reset_index()
                        sentiment_counts.columns = ['Sentiment', 'Count']
                        if not sentiment_counts.empty:
                            create_chart("pie", sentiment_counts, names='Sentiment', title="Distribusi Sentimen")
                        else:
                            st.info("Tidak ada data sentimen setelah filter.")
                    else:
                        st.info("Kolom 'Sentiment' tidak tersedia.")
                    st.markdown(
                        """
                        <div class="insights-box">
                            <p class="font-bold">Insight:</p>
                            <ul>
                                <li>Mayoritas sentimen positif menunjukkan citra merek yang kuat.</li>
                                <li>Persentase sentimen netral yang signifikan mengindikasikan peluang untuk mengubah audiens yang ragu-ragu.</li>
                                <li>Perhatikan sentimen negatif; peningkatan tiba-tiba bisa menjadi sinyal masalah.</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                    st.subheader("Platform Engagements")
                    if 'Platform' in filtered_df.columns and 'Engagements' in filtered_df.columns:
                        platform_engagements = filtered_df.groupby('Platform')['Engagements'].sum().reset_index()
                        if not platform_engagements.empty:
                            create_chart("bar", platform_engagements, x='Platform', y='Engagements', title="Total Engagement per Platform")
                        else:
                            st.info("Tidak ada data platform engagement setelah filter.")
                    else:
                        st.info("Kolom 'Platform' atau 'Engagements' tidak tersedia.")
                    st.markdown(
                        """
                        <div class="insights-box">
                            <p class="font-bold">Insight:</p>
                            <ul>
                                <li>Platform dengan engagement tertinggi adalah saluran utama interaksi audiens Anda.</li>
                                <li>Platform dengan engagement rendah mungkin memerlukan evaluasi ulang strategi konten atau penargetan audiens.</li>
                                <li>Konten tertentu mungkin berkinerja lebih baik di platform spesifik, sesuaikan strategi Anda.</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                # Baris 2: Engagement Trend over Time
                st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                st.subheader("Engagement Trend over Time")
                if 'Date' in filtered_df.columns and 'Engagements' in filtered_df.columns:
                    engagement_trend = filtered_df.groupby(pd.Grouper(key='Date', freq='D'))['Engagements'].sum().reset_index()
                    engagement_trend.columns = ['Date', 'Total Engagements']
                    if not engagement_trend.empty:
                        create_chart("line", engagement_trend, x='Date', y='Total Engagements', title="Tren Engagement dari Waktu ke Waktu", sort_values=True)
                    else:
                        st.info("Tidak ada data tren engagement setelah filter.")
                else:
                    st.info("Kolom 'Date' atau 'Engagements' tidak tersedia.")
                st.markdown(
                    """
                    <div class="insights-box">
                        <p class="font-bold">Insight:</p>
                        <ul>
                            <li>Lonjakan engagement setelah peluncuran kampanye menandakan keberhasilan.</li>
                            <li>Engagement cenderung memuncak dalam 24-48 jam pertama setelah publikasi konten.</li>
                            <li>Identifikasi tren musiman untuk merencanakan konten yang relevan.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)


                # Baris 3: Media Type Mix & Top 5 Locations
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                    st.subheader("Media Type Mix")
                    if 'MediaType' in filtered_df.columns:
                        media_type_counts = filtered_df['MediaType'].value_counts().reset_index()
                        media_type_counts.columns = ['MediaType', 'Count']
                        if not media_type_counts.empty:
                            create_chart("pie", media_type_counts, names='MediaType', title="Proporsi Tipe Media")
                        else:
                            st.info("Tidak ada data tipe media setelah filter.")
                    else:
                        st.info("Kolom 'MediaType' tidak tersedia.")
                    st.markdown(
                        """
                        <div class="insights-box">
                            <p class="font-bold">Insight:</p>
                            <ul>
                                <li>Tipe media dominan mencerminkan preferensi audiens Anda.</li>
                                <li>Jika artikel memiliki engagement tinggi tetapi proporsinya rendah, pertimbangkan untuk membuat lebih banyak.</li>
                                <li>Diversifikasi tipe media dapat membantu menjangkau audiens yang lebih luas.</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                with col4:
                    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                    st.subheader("Top 5 Locations by Engagement")
                    if 'Location' in filtered_df.columns and 'Engagements' in filtered_df.columns:
                        location_engagements = filtered_df.groupby('Location')['Engagements'].sum().reset_index()
                        if not location_engagements.empty:
                            create_chart("bar", location_engagements, x='Location', y='Engagements', title="Top 5 Lokasi berdasarkan Engagement", top_n=5)
                        else:
                            st.info("Tidak ada data lokasi setelah filter.")
                    else:
                        st.info("Kolom 'Location' atau 'Engagements' tidak tersedia.")
                    st.markdown(
                        """
                        <div class="insights-box">
                            <p class="font-bold">Insight:</p>
                            <ul>
                                <li>Lokasi teratas adalah area dengan minat tinggi terhadap merek/topik Anda.</li>
                                <li>Data ini mendukung kampanye pemasaran atau konten yang dilokalisasi.</li>
                                <li>Area di luar 5 besar dengan engagement yang muncul bisa menjadi target ekspansi.</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file CSV: {e}")
        st.info("Mohon pastikan file CSV Anda memiliki format yang benar dan kolom-kolom yang diharapkan: `Date`, `Platform`, `Sentiment`, `MediaType`, `Location`, `Engagements`.")

else:
    st.info("Silakan unggah file CSV Anda di sidebar untuk melihat visualisasi data.")
    st.write("Pastikan file CSV memiliki kolom: `Date`, `Platform`, `Sentiment`, `MediaType`, `Location`, `Engagements`.")

st.markdown("---")

# --- Fitur Ekspor Dashboard ---
st.header("Fitur Ekspor Dashboard")
st.write("""
Streamlit tidak memiliki fitur ekspor PDF bawaan secara langsung dari aplikasi.
Namun, Anda dapat menggunakan fungsi cetak browser (`Ctrl + P` atau `Cmd + P`)
dan menyimpannya sebagai PDF untuk mendapatkan salinan dashboard Anda.
""")

st.write("---")

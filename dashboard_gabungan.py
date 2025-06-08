import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Dashboard Gabungan", layout="wide")

menu = st.sidebar.radio("📌 Pilih Dashboard:", [
    "📊 Prodi & Dosen",
    "📘 Aktivitas Dosen per Semester",
    "🎓 Riwayat Pendidikan"
])

# ===========================
# 📊 Dashboard Prodi & Dosen
# ===========================
if menu == "📊 Prodi & Dosen":
    st.title("📊 Dashboard Data Prodi dan Dosen Perguruan Tinggi")
    uploaded_file = st.file_uploader("📥 Upload file Excel (DosenUG_prodi_homebase_dan_nm_kel_bidang.xlsx)", type=["xlsx"], key="prodi_dosen")

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df['usia'] = pd.to_numeric(df['usia'], errors='coerce')
        df['Tahun_Pensiun'] = pd.to_numeric(df['Tahun_Pensiun'], errors='coerce')

        with st.sidebar:
            st.header("🔎 Filter Data")
            selected_prov = st.selectbox("Provinsi PT", options=["Semua"] + sorted(df['provinsi_pt'].dropna().unique().tolist()))
            selected_jenjang = st.multiselect("Jenjang Prodi", options=sorted(df['jenjang_prodi'].dropna().unique().tolist()), default=None)

        if selected_prov != "Semua":
            df = df[df['provinsi_pt'] == selected_prov]
        if selected_jenjang:
            df = df[df['jenjang_prodi'].isin(selected_jenjang)]

        col1, col2 = st.columns(2)

        jenjang_df = df['jenjang_prodi'].value_counts().reset_index()
        jenjang_df.columns = ['Jenjang', 'Jumlah']
        fig1 = px.bar(jenjang_df, x='Jenjang', y='Jumlah', title='Distribusi Jenjang Pendidikan')
        col1.plotly_chart(fig1, use_container_width=True)

        fig3 = px.pie(df, names='jk', title='Komposisi Jenis Kelamin Dosen')
        col2.plotly_chart(fig3, use_container_width=True)

        col3, col4 = st.columns(2)
        top_pt = df['nama_pt'].value_counts().head(10).reset_index()
        top_pt.columns = ['Perguruan Tinggi', 'Jumlah']
        fig2 = px.bar(top_pt, x='Jumlah', y='Perguruan Tinggi', orientation='h', title='Top 10 PT dengan Jumlah Dosen Terbanyak')
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
        col3.plotly_chart(fig2, use_container_width=True)

        jabfung_df = df['jabatan_akademik'].value_counts().reset_index()
        jabfung_df.columns = ['Jabatan Akademik', 'Jumlah']
        fig4 = px.bar(jabfung_df, x='Jabatan Akademik', y='Jumlah', title='Distribusi Jabatan Akademik')
        col4.plotly_chart(fig4, use_container_width=True)

        fig5 = px.histogram(df, x='usia', nbins=30, title='Distribusi Usia Dosen')
        st.plotly_chart(fig5, use_container_width=True)

        pensiun = df['Tahun_Pensiun'].dropna().astype(int).value_counts().sort_index().reset_index()
        pensiun.columns = ['Tahun Pensiun', 'Jumlah']
        fig6 = px.line(pensiun, x='Tahun Pensiun', y='Jumlah', markers=True, title='Proyeksi Jumlah Dosen Pensiun')
        st.plotly_chart(fig6, use_container_width=True)

        with st.expander("📄 Lihat Data Mentah"):
            st.dataframe(df)
    else:
        st.info("Silakan upload file Excel terlebih dahulu.")

# =========================================
# 📘 Dashboard Aktivitas Dosen per Semester
# =========================================
elif menu == "📘 Aktivitas Dosen per Semester":
    st.title("📘 Dashboard Aktivitas Dosen per Semester")
    uploaded_file = st.file_uploader("📥 Upload file Excel (DataAjarUG2023-2024_prodi_dan_mk.xlsx)", type=["xlsx"], key="aktivitas_dosen")

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df['SKSDOS'] = df['SKSDOS'].astype(str).str.replace(',', '.').astype(float)
        df['SKSMK'] = df['SKSMK'].astype(str).str.replace(',', '.').astype(float)
        df['REN-TM'] = pd.to_numeric(df['REN-TM'], errors='coerce')
        df['REN-REAL'] = pd.to_numeric(df['REN-REAL'], errors='coerce')

        semester_list = sorted(df['SEMESTER'].dropna().unique())
        selected_semester = st.selectbox("📅 Pilih Semester", semester_list)
        df_filtered = df[df['SEMESTER'] == selected_semester]

        col1, col2 = st.columns(2)
        pend_df = df_filtered['PENDTERAKHIR'].value_counts().reset_index()
        pend_df.columns = ['Pendidikan Terakhir', 'Jumlah']
        fig1 = px.bar(pend_df, x='Pendidikan Terakhir', y='Jumlah', title='Pendidikan Terakhir Dosen')
        col1.plotly_chart(fig1, use_container_width=True)

        fig2 = px.histogram(df_filtered, x='SKSDOS', nbins=20, title='Histogram SKS Dosen')
        col1.plotly_chart(fig2, use_container_width=True)

        top_mk = df_filtered['NMMK'].value_counts().head(10).reset_index()
        top_mk.columns = ['Nama Mata Kuliah', 'Jumlah']
        fig3 = px.bar(top_mk, x='Jumlah', y='Nama Mata Kuliah', orientation='h', title='Top 10 Mata Kuliah')
        col2.plotly_chart(fig3, use_container_width=True)

        fig4 = px.scatter(df_filtered, x='REN-TM', y='REN-REAL', trendline="ols", title='Rencana vs Realisasi TM')
        col2.plotly_chart(fig4, use_container_width=True)

        prodi_dosen = df_filtered.groupby('NMPS')['NMDSN'].nunique().reset_index()
        prodi_dosen.columns = ['Program Studi', 'Jumlah Dosen']
        fig5 = px.bar(prodi_dosen.sort_values('Jumlah Dosen', ascending=False),
                      x='Jumlah Dosen', y='Program Studi', orientation='h',
                      title='Jumlah Dosen Mengajar per Prodi')
        st.plotly_chart(fig5, use_container_width=True)

        with st.expander("📤 Ekspor Data"):
            col3, col4 = st.columns(2)
            with col3:
                output = io.BytesIO()
                df_filtered.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                st.download_button("💾 Unduh Data", data=output, file_name=f"aktivitas_dosen_{selected_semester}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            with col4:
                st.download_button("🖼️ Unduh Grafik (PNG)", data=fig5.to_image(format="png"), file_name=f"grafik_dosen_prodi_{selected_semester}.png", mime="image/png")
    else:
        st.info("Silakan upload file Excel terlebih dahulu.")

# ===========================================
# 🎓 Dashboard Riwayat Pendidikan Dosen
# ===========================================
elif menu == "🎓 Riwayat Pendidikan":
    st.title("🎓 Dashboard Riwayat Pendidikan Dosen")
    uploaded_file = st.file_uploader("📥 Upload file Excel (RwytPendidikanDosen_riwayat_pendidikan_PRODIPEND.xlsx)", type=["xlsx"], key="riwayat_pendidikan")

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df['THNLULUS'] = pd.to_numeric(df['THNLULUS'], errors='coerce')

        jenjang_df = df['JEN'].value_counts().reset_index()
        jenjang_df.columns = ['Jenjang', 'Jumlah']
        fig1 = px.bar(jenjang_df, x='Jenjang', y='Jumlah', title='Distribusi Jenjang Pendidikan')
        st.plotly_chart(fig1, use_container_width=True)

        prodi_df = df['PRODIPEND'].value_counts().head(10).reset_index()
        prodi_df.columns = ['Program Studi', 'Jumlah']
        fig2 = px.bar(prodi_df, x='Jumlah', y='Program Studi', orientation='h', title='Top 10 Program Studi')
        st.plotly_chart(fig2, use_container_width=True)

        tahun_df = df['THNLULUS'].dropna().astype(int).value_counts().sort_index().reset_index()
        tahun_df.columns = ['Tahun Lulus', 'Jumlah']
        fig3 = px.line(tahun_df, x='Tahun Lulus', y='Jumlah', markers=True, title='Distribusi Tahun Lulus Dosen')
        st.plotly_chart(fig3, use_container_width=True)

        pt_df = df['PTPEND'].value_counts().head(10).reset_index()
        pt_df.columns = ['PT Asal', 'Jumlah']
        fig4 = px.bar(pt_df, x='PT Asal', y='Jumlah', title='10 PT Asal Pendidikan Terbanyak')
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)

        with st.expander("📄 Lihat Data Mentah"):
            st.dataframe(df)
    else:
        st.info("Silakan upload file Excel terlebih dahulu.")

import streamlit as st
import pandas as pd
import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import locale
import plotly.express as px
from streamlit_calendar import calendar
from streamlit_extras.metric_cards import style_metric_cards
import re

# import streamlit as st
# from streamlit_theme import st_theme
# theme = st_theme()
# st.write(theme)

# Siapkan kredensial dari secrets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive', 
         'https://www.googleapis.com/auth/drive.file', 
         'https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)
client = gspread.authorize(creds)


@st.cache_data(ttl=66)
# Fungsi untuk membuka lembar kerja
def open_sheet(sheet_id, sheet_name):
    # Buka lembar kerja
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    # Dapatkan header dari baris pertama
    headers = pd.Series(sheet.get_values('1:1')[0]).unique()
    # Hapus header kosong
    i = np.where(headers == '')
    headers = np.delete(headers, i)

    # Muat semua catatan ke dalam DataFrame
    data = sheet.get_all_records(expected_headers=headers)
    df = pd.DataFrame(data)

    return df[headers]

def clean_and_prefix(df):
    df.columns = df.columns.str.strip()
    if "NIP" in df.columns:
        df["NIP"] = df["NIP"].astype(str).str.strip()
        # Validasi NIP: hanya digit
        df = df[df["NIP"].str.fullmatch(r"\d+")]
    else:
        # Kolom NIP wajib ada
        raise ValueError(f"Sheet tidak punya kolom 'NIP'")
    # Prefix kolom agar tidak bentrok saat merge
    return df

def load_all_data(emp_id):
    # Muat dan bersihkan semua sheet
    personal_info = clean_and_prefix(open_sheet(emp_id, "personal_information"))
    employment_info = clean_and_prefix(open_sheet(emp_id, "employment_information"))
    employmentcontract_info = clean_and_prefix(open_sheet(emp_id, "employee_contract"))
    leaves_info = clean_and_prefix(open_sheet(emp_id, "employee_leave"))
    warning_info = clean_and_prefix(open_sheet(emp_id, "employee_warning"))
    funfact_info = clean_and_prefix(open_sheet(emp_id, "employee_funfacts"))
    data_db = clean_and_prefix(open_sheet(emp_id, "data_dashboard"))

    # Merge semua berdasarkan NIP yang sudah dibersihkan
    base = personal_info.merge(employment_info, on="NIP", how="inner")  # ← hanya NIP yang ada di keduanya
    full = base \
        .merge(employmentcontract_info, on="NIP", how="left") \
        .merge(leaves_info, on="NIP", how="left") \
        .merge(warning_info, on="NIP", how="left") \
        .merge(funfact_info, on="NIP", how="left") \
        .merge(data_db, on="NIP", how="left")
    
    # Rapikan name → hilangkan spasi ekstra & kapitalisasi awal kata
    if 'name' in full.columns:
        full['name'] = (
            full['name']
            .astype(str)
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.title()
        )

    return full

emp_id = "11KEd9_kPIaffyh6EVe9H1Qo4uKzuYC-9klgL5HFNdIs"
data_gabung = load_all_data(emp_id)
# st.write(f"Jumlah data awal: {len(data_gabung)}")
# if not data_gabung.empty:
#     st.write("Daftar Nama Kolom:", data_gabung.columns.tolist())
#     st.write("Contoh 5 data teratas:", data_gabung.head())

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()    
    personal_info = clean_and_prefix(open_sheet(emp_id, "personal_information"))
    employment_info = clean_and_prefix(open_sheet(emp_id, "employment_information"))
    employmentcontract_info = clean_and_prefix(open_sheet(emp_id, "employee_contract"))
    leaves_info = clean_and_prefix(open_sheet(emp_id, "employee_leave"))
    warning_info = clean_and_prefix(open_sheet(emp_id, "employee_warning"))
    funfact_info = clean_and_prefix(open_sheet(emp_id, "employee_funfacts"))
    data_db = clean_and_prefix(open_sheet(emp_id, "data_dashboard"))


def detail_employee():
    st.title("👤 Detail Employee")
    st.sidebar.markdown("### Sections")
    st.sidebar.markdown("""
    - [Status](#status)
    - [General Info](#general_info)
    - [Employment Info](#emp_info)
    - [Contact](#contact)
    - [Emergency](#emergency)
    - [Certification](#certif)
    - [Education](#education)
    - [Cuti](#cuti)
    - [Contract](#kontrak)
    - [Detail SP](#peringatan)
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Hanya ubah link di sidebar */
    section[data-testid="stSidebar"] a {
        color: #5ACECB !important;   
        text-decoration: none;       
    }
    section[data-testid="stSidebar"] a:hover {
        color: #547A8A !important;  
    }
    </style>
    """, unsafe_allow_html=True)


    # st.dataframe(data_gabung)

    col1, col2 = st.columns(2)

    selected_dept = col1.selectbox(
        "Pilih Departemen",
        options=["All Dept"] + sorted(data_gabung["department"].dropna().unique().tolist())
    )
    if selected_dept != "All Dept":
        filtered_bydept = data_gabung[data_gabung['department']== selected_dept]
    else:
        filtered_bydept = data_gabung.copy()
    
    available_names = filtered_bydept['name'].dropna().unique().tolist()
    selected_name = col2.selectbox(
     "Pilih Nama employee",
     options=sorted(available_names)       
    )

    filtered_data_byname = data_gabung[data_gabung["name"]==selected_name].copy()
    employee_nip = filtered_data_byname['NIP'].unique().tolist()


    if not filtered_data_byname.empty:
        result_data = filtered_data_byname.iloc[-1]

        result_data = result_data.apply(
        lambda x: None if (pd.isna(x) or str(x).strip() == "") else str(x).strip()
        )

        # === STATUS ===
        # Hitung lama kerja
        join_date_parsed_earliest = pd.to_datetime(result_data.get("date_of_joining", ""), errors="coerce")

        today = pd.Timestamp.today().normalize()

        if pd.notnull(join_date_parsed_earliest):
            delta = today - join_date_parsed_earliest
            total_days = delta.days
            years = total_days // 365
            remaining_days_after_years = total_days % 365
            months = remaining_days_after_years // 30
            days = remaining_days_after_years % 30
            lama_kerja_display = f"{years} tahun {months} bulan {days} hari"
        else:
            lama_kerja_display = "Tanggal masuk tidak tersedia"

        st.markdown(f"""
        <div id='status' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); color: #333333;'>
            <h4 style='margin-top: 0;'>STATUS</h4>
            <p><strong>Lama kerja: {lama_kerja_display}</strong> </p>
            <p><strong>Status: {result_data.get('status', 'Tidak ada info')}</strong> </p>
        </div>
        """, unsafe_allow_html=True)

        # === PERSONAL INFO ===

        st.markdown(f"""
        <div id='general_info' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>GENERAL PERSONAL INFORMATION</h4>
            <p><strong>Nama:</strong> {result_data.get('name', 'Tidak ada info')}</p>
            <p><strong>Tanggal Lahir:</strong> {result_data.get('dob', 'Tidak ada info')}</p>
            <p><strong>Jenis Kelamin:</strong> {result_data.get('gender', 'Tidak ada info')}</p>
        </div>        
        """, unsafe_allow_html=True)

        # === employee INFO ===
        st.markdown(f"""
         <div id='emp_info' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>EMPLOYMENT INFORMATION</h4>
            <p><strong>NIP:</strong> {result_data.get('NIP', 'Tidak ada info')}</p>
            <p><strong>Department:</strong> {result_data.get('department', 'Tidak ada info')}</p>
            <p><strong>Tipe:</strong> {result_data.get('type_x', 'Tidak ada info')}</p>
            <p><strong>Status:</strong> {result_data.get('status', 'Tidak ada info')}</p>
            <p><strong>Tanggal Masuk:</strong> {result_data.get('date_of_joining', 'Tidak ada info')}</p>
        </div>         

        """, unsafe_allow_html=True)

        # === CONTACT ===

        st.markdown(f"""
        <div id='contact' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>CONTACT</h4>
            <p><strong>No. Telepon:</strong> {result_data.get('phone_number', 'Tidak ada info')}</p>
            <p><strong>Email:</strong> {result_data.get('email', 'Tidak ada info')}</p>
            <p><strong>Alamat Lengkap:</strong> {result_data.get('address', 'Tidak ada info')}</p>
            <p><strong>Kota:</strong> {result_data.get('city', 'Tidak ada info')}</p>
        </div>
        """, unsafe_allow_html=True)

        # === EMERGENCY ===
        st.markdown(f"""
        <div id='emergency' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>EMERGENCY CONTACT</h4>
            <p><strong>Emergency Phone:</strong> {result_data.get('emergency_phone_number', 'Tidak ada info')}</p>
            <p><strong>Relationship:</strong> {result_data.get('emergency_relationship', 'Tidak ada info')}</p>           
        </div>
        """, unsafe_allow_html=True)


        st.markdown(f"""
        <div id='certif' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>CERTIFICATION</h4>
            <p><strong>Sertifikasi:</strong> {result_data.get('prof_cert', 'Tidak ada info')}</p>
            <p><strong>Skor:</strong> {result_data.get('prof_score', 'Tidak ada info')}</p>            
        </div>
        """, unsafe_allow_html=True)
    else : 
        st.markdown(f"""
        <div style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); color: #333333;'>
            <h4 style='margin-top: 0;'>STATUS</h4>
            <p> Tidak ada data untuk employee ini </strong>.<p>

        </div>
        """, unsafe_allow_html=True)

        # === PERSONAL INFO ===

        st.markdown(f"""
        <div id='general_info' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>GENERAL PERSONAL INFORMATION</h4>
            <p> Tidak ada data untuk employee ini </strong>.<p>
        </div>        
        """, unsafe_allow_html=True)

        # === CONTACT ===

        st.markdown(f"""
        <div id='contact' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>CONTACT</h4>
            <p> Tidak ada data untuk employee ini </strong>.<p>
        </div>
        """, unsafe_allow_html=True)

        # === EMERGENCY ===
        st.markdown(f"""
        <div id='emergency' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>EMERGENCY CONTACT</h4>
            <p>Tidak ada data untuk employee ini.</p>         
        </div>
        """, unsafe_allow_html=True)

        # === SERTIFIKAT ===
        st.markdown(f"""
        <div id='certif' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>CERTIFICATION</h4>
            <p>Tidak ada data untuk employee ini.</p>         
        </div>
        """, unsafe_allow_html=True)

    # ==== EDUCATION ====
    edu_level = result_data.get('education_level')
    university = result_data.get('university')
    major = result_data.get('major')

    if not any([edu_level, university, major]):
        st.markdown(f"""
        <div id='edu' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>EDUCATION</h4>
            <p>Tidak ada data education untuk employee ini.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div id='edu' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>EDUCATION</h4>
            <p><strong>Pendidikan:</strong> {edu_level or 'Tidak ada info'}</p>
            <p><strong>Universitas:</strong> {university or 'Tidak ada info'}</p>
            <p><strong>Jurusan:</strong> {major or 'Tidak ada info'}</p>
        </div>
        """, unsafe_allow_html=True)     


    # ==== CUTI ====
    nip_employee = result_data.get("NIP")

    df_cuti = data_gabung[data_gabung["NIP"] == nip_employee][[
         "start_date_x", "end_date_x", "type_y"
    ]].copy()

    # Cek apakah semua kolom yang dibutuhkan kosong/null
    if df_cuti[["start_date_x", "end_date_x", "type_y"]].isnull().all().all():
        st.markdown(f"""
        <div id='cuti' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>INFO CUTI</h4>
            <p> Tidak ada data cuti untuk employee ini </strong>.<p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_cuti["start_date_x"] = pd.to_datetime(df_cuti["start_date_x"], errors="coerce")
        df_cuti["end_date_x"] = pd.to_datetime(df_cuti["end_date_x"], errors="coerce")
        df_cuti['Tanggal Mulai'] = df_cuti['start_date_x'].dt.strftime('%d %B %Y')
        df_cuti['Tanggal Berakhir'] = df_cuti['end_date_x'].dt.strftime('%d %B %Y')
        df_cuti['Keterangan'] = df_cuti['type_y']
        df_cuti["Durasi Cuti"] = (df_cuti["end_date_x"] - df_cuti["start_date_x"]).dt.days.astype(str) + ' hari'

        df_cuti_display = df_cuti[['Tanggal Mulai', 'Tanggal Berakhir', 'Durasi Cuti','Keterangan']]


        st.markdown(f"""
        <div id='cuti' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>INFO CUTI</h4>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(df_cuti_display)

    # === DETAIL KONTRAK ===
    kontrak_data = data_gabung[data_gabung["NIP"] == nip_employee][[
        "name_x", "date_created", "link"
    ]].copy()

    if kontrak_data[["name_x", "date_created", "link"]].isnull().all().all():
        st.markdown(f"""
        <div id='kontrak' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>DETAIL KONTRAK</h4>
            <p> Tidak ada detail kontrak untuk employee ini </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Drop baris duplikat agar tidak tampil dobel
        kontrak_data = kontrak_data.dropna(subset=["name_x", "date_created", "link"], how="all")
        kontrak_data = kontrak_data.drop_duplicates(subset=["name_x", "date_created", "link"])

        kontrak_data_renamed = kontrak_data.rename(columns={
            "name_x": "Nama Dokumen",
            "date_created": "Tanggal Dibuat",
            "link": "Link"
        })
        
        # st.dataframe(kontrak_data_renamed)

        # Ubah kolom link jadi tombol HTML
        kontrak_data_renamed["Link"] = kontrak_data_renamed["Link"].apply(
            lambda url: f'<a href="{url}" target="_blank" '
                        f'style="color: white; background-color: #4CAF50; '
                        f'padding: 6px 76px; text-decoration: none; border-radius: 5px; display: inline-block;">Buka</a>'
            if pd.notnull(url) and str(url).strip() != "" else ""
        )

        # Render tabel HTML tanpa escape tag
        url_html = kontrak_data_renamed.to_html(escape=False, index=False)

        st.markdown(f"""
        <div id='kontrak' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>DETAIL KONTRAK</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(url_html, unsafe_allow_html=True)



    peringatan_data = data_gabung[data_gabung["NIP"] == nip_employee][[
        "no_surat_peringatan", "start_date_y", "end_date_y"
        ]].copy()

    if peringatan_data[["no_surat_peringatan", "start_date_y", "end_date_y"]].isnull().all().all():
        st.markdown(f"""
        <div id='peringatan' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>SURAT PERINGATAN</h4>
            <p> Tidak ada surat peringatan untuk employee ini </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        peringatan_data = peringatan_data.dropna(
            subset=["no_surat_peringatan", "start_date_y", "end_date_y"], how="all"
        ).drop_duplicates(subset=["no_surat_peringatan", "start_date_y", "end_date_y"])

        peringatan_data_renamed = peringatan_data.rename(columns={
            "no_surat_peringatan": "Nomor Surat",
            "start_date_y": "Tanggal Mulai",
            "end_date_y": "Tanggal Berakhir"
        })

        total_sp = len(peringatan_data_renamed)

        st.markdown(f"""
        <div id='peringatan' style='background-color: #f9f4ef; padding: 20px; border-radius: 12px;
                        margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); color: #333333;'>
            <h4 style='margin-top: 0;'>SURAT PERINGATAN</h4>
            <p><strong>Total SP:{total_sp}</strong> </p> 
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(peringatan_data_renamed)

        #st.dataframe(data_gabung)

def grand_dashboard():

    data_gabung =  load_all_data(emp_id)
    data_gabung =  data_gabung.drop_duplicates(subset=["NIP"])


    st.title("📊 Employee Dashboard")
    st.markdown("<style>body{background-color:#f9f4ef;}</style>", unsafe_allow_html=True)
    # st.dataframe(data_gabung)

    required_columns = ['department', 'type_x', 'name', 'phone_number', 'email', 'status', 'education_level', 
                        'gender', 'city', 'date_of_joining', 'departement_db', 
                        'name_db', 'dob_db', 'year_dob', 'gen', 'edu_db', 
                        'bach_db', 'uni_db', 'stat_uni_db', 'exc_db', 
                        'prof_db', 'prof_score_db']
    for col in required_columns:
        if col not in data_gabung.columns:
            data_gabung[col] = None

    # Bersihkan data: ubah string kosong jadi NaN, drop NA
    data_gabung[required_columns] = data_gabung[required_columns].replace('', pd.NA)
    data_gabung = data_gabung.dropna(subset=required_columns, how='all')

    data_gabung = (
        data_gabung
        .sort_values(by=['name', 'date_of_joining'], ascending=[True, True])
        .drop_duplicates(subset=['name'], keep='first')
        .reset_index(drop=True)
    )
   

    # Sidebar Filter
    st.sidebar.header("Filters")
    filter_fields = {
        "department": ("Department", data_gabung['department'].dropna().unique()),
        "type_x": ("Tipe employee", data_gabung['type_x'].dropna().unique()),
        "status": ("Status", data_gabung['status'].dropna().unique()),
        "education_level": ("Education Level", data_gabung['education_level'].dropna().unique()),
        "gender": ("Gender", data_gabung['gender'].dropna().unique()),
        "city": ("City", data_gabung['city'].dropna().unique())
    }

    for col_name, (label, options) in filter_fields.items():
        selected = st.sidebar.multiselect(label=label, options=options)
        if selected:
            data_gabung = data_gabung[data_gabung[col_name].isin(selected)]

    # --- METRICS ---
    col1, col2 = st.columns(2)
    jumlah_total = len(data_gabung)
    jumlah_aktif = data_gabung[data_gabung['status'].str.upper() == 'A'].shape[0]

    # Rata-rata masa kerja
    data_gabung['date_of_joining'] = pd.to_datetime(data_gabung['date_of_joining'], errors='coerce')
    masa_kerja_hari = (pd.Timestamp.today() - data_gabung['date_of_joining']).dt.days
    avg_masa_kerja = round(masa_kerja_hari.mean(), 1) if not masa_kerja_hari.isna().all() else 0

    col1.metric("Jumlah Total Karyawan", jumlah_total)
    col2.metric("Jumlah Aktif", jumlah_aktif)
    # col3.metric("Rata-rata Masa Kerja (hari)", avg_masa_kerja)

    # --- PIE CHARTS ---
    col_gender, col_divisi = st.columns(2)
    with col_gender:
        if data_gabung['gender'].notna().any():
            gender_counts = data_gabung['gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Jumlah']
            fig_gender = px.pie(gender_counts, names='Gender', values='Jumlah', 
                                title='Distribusi Gender', hole=0.3)
            st.plotly_chart(fig_gender, use_container_width=True)

    with col_divisi:
        if data_gabung['department'].notna().any():
            divisi_counts = data_gabung['department'].value_counts().reset_index()
            divisi_counts.columns = ['Department', 'Jumlah']
            fig_div = px.pie(divisi_counts, names='Department', values='Jumlah',
                             title='Distribusi Department', hole=0.3)
            st.plotly_chart(fig_div, use_container_width=True)
    col_gen, col_uni = st.columns(2)
    with col_gen:
        if data_gabung['gen'].notna().any():
            gen_counts = data_gabung['gen'].value_counts().reset_index()
            gen_counts.columns = ['Generasi', 'Jumlah']
            fig_gen = px.pie(
                gen_counts, names='Generasi', values='Jumlah', 
                title="Generasi (Gen Z / Milenial)", hole=0.3
            )
            st.plotly_chart(fig_gen, use_container_width=True)

    with col_uni:
        if data_gabung['stat_uni_db'].notna().any():
            stat_counts = data_gabung['stat_uni_db'] \
                .map({'L': 'Luar Negeri', 'D': 'Dalam Negeri'}) \
                .value_counts().reset_index()
            stat_counts.columns = ['Status Universitas', 'Jumlah']
            fig_stat = px.pie(
                stat_counts, names='Status Universitas', values='Jumlah', 
                title="Status Universitas", hole=0.3
            )
            st.plotly_chart(fig_stat, use_container_width=True)

    col_bach, col_type = st.columns(2)
    with col_bach:
        if data_gabung['edu_db'].notna().any():
            bach_counts = data_gabung['edu_db'].value_counts().reset_index()
            bach_counts.columns = ['Jenjang Pendidikan', 'Jumlah']
            fig_bach = px.pie(
                bach_counts, names='Jenjang Pendidikan', values='Jumlah', 
                title="Jenjang Pendidikan", hole=0.3
            )
            st.plotly_chart(fig_bach, use_container_width=True)

    with col_type:
        if data_gabung['type_x'].notna().any():
            type_counts = data_gabung['type_x'].value_counts().reset_index()
            type_counts.columns = ['Tipe employee', 'Jumlah']
            fig_type = px.pie(
                type_counts, names='Tipe employee', values='Jumlah', 
                title="Tipe employee", hole=0.3
            )
            st.plotly_chart(fig_type, use_container_width=True)


    # --- BAR CHART City ---
    if data_gabung['city'].notna().any():
        city_counts = data_gabung['city'].value_counts().reset_index()
        city_counts.columns = ['City', 'Jumlah']
        fig_city = px.bar(city_counts.head(10), x='City', y='Jumlah', 
                          title='Top 10 Domisili', color='City')
        st.plotly_chart(fig_city, use_container_width=True)

    # # --- LINE CHART Join Date ---
    # if data_gabung['date_of_joining'].notna().any():
    #     monthly_join = data_gabung.groupby(
    #         data_gabung['date_of_joining'].dt.to_period('M')
    #     ).size().reset_index(name='Jumlah')
    #     monthly_join['date_of_joining'] = monthly_join['date_of_joining'].dt.to_timestamp()
    #     fig_join = px.line(monthly_join, x='date_of_joining', y='Jumlah', 
    #                        title='Rekap Karyawan Masuk per Bulan')
    #     st.plotly_chart(fig_join, use_container_width=True)
    
    show_col = ['department', 'status_editable','name', 'phone_number', 'NIP','email',
                  'city', 'address']    
    st.subheader('Detail employee')

    df_show = data_gabung[show_col].rename(columns={
    'department': 'Department',
    'status_editable': 'Status',
    'name': 'employee Name',
    'phone_number': 'Nomor Telepon',
    'NIP': 'NIP',
    'email': 'Email',
    'city': 'Kota Domisili',
    'address': 'Alamat'
    })[['Department', 'Status', 'employee Name', 'Nomor Telepon', 'NIP', 'Email', 'Kota Domisili', 'Alamat']]

    st.dataframe(df_show)   
    # st.dataframe(data_gabung[show_col])
    # st.dataframe(data_gabung)


def birthday_calendar():
    st.title("🎂 Birthday Calendar")

    # Filter hanya karyawan aktif
    df_ultah = data_gabung.copy()

    # Ambil data unik per NIP
    df_ultah = df_ultah.drop_duplicates(subset=["NIP"])

    # Pastikan kolom DOB valid datetime
    df_ultah['dob'] = pd.to_datetime(df_ultah['dob'], errors='coerce')
    df_ultah['bulan_ultah'] = df_ultah['dob'].dt.month
    df_ultah['tanggal_ultah'] = df_ultah['dob'].dt.day

    # === SIDEBAR FILTER ===
    st.sidebar.header("🎯 Filter")
    all_departments = sorted(df_ultah['department'].dropna().unique())
    selected_dept = st.sidebar.multiselect("Pilih Department", all_departments)

    # Filter berdasarkan department (kalau ada yang dipilih)
    if selected_dept:
        df_filtered = df_ultah[df_ultah['department'].isin(selected_dept)]
    else:
        df_filtered = df_ultah.copy()

    today = datetime.today()

    # Filter ultah hari ini (berdasarkan hasil filter department)
    ultah_hari_ini = df_filtered[
        (df_filtered['dob'].dt.month == today.month) &
        (df_filtered['dob'].dt.day == today.day)
    ]

    st.subheader("🔮 Siapa yaa yang Ultah Hari Ini ...")
    if not ultah_hari_ini.empty:
        st.success("🎉 Hari ini ada yang ulang tahun, cek detailnya di bawah! 🎂")

        for _, row in ultah_hari_ini.iterrows():
            with st.expander(f"🎂 {row['name']}"):
                st.write(f"**Tanggal Masuk:** {row['date_of_joining']}")
                st.write(f"**Department:** {row['department']}")
                st.write(f"**Hobby:** {row['hobby']}")
                st.write(f"**Favorite Food:** {row['fav_food']}")
                st.write(f"**Favorite Movie:** {row['fav_movie']}")
                st.write(f"**Favorite Color:** {row['fav_color']}")
                st.write(f"**Favorite Training:** {row['fav_training']}")
                st.write(f"**Favorite Activity:** {row['fav_activity']}")
                st.write(f"**Weekend Activity:** {row['weekend_activity']}")
                st.write(f"**Wish in 1 Year:** {row['wish_year_1']}")
                st.write(f"**Wish in 3 Years:** {row['wish_year_3']}")
                st.write(f"**Wish in 5 Years:** {row['wish_year_5']}")
    else:
        st.info("😅 Hari ini belum ada yang ultah nih")

    # === Helper aman ganti tahun kabisat ===
    def safe_replace_year(dt, year):
        if pd.isnull(dt):
            return None
        try:
            return dt.replace(year=year)
        except ValueError:
            return dt.replace(year=year, day=28)

    # === Generate event calendar ===
    events = []
    for _, row in df_filtered.iterrows():
        if pd.notnull(row['dob']):
            ulang_tahun_tahun_ini = safe_replace_year(row['dob'], today.year)
            if ulang_tahun_tahun_ini:
                events.append({
                    "title": f"Ultah {row['name']} ({row['department']})",
                    "start": ulang_tahun_tahun_ini.strftime("%Y-%m-%d"),
                    "end": ulang_tahun_tahun_ini.strftime("%Y-%m-%d"),
                    "allDay": True,
                    "color": "#DD1F8799"
                })

    # === Opsi Calendar ===
    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listWeek"
        }
    }

    # === CSS Custom ===
    custom_css = """
    .fc .fc-button-primary {
        background-color: #DD1F8799 !important; 
        border-color: #0000 !important;
        color: black !important;
        margin-right: 0.5em !important;
    }
    .fc .fc-button-primary:not(.fc-button-active):hover {
        background-color: #FF7F50 !important; 
        border-color: #FF7F50 !important;
    }
    .fc .fc-button-primary.fc-button-active {
        background-color: #CD5C5C !important; 
        border-color: #CD5C5C !important;
    }
    .fc-icon {
        color: white !important;
    }
    .fc .fc-button {
        border-radius: 10px !important;
    }
    .fc .fc-header-toolbar {
        background-color: transparent; 
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px; 
    }
    """

    # === Render Calendar ===
    calendar(events=events, options=calendar_options, custom_css=custom_css, key="birthday_calendar")
    # calendar(events=events, options=calendar_options, key="birthday_calendar")
    st.caption("nb : hanya employee aktif yang ada di calendar")
    # st.dataframe(df_ultah)


# Navigasi
pages = [st.Page(detail_employee, title="🔍 Detail Employee"),
         st.Page(grand_dashboard, title="📊 Grand Dashboard"),
         st.Page(birthday_calendar, title= "🎂 Birthday Calendar")
]
pg = st.navigation(pages)
pg.run()
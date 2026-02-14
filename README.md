{
  "project_name": "Employee Management Dashboard",
  "version": "1.0.0",
  "description": "Dashboard interaktif berbasis Streamlit untuk mengelola dan memvisualisasikan data karyawan secara real-time melalui integrasi Google Sheets.",
  "features": [
    {
      "name": "Profil Karyawan",
      "description": "Informasi mendalam untuk setiap individu karyawan.",
      "points": [
        "Penghitungan otomatis masa kerja (Tahun, Bulan, Hari).",
        "Informasi personal, kontak darurat, dan sertifikasi profesi.",
        "Tracking riwayat cuti, detail kontrak kerja, dan riwayat administrasi (Surat Peringatan).",
        "Navigasi cepat menggunakan sidebar anchor links untuk akses informasi spesifik."
      ]
    },
    {
      "name": "Dashboard Utama",
      "description": "Analisis data agregat seluruh karyawan.",
      "points": [
        "Metrik utama: Total karyawan, jumlah karyawan aktif, dan rata-rata masa kerja.",
        "Visualisasi distribusi Gender, Departemen, Generasi, dan Jenjang Pendidikan via Pie Charts.",
        "Analisis sebaran domisili karyawan melalui Bar Chart.",
        "Filter dinamis untuk departemen, tipe pekerjaan, dan status keaktifan."
      ]
    },
    {
      "name": "Kalender Ulang Tahun",
      "description": "Fitur engagement dan internal culture.",
      "points": [
        "Notifikasi otomatis untuk karyawan yang berulang tahun pada hari ini.",
        "Menampilkan profil personal (Hobi, Preferensi, dan Harapan Tahunan).",
        "Kalender interaktif bulanan untuk memantau hari spesial seluruh karyawan aktif."
      ]
    }
  ],
  "technology_stack": [
    "Python",
    "Streamlit",
    "Pandas",
    "Plotly Express",
    "Streamlit-Calendar",
    "Gspread",
    "OAuth2"
  ],
  "installation_steps": [
    "Clone repository: git clone https://github.com/username/employee-management-dashboard.git",
    "Install dependencies: pip install streamlit pandas plotly gspread oauth2client streamlit-calendar",
    "Setup credentials.json (Google Service Account) di root folder.",
    "Jalankan aplikasi: streamlit run app.py"
  ],
  "data_management": {
    "method": "Caching",
    "mechanism": "st.cache_data",
    "ttl_seconds": 600,
    "refresh_manual": "Tersedia tombol 'Refresh Data' di sidebar untuk sinkronisasi data terbaru secara instan."
  },
  "ui_customization": {
    "theme_color": "#f9f4ef",
    "style": "Layout berbasis kartu (Card-based) dengan integrasi HTML/CSS kustom untuk estetika dan fungsionalitas tabel."
  }
}

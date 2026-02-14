# 👥 Employee Management Dashboard
**_Comprehensive HR Analytics & Employee Information System — Built with Streamlit and Google Sheets_**

![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Google Sheets](https://img.shields.io/badge/Database-Google%20Sheets-green?logo=googlesheets)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🌟 Overview
**Employee Management Dashboard** adalah aplikasi internal perusahaan yang dirancang untuk mengelola dan memantau data karyawan secara terpusat. Dengan mengintegrasikan **Google Sheets API** dan **Streamlit**, aplikasi ini menyajikan data mentah menjadi wawasan visual yang memudahkan tim manajemen dan HR dalam memantau profil karyawan, kontrak, hingga budaya perusahaan (engagement).

---

## 🧩 Fitur Utama

- 🔍 **Detail Informasi Karyawan**
  Memberikan profil mendalam per individu termasuk penghitungan otomatis masa kerja, informasi personal, riwayat pendidikan, sertifikasi, hingga detail kontrak kerja dan riwayat administrasi (SP).

- 📊 **Grand Dashboard (HR Analytics)**
  Visualisasi data agregat melalui grafik interaktif untuk memantau distribusi gender, departemen, generasi (Gen Z/Milenial), serta statistik domisili karyawan secara real-time.

- 🎂 **Kalender Ulang Tahun & Fun Facts**
  Fitur interaktif untuk meningkatkan engagement dengan menampilkan karyawan yang berulang tahun hari ini, lengkap dengan hobi dan harapan mereka di masa depan.

- 🔄 **Sinkronisasi Data Real-Time**
  Dilengkapi dengan fitur pembersihan cache instan untuk memastikan data yang ditampilkan selalu sesuai dengan perubahan terbaru di Google Sheets.

- 🌙 **Antarmuka Modern & Responsif**
  Desain berbasis kartu (card-based) yang bersih, profesional, dan nyaman diakses baik melalui desktop maupun perangkat mobile.

---

## ⚙️ Teknologi
| Komponen | Deskripsi |
|-----------|------------|
| **Framework** | [Streamlit](https://streamlit.io) |
| **Database** | [Google Sheets API (via gspread)](https://docs.gspread.org) |
| **Visualisasi** | [Plotly Express](https://plotly.com/python/plotly-express/) & [Streamlit-Calendar](https://github.com/im-puka/streamlit-calendar) |
| **Data Engine** | Pandas (Data Cleaning, Filtering, & Merging) |
| **Auth** | OAuth2 Service Account |

---

## 🚀 Cara Menjalankan di Lokal

1. **Clone repository**
   ```bash
   git clone [https://github.com/username/employee-management-dashboard.git](https://github.com/username/employee-management-dashboard.git)
   cd employee-management-dashboard

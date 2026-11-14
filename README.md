# 🚲 Bike Sharing Analytics Dashboard

Proyek akhir **Belajar Analisis Data dengan Python** menggunakan **Bike Sharing Dataset (2011–2012)**. Proyek ini mencakup seluruh alur analisis data mulai dari *Data Wrangling*, *Exploratory Data Analysis (EDA)*, *Visualization & Explanatory Analysis*, *Analisis Lanjutan (Clustering)*, hingga pengembangan *Dashboard Interaktif* berbasis Streamlit.

**Disusun oleh:** Febrian Pratama Saputra

---

## 📁 Struktur Direktori

```text
Febrian Pratama Saputra_Proyek Analisis Data/
├── dashboard/
│   ├── dashboard.py       # Kode utama aplikasi dashboard Streamlit
│   └── main_data.csv      # Dataset bersih hasil wrangling & clustering
├── data/
│   ├── day.csv            # Dataset mentah penyewaan sepeda harian
│   └── hour.csv           # Dataset mentah penyewaan sepeda per jam
├── notebook.ipynb         # Jupyter/Colab Notebook berisi proses analisis lengkap
├── README.md              # Dokumentasi proyek dan panduan menjalankan dashboard
├── requirements.txt       # Daftar pustaka Python yang digunakan
└── url.txt                # Tautan aplikasi Streamlit Cloud
```

---

## ⚙️ Setup Environment & Instalasi

### Menggunakan Terminal / Command Prompt (Virtual Environment)

1. Buka terminal dan arahkan ke direktori utama proyek (gunakan tanda kutip ganda karena nama folder mengandung spasi):
   ```bash
   cd "Febrian Pratama Saputra_Proyek Analisis Data"
   ```

2. Buat dan aktifkan *virtual environment* (opsional namun disarankan):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instal seluruh dependensi yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```

### Menggunakan Anaconda

```bash
conda create --name bike-sharing-ds python=3.10
conda activate bike-sharing-ds
pip install -r requirements.txt
```

---

## 🚀 Cara Menjalankan Dashboard di Lokal

Pastikan terminal sudah berada di direktori utama proyek (`Febrian Pratama Saputra_Proyek Analisis Data`), lalu jalankan perintah berikut:

```bash
streamlit run dashboard/dashboard.py
```

Jika menjalankan dari luar direktori proyek, apit seluruh *path* dengan tanda kutip ganda:

```bash
streamlit run "path/menuju/Febrian Pratama Saputra_Proyek Analisis Data/dashboard/dashboard.py"
```

Setelah perintah dijalankan, aplikasi akan terbuka otomatis di peramban (*browser*) pada alamat `http://localhost:8501`.

---

## 📊 Fitur Utama Dashboard

* **Filter Interaktif (Sidebar):** Penyaringan data dinamis berdasarkan rentang tanggal (`2011-01-01` s.d. `2012-12-31`), musim (*Spring, Summer, Fall, Winter*), kategori hari (*Working Day* vs *Weekend/Holiday*), serta kondisi cuaca harian.
* **Ringkasan KPI Utama:** Menampilkan total penyewaan (`cnt`), rata-rata penyewaan harian, serta jumlah dan persentase proporsi pengguna *Registered* maupun *Casual*.
* **Visualisasi Terstruktur dalam 3 Tab:**
  1. **Pola Penyewaan Per Jam:** Grafik garis komparasi pola komuter (*bimodal*) pada hari kerja dan pola rekreasi siang (*unimodal*) pada akhir pekan/hari libur.
  2. **Dampak Cuaca & Musim:** Diagram batang perbandingan rata-rata penyewaan harian serta persentase penurunan akibat perubahan cuaca dan pergantian musim.
  3. **Analisis Lanjutan (Clustering):** Hasil segmentasi periode waktu operasional (*Manual Grouping*) dan profil klaster tingkat permintaan harian beserta suhu aktual dan kelembapannya (*Binning*).
# Analisis Sentimen

Proyek analisis sentimen sederhana untuk teks dalam bahasa Indonesia menggunakan kamus sentimen kustom. Skrip ini dapat menganalisis komentar YouTube atau tweet Twitter, memberikan skor sentimen, dan menghasilkan laporan dalam format JSON, CSV, dan Excel.

## Deskripsi

Skrip ini menggunakan kamus sentimen dari file `positive.tsv` dan `negative.tsv` untuk menilai teks. Proses meliputi tokenisasi, stemming dengan Sastrawi, dan perhitungan skor sentimen. Klasifikasi sentimen berdasarkan total skor: positif (>0.1), negatif (< -0.1), atau netral (antara -0.1 dan 0.1).

### Fitur
- Mendukung sumber data: YouTube komentar dan tweet Twitter.
- Preprocessing teks: tokenisasi sederhana, stemming Indonesia.
- Analisis sentimen berdasarkan kamus kustom.
- Output terstruktur: JSON, CSV, dan Excel dengan detail token dan skor.
- Ringkasan statistik sentimen keseluruhan.

## Persyaratan
- Python 3.x
- Libraries: `pandas`, `Sastrawi`
- File data: `positive.tsv`, `negative.tsv`, `youtube_sound_horeg_comments.json`, `hasil_tweet_sound_horeg.json`

## Instalasi

1. Clone repositori:
   ```bash
   git clone https://github.com/Fardanaya/analisis-sentimen.git
   cd analisis-sentimen
   ```

2. Instal dependencies:
   ```bash
   pip install pandas Sastrawi
   ```

## Penggunaan

Jalankan skrip dengan parameter sumber data:

### Analisis YouTube:
```bash
python sentiment_analysis.py youtube
```

### Analisis Twitter:
```bash
python sentiment_analysis.py twitter
```

Skrip akan memproses data, menghasilkan output, dan mencetak ringkasan statistik ke konsol.

## Output Files

Setelah eksekusi, file berikut akan dibuat:
- `sentiment_results.json`: Detail analisis untuk setiap komentar (tokens, skor, dll.).
- `sentiment_results.csv`: Data token-level dalam format CSV.
- `sentiment_analysis_[source].xlsx`: Laporan Excel dengan semua data komentar.
- `sentiment_summary.csv`: Statistik keseluruhan (total komentar, rata-rata skor, rasio sentimen).

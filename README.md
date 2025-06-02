# Tubes3_stimaaa


## Dependency
```
pip install pdfplumber
```

## How to run
```
python src/main.py
```

untuk jalanin databasenya
- pip install faker
- pip install sqlalchemy mysql-connector-python python-dotenv
- install MySQL jika sudah ada yang ngambil port 3306 yaitu misalnya MariaDB, disaranin pake port 3308 dengan X Protocol nya 33080 dan jangan lupa tambahin di PATH, lalu create database ats_db di cmd (dengan cd C:\Program Files\MySQL80\MySQL Server 8.0\bin -> mysql -u root -p -h localhost -P 3308 -> CREATE DATABASE IF NOT EXISTS ats_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;)
- lalu install ekstensi di vs code yaitu SQL Tools by Matheus Teixeira (bentuk tabung kuning untuk connectnya isiin aja portnya 3308 kalo memang 3308 portnya) lalu install ekstensi SQLTools MySQL/MariaDB/TiDB Driver by Matheus Teixei
- di ganti password di .env
- di terminal run ini
python src/db/seeder.py
supaya kebaca semua isi file pdf dari cv yang mau dipake dengan kategori kategori masing masing
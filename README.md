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
(ga perlu buat database ats_db dulu)

Jalanin untuk liat tabel dari databasenya
- setelah download ekstensi di atas
- lalu masuk ke ekstensi SQLTools itu
- Add New Connection > MySQL > [Connection namenya bebas] > [Port sesuaikan dengan port yang dipakai di MySQL] > di Database masukkin 'ats_db'> Username : 'root' > Pilih Save as plaintext in settings di bagian Password mode > isi password sesuai dengan password di MySQL

# Tugas Besar IF2224 – Teori Bahasa Formal dan Otomata  
## **Milestone 3: Semantic Analysis (Pascal-S Compiler)**

---

## Identitas Kelompok
Kelompok FRT
| Nama                            | NIM      | Tugas                                                             |
|---------------------------------|----------|-------------------------------------------------------------------|
| Maggie Zeta Rosida S            | 13521117 | Semantic Analysis, Laporan, Testing                               |
| Buege Mahara Putra              | 13523037 | Semantic Analysis, Laporan, Testing                               |
| Hanif Kalyana Aditya            | 13523041 | Semantic Analysis, Laporan, Testing                               |
| Jethro Jens Norbert Simatupang  | 13523081 | Semantic Analysis, Laporan, Testing                               |

---

## Deskripsi Program

Pada milestone ini, program berfungsi sebagai semantic analyzer untuk bahasa Pascal-S, yang merupakan tahap ketiga dalam proses kompilasi setelah lexical analysis dan syntax analysis. Semantic analyzer bertugas memeriksa kebenaran makna program yang sudah benar secara sintaks, dengan memvalidasi konsistensi tipe data, deklarasi variabel dan fungsi, aturan lingkup (scope), serta control flow.

Semantic analyzer ini menggunakan pendekatan Attributed Grammar yang mengimplementasikan aturan semantik melalui Visitor Pattern. Setiap jenis node pada parse tree memiliki fungsi visit terpisah yang bertanggung jawab untuk membangun Abstract Syntax Tree (AST) terdekorasi, mengelola symbol table, dan melakukan type checking.

Program menghasilkan decorated AST yang telah dianotasi dengan informasi tipe data, referensi symbol table, dan informasi scope, serta melaporkan error semantik seperti penggunaan variabel belum terdekralasi, ketidaksesuaian tipe data, atau pelanggaran aturan scope.

---

## Requirements

- Python ≥ 3.10  
- `pip` (Python package manager)

---

## Cara Penggunaan Program
1. Clone repository
```bash
git clone https://github.com/JethroJNS/FRT-Tubes-IF2224.git
```
2. Masuk ke direktori repository dan jalankan compiler (Lexer + Parser + Semantic Analysis)

    Contoh command:
```bash
python -m src.compiler test/milestone-3/input-1.pas 
```
3. Output: program akan menampilkan daftar token, parse tree, decorated Abstract Syntax Tree (AST), dan symbol tables ke terminal.

---

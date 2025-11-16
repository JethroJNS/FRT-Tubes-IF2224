# Tugas Besar IF2224 – Teori Bahasa Formal dan Otomata  
## **Milestone 2: Syntax Analysis (Pascal-S Compiler)**

---

## Identitas Kelompok
Kelompok FRT
| Nama                            | NIM      | Tugas                                                             |
|---------------------------------|----------|-------------------------------------------------------------------|
| Maggie Zeta Rosida S            | 13521117 | Grammar Specification, Laporan, Testing                           |
| Buege Mahara Putra              | 13523037 | Laporan, Testing                                                  |
| Hanif Kalyana Aditya            | 13523041 | Grammar Implementation, Main Parser, Parse Tree, Laporan, Testing |
| Jethro Jens Norbert Simatupang  | 13523081 | Grammar Implementation, Main Parser, Parse Tree, Laporan, Testing |

---

## Deskripsi Program

Pada milestone ini, program berfungsi sebagai syntax analyzer (parser) untuk bahasa Pascal-S, yang merupakan tahap kedua dalam proses kompilasi setelah lexical analysis. Parser bertugas memeriksa urutan token yang dihasilkan oleh lexer agar sesuai dengan aturan tata bahasa (grammar) dari bahasa Pascal-S.

Parser ini menggunakan pendekatan Recursive Descent Parsing yang mengimplementasikan setiap non-terminal dalam grammar sebagai fungsi terpisah, dan membangun Parse Tree lengkap yang merepresentasikan struktur hierarkis program sumber.

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
2. Masuk ke direktori repository dan jalankan compiler (Lexer + Parser)

    Contoh command:
```bash
python -m src.compiler test/milestone-2/input-1.pas 
```
3. Output: program akan menampilkan daftar token diikuti dengan parse tree di terminal

---

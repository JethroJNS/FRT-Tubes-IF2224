# Tugas Besar IF2224 – Teori Bahasa Formal dan Otomata  
## **Milestone 1: Lexical Analysis (Pascal-S Compiler)**

---

## Identitas Kelompok
Kelompok FRT
| Nama | NIM | Tugas |
|------|------|--------|
| Maggie Zeta Rosida S | 13521117 | Define Token, Laporan, Testing |
| Buege Mahara Putra | 13523037 | Parser DFA, Laporan, Testing |
| Hanif Kalyana Aditya  | 13523041 | Design DFA, Laporan, Testing |
| Jethro Jens Norbert Simatupang  | 13523081 | Implement Main Lexer, Laporan, Testing |

---

## Deskripsi Program

Pada milestone ini, program berfungsi sebagai lexical analyzer untuk bahasa Pascal-S, yaitu versi sederhana dari bahasa Pascal.  
Lexer bertugas membaca source code Pascal-S dan mengubahnya menjadi daftar token sesuai aturan formal bahasa.
Lexer ini menggunakan pendekatan Deterministic Finite Automata (DFA) dan Regular Expression (Regex) yang didefinisikan dalam file `token_spec.json`.

---

## Requirements

- Python ≥ 3.10  
- `pip` (Python package manager)

---

### Cara Penggunaan Program
1. Clone Repository
https://github.com/JethroJNS/FRT-Tubes-IF2224.git
2. Jalankan Lexer
python -m src.compiler test/milestone-1/[nama file test case]
Contoh:
python -m src.compiler test/milestone-1/input-5.pas
3. Output
Program akan menampilkan daftar token di terminal

---

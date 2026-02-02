import json
import os
from datetime import datetime

DATA_FILE = "data.json"

saldo = 0
transaksi = []

def load_data():
    global saldo, transaksi
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            saldo = float(data.get("saldo", 0))
            transaksi = data.get("transaksi", []) or []
            for t in transaksi:
                t["jumlah"] = float(t.get("jumlah", 0))
        except Exception:
            saldo = 0
            transaksi = []

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"saldo": saldo, "transaksi": transaksi}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Gagal menyimpan data:", e)

def recompute_saldo():
    total = 0.0
    for t in transaksi:
        if t.get("tipe") == "pemasukan":
            total += float(t.get("jumlah", 0))
        elif t.get("tipe") == "pengeluaran":
            total -= float(t.get("jumlah", 0))
    return total


def tambah_pemasukan():
    global saldo
    try:
        jumlah = input("Masukkan jumlah pemasukan: ")
        jumlah = float(jumlah)
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return
        keterangan = input("Keterangan (opsional): ").strip()
        saldo += jumlah
        transaksi.append({"tipe": "pemasukan", "jumlah": jumlah, "waktu": datetime.now().isoformat(), "keterangan": keterangan})
        save_data()
        print(f"Berhasil menambahkan {jumlah:.2f}. Saldo sekarang: {saldo:.2f}")
    except ValueError:
        print("Input tidak valid. Masukkan angka.")

def tambah_pengeluaran():
    global saldo
    try:
        jumlah = input("Masukkan jumlah pengeluaran: ")
        jumlah = float(jumlah)
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return
        if jumlah > saldo:
            print("Saldo tidak cukup.")
            return
        keterangan = input("Keterangan (opsional): ").strip()
        saldo -= jumlah
        transaksi.append({"tipe": "pengeluaran", "jumlah": jumlah, "waktu": datetime.now().isoformat(), "keterangan": keterangan})
        save_data()
        print(f"Berhasil mengurangi {jumlah:.2f}. Saldo sekarang: {saldo:.2f}")
    except ValueError:
        print("Input tidak valid. Masukkan angka.")

def lihat_saldo():
    global saldo
    print("=== Saldo Saat Ini ===")
    print(f"Rp {saldo:,.2f}")

def show_transaksi(items):
    global saldo
    if not items:
        print("Tidak ada transaksi untuk ditampilkan.")
        return
    total_masuk = 0.0
    total_keluar = 0.0
    for orig_idx, t in items:
        waktu = t.get("waktu", "")
        tipe = t.get("tipe", "")
        jumlah = float(t.get("jumlah", 0))
        keterangan = t.get("keterangan", "")
        if tipe == "pemasukan":
            total_masuk += jumlah
        elif tipe == "pengeluaran":
            total_keluar += jumlah
        print(f"{orig_idx:>3}. {waktu} - {tipe.capitalize():<10} Rp {jumlah:,.2f} - {keterangan}")
    print("---")
    print(f"Total pemasukan : Rp {total_masuk:,.2f}")
    print(f"Total pengeluaran: Rp {total_keluar:,.2f}")
    print(f"Saldo saat ini   : Rp {saldo:,.2f}")


def laporan():
    global transaksi
    print("=== Laporan Transaksi ===")
    if not transaksi:
        print("Belum ada transaksi.")
        return
    print("Filter:\n1. Semua\n2. Hari ini\n3. Bulan ini\n4. Tahun ini\n5. Rentang tanggal")
    choice = input("Pilih filter [1-5]: ").strip()
    now = datetime.now()
    items = []
    if choice == "2":
        for idx, t in enumerate(transaksi, start=1):
            t_dt = datetime.fromisoformat(t.get("waktu"))
            if t_dt.date() == now.date():
                items.append((idx, t))
    elif choice == "3":
        for idx, t in enumerate(transaksi, start=1):
            t_dt = datetime.fromisoformat(t.get("waktu"))
            if t_dt.year == now.year and t_dt.month == now.month:
                items.append((idx, t))
    elif choice == "4":
        for idx, t in enumerate(transaksi, start=1):
            t_dt = datetime.fromisoformat(t.get("waktu"))
            if t_dt.year == now.year:
                items.append((idx, t))
    elif choice == "5":
        start = input("Tanggal mulai (YYYY-MM-DD): ").strip()
        end = input("Tanggal akhir (YYYY-MM-DD): ").strip()
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            for idx, t in enumerate(transaksi, start=1):
                t_dt = datetime.fromisoformat(t.get("waktu"))
                if start_dt.date() <= t_dt.date() <= end_dt.date():
                    items.append((idx, t))
        except Exception:
            print("Format tanggal salah.")
            return
    else:
        items = list(enumerate(transaksi, start=1))
    show_transaksi(items)


def kelola_transaksi():
    global transaksi, saldo
    if not transaksi:
        print("Belum ada transaksi.")
        return
    while True:
        print("=== Kelola Transaksi ===")
        for idx, t in enumerate(transaksi, start=1):
            waktu = t.get("waktu", "")
            tipe = t.get("tipe", "")
            jumlah = float(t.get("jumlah", 0))
            keterangan = t.get("keterangan", "")
            print(f"{idx:>3}. {waktu} - {tipe.capitalize():<10} Rp {jumlah:,.2f} - {keterangan}")
        choice = input("Pilih nomor transaksi untuk edit/hapus (atau 'b' untuk kembali): ").strip()
        if choice.lower() == 'b':
            return
        try:
            i = int(choice) - 1
            if i < 0 or i >= len(transaksi):
                print("Nomor tidak valid.")
                continue
            t = transaksi[i]
            action = input("Ketik 'e' untuk edit, 'd' untuk hapus, atau 'b' untuk batal: ").strip().lower()
            if action == 'b':
                continue
            if action == 'd':
                confirm = input("Yakin ingin menghapus transaksi ini? (y/n): ").strip().lower()
                if confirm == 'y':
                    transaksi.pop(i)
                    saldo = recompute_saldo()
                    save_data()
                    print("Transaksi dihapus.")
                continue
            elif action == 'e':
                print("Kosongkan input untuk mempertahankan nilai lama.")
                new_jumlah = input(f"Jumlah ({t.get('jumlah')}): ").strip()
                new_ket = input(f"Keterangan ({t.get('keterangan','')}): ").strip()
                if new_jumlah:
                    try:
                        val = float(new_jumlah)
                        if val <= 0:
                            print("Jumlah harus > 0. Edit dibatalkan.")
                            continue
                    except ValueError:
                        print("Input jumlah tidak valid. Edit dibatalkan.")
                        continue
                updated = t.copy()
                if new_jumlah:
                    updated['jumlah'] = float(new_jumlah)
                if new_ket:
                    updated['keterangan'] = new_ket
                temp = transaksi.copy()
                temp[i] = updated
                total = 0.0
                for tt in temp:
                    if tt.get('tipe') == 'pemasukan':
                        total += float(tt.get('jumlah', 0))
                    elif tt.get('tipe') == 'pengeluaran':
                        total -= float(tt.get('jumlah', 0))
                if total < 0:
                    print("Perubahan menyebabkan saldo negatif. Edit dibatalkan.")
                    continue
                transaksi[i] = updated
                saldo = total
                save_data()
                print("Transaksi diperbarui.")
                continue
            else:
                print("Aksi tidak dikenal.")
                continue
        except ValueError:
            print("Input tidak valid.")


def menu():
    print("=== Aplikasi Pengelola Uang Saku ===")
    print("1. Tambah pemasukan")
    print("2. Tambah pengeluaran")
    print("3. Lihat saldo")
    print("4. Laporan")
    print("5. Kelola transaksi")
    print("6. Keluar")

if __name__ == "__main__":
    load_data()

    while True:
        menu()
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_pemasukan()
        elif pilihan == "2":
            tambah_pengeluaran()
        elif pilihan == "3":
            lihat_saldo()
        elif pilihan == "4":
            laporan()
        elif pilihan == "5":
            kelola_transaksi()
        elif pilihan == "6":
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak valid")
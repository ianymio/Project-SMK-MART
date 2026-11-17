
# fitur hapus pengguna maupun barang dan dapat dipulihkan (soft delete) | 50/50 (tinggal pulihkan)
# setelah muncul nota, otomatis lanjut tambah transaksi baru (dapat dibatalkan) | x
# edit qty di keranjang belanjaan || FIX | x
# cari riwayat transaksi berdasarkan tanggal | x 

import json
import os
import getpass
from datetime import datetime

FILE_DB = "smk_mart_db.json"
FILE_LOG_TRANSAKSI = "riwayat_transaksi.txt"
FILE_LOG_REVISI = "riwayat_revisi_barang.txt"


smk_mart_db = {
    "barang": {},
    "Transaksi": {},
    "Gudang": {},
    "Pengguna": {
        "USR001": {
            "username": "admin",
            "password": "123",
            "role": "Admin"
        },
        "USR002": {
            "username": "kasir",
            "password": "123",
            "role": "Kasir"
        },
        "USR003": {
            "username": "gudang",
            "password": "123",
            "role": "Gudang"
        }
    }
}

# baca data dari JSON jika ada, jika tidak ada gunakan data default
def muat_database():
    if os.path.exists(FILE_DB):
        with open(FILE_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "barang" in data:
                for id_brg in data["barang"]:
                    if "Terhapus" not in data["barang"][id_brg]:
                        data["barang"][id_brg]["Terhapus"] = False
            return data            
    return smk_mart_db

# menyimpan data terbaru ke JSON
def simpan_database():
    with open(FILE_DB, "w", encoding="utf-8") as f:
        json.dump(smk_mart_db, f, indent=4)

# mencatat riwayat revisi barang ke txt
def catat_log_revisi(aksi, id_barang, keterangan):
    with open(FILE_LOG_REVISI, "a", encoding="utf-8") as f:
        f.write(f"({user_aktif}) | {aksi} | ID: {id_barang} | {keterangan}\n")

# mencatat riwayat transaksi ke txt
def catat_log_transaksi(id_tx):
    data = smk_mart_db["Transaksi"][id_tx]
    with open(FILE_LOG_TRANSAKSI, "a", encoding="utf-8") as f:
        f.write(f"=== NOTA {id_tx} | Tgl: {data['tanggal']} | Kasir: {data['id_kasir']} ===\n")
        for item in data["items"]:
            f.write(f"- {item['nama_barang']} x{item['jumlah_beli']} = Rp{item['subtotal']}\n")
        f.write(f"Total: Rp{data['total_harga']} ({data['metode_pembayaran']})\n\n")


smk_mart_db = muat_database()
nomor_nota = len(smk_mart_db["Transaksi"])
nomor_gudang = len(smk_mart_db["Gudang"])

user_aktif = None
role_aktif = None

def input_angka(pesan, minimum=0):
    while True:
        try:
            nilai = int(input(pesan))
            if nilai < minimum:
                print(f"❌ Angka tidak boleh kurang dari {minimum}!")
                continue
            return nilai
        except ValueError:
            print("❌ Masukkan angka yang valid!")

# SISTEM LOGIN
def login_sistem():
    global user_aktif, role_aktif
    print("\n================================================")
    print("       SELAMAT DATANG DI APLIKASI SMK MART       ")
    print("================================================")
    print("Silakan login terlebih dahulu.")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    for id_user, data in smk_mart_db["Pengguna"].items():
        if data["username"] == username and data["password"] == password:
            user_aktif = data["username"]
            role_aktif = data["role"]
            print(f"\n✅ Login Berhasil! Selamat datang, {user_aktif} ({role_aktif}).")
            return True
            
    print("❌ Username atau Password salah!")
    return False

# PENGECEKAN STOK MINIMUM
def cek_stok_minimum():
    ada_peringatan = False
    print("\n============ SISTEM MONITORING STOK ============")
    if not smk_mart_db["barang"]:
        print("💡 Sistem: Belum ada data barang terdaftar untuk dipindai.")
        print("=" * 48)
        return
    for id_barang, data in smk_mart_db["barang"].items():
        if data.get("Terhapus", False):
            continue
        if data["Stok Sekarang"] <= data["Batas Minimum"]:
            print(f"⚠️ PERINGATAN! Stok barang '{data['Nama Barang']}' (ID: {id_barang}) kritis!")
            print(f"   Stok Saat Ini: {data['Stok Sekarang']} | Batas Minimum: {data['Batas Minimum']}")
            ada_peringatan = True
    if not ada_peringatan:
        print("✅ Semua stok barang berada dalam kondisi aman.")
    print("=" * 48)

# TAMBAH DATA BARANG
def tambah_data_barang():
    print("\n=== Menambahkan Data Barang ===")
    
    # 1. Navigasi Batal di awal sebelum mengisi data yang panjang
    navigasi = input("Tekan [Enter] untuk lanjut atau ketik [B]atal: ").strip().lower()
    if navigasi == 'b':
        print("❌ Penambahan barang dibatalkan.")
        return

    nomor_barang_baru = len(smk_mart_db["barang"]) + 1
    id_barang = f"BRG{nomor_barang_baru:03d}"
    
    # Antisipasi jika ID sudah ada (misal setelah ada penghapusan data), sistem akan mencari nomor berikutnya yang kosong
    while id_barang in smk_mart_db["barang"]:
        nomor_barang_baru += 1
        id_barang = f"BRG{nomor_barang_baru:03d}"

    # 3. Pengisian data barang
    nama_barang = input("Masukkan Nama Barang: ").strip()
    if not nama_barang:
        print("❌ Nama Barang tidak boleh kosong!")
        return
        
    harga_beli = input_angka("Masukkan Harga Beli Pabrik: Rp", minimum=0)
    harga_jual = input_angka("Masukkan Harga Jual Toko: Rp", minimum=harga_beli) 
    stok_sekarang = input_angka("Masukkan Stok Sekarang: ", minimum=0)
    minimal_stok = input_angka("Masukkan Minimal Stok: ", minimum=0)
    
    konfirmasi_tambah = input(f"Apakah Anda yakin ingin menambahkan barang '{nama_barang}' dengan ID {id_barang}? (y/n): ").strip().lower()

    if konfirmasi_tambah == 'y':
        smk_mart_db["barang"][id_barang] = {
            "Nama Barang": nama_barang,
            "Harga Beli": harga_beli,
            "Harga Jual": harga_jual,
            "Stok Sekarang": stok_sekarang,
            "Batas Minimum": minimal_stok,
            "Terhapus": False
        }
        simpan_database()
        catat_log_revisi("TAMBAH", id_barang, f"{nama_barang} | Modal: Rp{harga_beli} | Jual: Rp{harga_jual} | Stok: {stok_sekarang}")
        print(f"✅ Data barang '{nama_barang}' berhasil ditambahkan dengan ID {id_barang}!")
    else:
        print("❌ Penambahan barang dibatalkan.")


# TAMPILKAN DAN MENGURUTKAN DATA BARANG
def urutkan_dan_tampilkan_barang():
    print("\n" + "=" * 40 + " DAFTAR DATA BARANG " + "=" * 40)
    print("=" * 100)
    if not smk_mart_db["barang"]:
        print("Belum ada data barang di database.")
        return
    
    list_barang = []
    for id_barang, data in smk_mart_db["barang"].items():
        item = {
            "id_barang": id_barang,
            "Nama Barang": data["Nama Barang"],
            "Harga Beli": data.get("Harga Beli", 0),
            "Harga Jual": data["Harga Jual"],
            "Stok Sekarang": data["Stok Sekarang"],
            "Batas Minimum": data["Batas Minimum"]
        }
        list_barang.append(item)

    # Bubble Sort berdasarkan Nama Barang (case-insensitive)
    n = len(list_barang)
    for i in range(n):
        for j in range(0, n - i - 1):
            if list_barang[j]["Nama Barang"].lower() > list_barang[j + 1]["Nama Barang"].lower():
                list_barang[j], list_barang[j + 1] = list_barang[j + 1], list_barang[j]
                
    print(f"{'ID Barang':<12} {'Nama Barang':<25} {'Harga Jual':<15} {'Harga Beli':<15} {'Stok Sekarang':<15} {'Batas Minimum':<15}")
    print("-" * 100)
    for data in list_barang:
        harga_beli_teks = f"Rp{data.get('Harga Beli', 0)}"
        harga_jual_teks = f"Rp{data['Harga Jual']}"
        stok_teks = f"{data['Stok Sekarang']} pcs"
        min_teks = f"{data['Batas Minimum']} pcs"
        print(f"{data['id_barang']:<12} {data['Nama Barang']:<25} {harga_jual_teks:<15} {harga_beli_teks:<15} {stok_teks:<15} {min_teks:<15}")



# SEARCHING DATA BARANG
def searching_data_barang():
    
    if not smk_mart_db["barang"]:
        print("Belum ada data barang di database.")
        return
    
    print("\n" + "=" * 40 + " SEARCHING DATA BARANG " + "=" * 40)
    print("=" * 103)
    
    keyword = input("Masukkan Nama Barang yang dicari atau [B]atal: ").lower()
    if keyword == "b":
        print("❌ Pencarian barang dibatalkan.")
        return
    
    hasil_pencarian = []

    for id_barang, data in smk_mart_db["barang"].items():
        if keyword in data["Nama Barang"].lower():
            hasil_pencarian.append({
            "id_barang": id_barang,
            "Nama Barang": data["Nama Barang"],
            "Harga Beli": data.get("Harga Beli", 0),
            "Harga Jual": data["Harga Jual"],
            "Stok Sekarang": data["Stok Sekarang"],
            "Batas Minimum": data["Batas Minimum"]
            })

    if not hasil_pencarian:
        print("❌ Tidak ditemukan barang dengan nama tersebut.")
        return
    print(f"✅ Ditemukan {len(hasil_pencarian)} barang:")
    print(f"\n{'ID Barang':<15} {'Nama Barang':<20} {'Harga Jual':<15} {'Harga Beli':<15} {'Stok Sekarang':<15} {'Batas Minimum':<15}")
    print("-" * 103)

    for data in hasil_pencarian:
     print(f"{data['id_barang']:<15} {data['Nama Barang']:<20} Rp{data['Harga Jual']:<15} Rp{data['Harga Beli']:<15} {data['Stok Sekarang']} pcs{'':<8} {data['Batas Minimum']} pcs")


# EDIT DATA BARANG
def edit_data_barang():
    print("\n=== EDIT DATA BARANG ===")
    
    if not smk_mart_db["barang"]:
        print("Belum ada data barang di database.")
        return

    while True:
        print("Navigasi Cepat: [L]ihat Daftar | [B]atal Edit")
        id_barang = input("Masukkan ID Barang yang ingin diedit: ").strip().upper()
        if id_barang == 'L':
            urutkan_dan_tampilkan_barang()
            continue
        if id_barang == 'B':
            print("❌ Edit data barang dibatalkan.")
            return
        if not id_barang:
            print("❌ ID Barang tidak boleh kosong!")
            return
        if id_barang not in smk_mart_db["barang"]:
            print("ID Barang tidak ditemukan! Silakan masukkan ulang.")
            continue
        break

    data_lama = smk_mart_db["barang"][id_barang].copy()

    nama_baru = data_lama["Nama Barang"]
    harga_beli_baru = data_lama.get("Harga Beli", 0)
    harga_baru = data_lama["Harga Jual"]
    stok_baru = data_lama["Stok Sekarang"]
    min_baru = data_lama["Batas Minimum"]
    
    perubahan_terjadi = False

    while True:
        print(f"\n=== Edit Data Barang [{id_barang}] ===")
        print(f"1. Nama Barang  : {nama_baru}")
        print(f"2. Harga Beli    : Rp{harga_beli_baru}")
        print(f"3. Harga Jual    : Rp{harga_baru}")
        print(f"4. Stok Sekarang : {stok_baru}")
        print(f"5. Batas Minimum : {min_baru}")
        print("6. Simpan Perubahan")
        print("0. Batal / Keluar")
        
        pilihan = input("Pilih menu edit (0-6): ").strip()

        if pilihan == '1':
            input_nama = input("Masukkan Nama Barang Baru: ").strip()
            if not input_nama:
                print("❌ Nama Barang tidak boleh kosong!")
            else:
                nama_baru = input_nama
                perubahan_terjadi = True
                
        elif pilihan == '2':
            harga_beli_baru = input_angka("Masukkan Harga Beli Baru: Rp", minimum=0)
            perubahan_terjadi = True
            
        elif pilihan == '3':
            harga_baru = input_angka("Masukkan Harga Jual Baru: Rp", minimum=harga_beli_baru)
            perubahan_terjadi = True

        elif pilihan == '4':
            stok_baru = input_angka("Masukkan Stok Sekarang Baru: ", minimum=0)
            perubahan_terjadi = True

        elif pilihan == '5':
            min_baru = input_angka("Masukkan Batas Minimum Baru: ", minimum=0)
            perubahan_terjadi = True
                
        elif pilihan == '6':
            if not perubahan_terjadi:
                print("⚠️ Tidak ada perubahan data yang dibuat.")
                return

            konfirmasi_edit = input("Apakah Anda yakin ingin menyimpan perubahan ini? (y/n): ").lower()
            if konfirmasi_edit == 'y':

                smk_mart_db["barang"][id_barang] = {
                    "Nama Barang": nama_baru,
                    "Harga Beli": harga_beli_baru,
                    "Harga Jual": harga_baru,
                    "Stok Sekarang": stok_baru,
                    "Batas Minimum": min_baru
                }
                simpan_database()
                
                log_detail = []
                
                if data_lama["Nama Barang"] != nama_baru:
                    log_detail.append(f"Nama: {data_lama['Nama Barang']} -> {nama_baru}")

                if data_lama.get("Harga Beli", 0) != harga_beli_baru:
                    log_detail.append(f"Harga Beli: Rp{data_lama.get('Harga Beli', 0)} -> Rp{harga_beli_baru}")
                    
                if data_lama["Harga Jual"] != harga_baru:
                    log_detail.append(f"Harga: Rp{data_lama['Harga Jual']} -> Rp{harga_baru}")
                    
                if data_lama["Stok Sekarang"] != stok_baru:
                    log_detail.append(f"Stok: {data_lama['Stok Sekarang']} -> {stok_baru}")
                    
                if data_lama["Batas Minimum"] != min_baru:
                    log_detail.append(f"Batas Min: {data_lama['Batas Minimum']} -> {min_baru}")
                
                keterangan_log = ", ".join(log_detail)

                catat_log_revisi("EDIT", id_barang, keterangan_log)
                
                print("✅ Data barang berhasil diperbarui!")
            else:
                print("❌ Perubahan data barang dibatalkan.")
            return

        elif pilihan == '0':
                print("❌ Edit data barang dibatalkan.")
                return

        else:
            print("❌ Pilihan tidak valid!")
    

# HAPUS DATA BARANG
def hapus_data_barang():
    print("\n=== HAPUS DATA BARANG ===")
    if not smk_mart_db["barang"]:
            print("Belum ada data barang di database.")
            return
    while True:
        print("\nNavigasi Cepat: [L]ihat Daftar | [B]atal Pengarsipan")
        id_barang = input("Masukkan ID Barang yang ingin diarsipkan atau masukkan navigasi cepat: ").strip().lower()
        if id_barang == "l":
            urutkan_dan_tampilkan_barang()
            continue
        if id_barang == "b":
            print("❌ Pengarsipan barang dibatalkan.")
            return
        if id_barang not in smk_mart_db["barang"] or smk_mart_db["barang"][id_barang].get("Terhapus", False):
            print("ID Barang tidak ditemukan! Silakan masukkan ulang.")
            continue
        break

    nama_lama = smk_mart_db["barang"][id_barang]["Nama Barang"]
    konfirmasi_hapus = input(f"Apakah Anda yakin ingin mengarsipkan barang '{nama_lama}' dengan ID '{id_barang}'? (y/n): ").lower()
    if konfirmasi_hapus != 'y':
            print("❌ Pengarsipan barang dibatalkan.")
            return
    else:
        smk_mart_db["barang"][id_barang]["Terhapus"] = True
        simpan_database()
        catat_log_revisi("SOFT_DEL", id_barang, f"Barang '{nama_lama}' diarsipkan")
        print(f"✅ Data barang dengan ID {id_barang} berhasil diarsipkan!")

# TAMBAH DATA TRANSAKSI
def tambah_data_transaksi():
    while True:
        print("\n=== MELAKUKAN TRANSAKSI ===")
        global nomor_nota

        tanggal = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        id_kasir = user_aktif

        keranjang_belanja = []
        total_harga_transaksi = 0
        
        while True:
            print("\n=== Input Barang Belanjaan ===")
            print("Navigasi Cepat: [L]ihat Daftar | [B]atal Transaksi ")
            id_barang = input("Masukkan ID Barang atau Kode Navigasi: ").strip().upper()
            
            if id_barang == 'L':
                urutkan_dan_tampilkan_barang()
                continue

            if id_barang == 'B':
                print("❌ Transaksi dibatalkan.")
                return

            if id_barang not in smk_mart_db["barang"] or smk_mart_db["barang"][id_barang].get("Terhapus", False):
                print("❌ ID Barang tidak ditemukan! Silakan masukkan ID Barang yang valid atau gunakan navigasi cepat.")
                continue
                
            nama_barang = smk_mart_db['barang'][id_barang]['Nama Barang']
            jumlah_beli = input_angka(f"Masukkan Jumlah Beli untuk '{nama_barang}': ", minimum=1)
            
            detail_barang = smk_mart_db["barang"][id_barang]
            sudah_di_keranjang = sum(i["jumlah_beli"] for i in keranjang_belanja if i["id_barang"] == id_barang)
            sisa_stok = detail_barang["Stok Sekarang"] - sudah_di_keranjang

            if jumlah_beli > sisa_stok:
                print(f"❌ Stok tidak cukup! Sisa stok barang ini tinggal {sisa_stok} pcs.")
                continue

            konfirmasi = input(f"Apakah Anda yakin ingin membeli {jumlah_beli} pcs '{nama_barang}'? (y/n): ").lower()
            if konfirmasi != 'y':
                print("❌ Pembelian barang ini dibatalkan.")
                continue 
            
            subtotal = detail_barang["Harga Jual"] * jumlah_beli
            total_harga_transaksi += subtotal
            
            keranjang_belanja.append({
                "id_barang": id_barang,
                "nama_barang": detail_barang["Nama Barang"],
                "harga_beli": detail_barang.get("Harga Beli", 0),
                "harga_satuan": detail_barang["Harga Jual"],
                "jumlah_beli": jumlah_beli,
                "subtotal": subtotal
            })
            print(f"✅ {detail_barang['Nama Barang']} ({jumlah_beli} pcs) berhasil ditambahkan ke keranjang.")

            tanya_lagi = input("Apakah ingin menambahkan barang lain? (y/n): ").lower()
            if tanya_lagi == 'n':
                break

        print("\n==============================================")
        print(f"💸TOTAL YANG HARUS DIBAYAR: Rp{total_harga_transaksi}")
        print("=== METODE PEMBAYARAN ===")
        print("1. Tunai (Cash)")
        print("2. QRIS (Digital)")
        opsi_bayar = input("Pilih metode (1-2): ")
        if opsi_bayar not in ("1", "2"):
            print("❌ Metode pembayaran tidak valid! Transaksi dibatalkan.")
            return

        if opsi_bayar == "1":
            metode = "Tunai"

            jumlah_bayar = input_angka("Masukkan jumlah uang yang dibayarkan: Rp", minimum=total_harga_transaksi)
            if jumlah_bayar < total_harga_transaksi:
                print("❌ Uang yang dibayarkan kurang! Transaksi dibatalkan.")
                return
            kembalian = jumlah_bayar - total_harga_transaksi
        else:
            metode = "QRIS"
            jumlah_bayar = total_harga_transaksi
            kembalian = 0

        for item in keranjang_belanja:
            smk_mart_db["barang"][item["id_barang"]]["Stok Sekarang"] -= item["jumlah_beli"]

        nomor_nota += 1
        id_transaksi = f"TX{nomor_nota:03d}" 

        smk_mart_db["Transaksi"][id_transaksi] = {
        "jumlah_bayar": jumlah_bayar,
        "kembalian": kembalian,
        "tanggal": tanggal,
        "id_kasir": id_kasir,
        "items": keranjang_belanja,
        "total_harga": total_harga_transaksi,
        "metode_pembayaran": metode
        }

        simpan_database()
        catat_log_transaksi(id_transaksi)
        cetak_struk_digital(id_transaksi)
        t_trx = input("\n Tambah transaksi lagi? (y/n): ")
        if t_trx != 'y':
            break        

def cetak_struk_digital(id_transaksi):
    if id_transaksi not in smk_mart_db["Transaksi"]:
        print("ID Transaksi tidak ditemukan!")
        return
    data_tx = smk_mart_db["Transaksi"][id_transaksi]
    print("====================================")
    print("       STRUK DIGITAL SMK MART       ")
    print("====================================")
    print(f"Nota        : {id_transaksi}")
    print(f"Tanggal     : {data_tx['tanggal']}")
    print(f"Kasir       : {data_tx['id_kasir']}")
    print("------------------------------------")
    for item in data_tx["items"]:
        print(f"{item['nama_barang']}")
        print(f"  {item['jumlah_beli']} pcs x Rp{item['harga_satuan']} = Rp{item['subtotal']}")
    print("------------------------------------")
    print(f"Metode      : {data_tx['metode_pembayaran']}")
    print(f"TOTAL BAYAR : Rp{data_tx['total_harga']}")
    if data_tx['metode_pembayaran'] == "Tunai":
        print(f"UANG BAYAR  : Rp{data_tx['jumlah_bayar']}")
        print(f"KEMBALIAN   : Rp{data_tx['kembalian']}")
    else:
        print(f"UANG BAYAR  : Rp{data_tx['total_harga']} (QRIS)")
    print("====================================")
    print("  Terima Kasih Atas Kunjungan Anda  ")
    print("====================================")

def tampilkan_data_transaksi():
    print("\n=== MENAMPILKAN RIWAYAT TRANSAKSI PENJUALAN ===")
    if not smk_mart_db["Transaksi"]:
        print("Belum ada riwayat transaksi penjualan.")
        return
        
    for id_tx, data_tx in smk_mart_db["Transaksi"].items():
        print(f"ID Transaksi / Nota : {id_tx}")
        print(f"Tanggal             : {data_tx['tanggal']}")
        print(f"ID Kasir            : {data_tx['id_kasir']}")
        print("Daftar Barang Belanjaan :")
        for item in data_tx["items"]:
            print(f"  - {item['nama_barang']} ({item['jumlah_beli']} pcs) | Subtotal: Rp{item['subtotal']}")
        print(f"Total Bayar         : Rp{data_tx['total_harga']}")
        print(f"Metode Pembayaran   : {data_tx['metode_pembayaran']}")
        print("====================================================")


# Data Laporan Penjualan
def laporan_penjualan():
    print("\n" + "=" * 45 + " LAPORAN TRANSAKSI PENJUALAN " + "=" * 45)
    print("=" * 119)
    if not smk_mart_db["Transaksi"]:
        print("Belum ada transaksi penjualan yang tercatat.")
        return

    total_uang_masuk = 0
    total_barang_terjual = 0
    total_keuntungan = 0

    print(f"{'Nota':<12} {'Tanggal':<25} {'Kasir':<12} {'Via':<12}{'Nama Barang':<20} {'Jumlah':<12} {'Jual':<12} {'Laba':<12}")
    print("-" * 119)

    for id_tx, data in smk_mart_db["Transaksi"].items():
        laporan_data = {
            "Nota": id_tx,
            "Tgl": data["tanggal"],
            "Kasir": data["id_kasir"],
            "Via": data["metode_pembayaran"]
        }

        for item in data["items"]:
            id_barang = item.get("id_barang", "KOSONG")
            jumlah = item["jumlah_beli"]

            if id_barang == "KOSONG":
                harga_beli_pabrik = 0
            else:
                harga_beli_pabrik = smk_mart_db["barang"].get(id_barang, {}).get("Harga Beli", item["harga_satuan"])

            laba_per_pcs = item["harga_satuan"] - harga_beli_pabrik
            keuntungan_item = laba_per_pcs * jumlah

            total_barang_terjual += jumlah
            total_keuntungan += keuntungan_item

            nama_barang_teks = f"{item['nama_barang']}"
            jumlah_beli_teks = f"{item['jumlah_beli']} pcs"
            jual = f"Rp{item['harga_satuan']}"
            laba = f"Rp{laba_per_pcs * jumlah}"
            print(f"{laporan_data['Nota']:<12} {laporan_data['Tgl']:<25} {laporan_data['Kasir']:<12} {laporan_data['Via']:<12}{nama_barang_teks:<20} {jumlah_beli_teks:<12} {jual:<12} {laba:<12}")
            
        total_uang_masuk += data["total_harga"]
       
    print(f"\nTotal Uang Masuk     : Rp{total_uang_masuk}")
    print(f"Total Barang Terjual : {total_barang_terjual} pcs")
    print(f"Total Keuntungan     : Rp{total_keuntungan}")

# TAMBAH AKTIVITAS GUDANG
def tambah_aktivitas_gudang():
    print("\n=== AKTIVITAS GUDANG ===")
    global nomor_gudang
    while True:
        print("Navigasi Cepat: [L]ihat Daftar | [B]atal:")
        id_barang = input("Masukkan ID Barang atau masukkan navigasi cepat: ").strip().upper()
        if id_barang == "L":
            urutkan_dan_tampilkan_barang()
            continue

        if id_barang == "B":
            print("❌ Aktivitas gudang dibatalkan.")
            return

        if not id_barang:
            print("❌ ID Barang tidak boleh kosong!")
            continue
        break

    tanggal_barang_masuk = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    # 1. Pindahkan pilihan aktivitas ke paling atas agar pembatalan bisa langsung diproses
    jenis_aktivitas = input("Masukkan Jenis Aktivitas [M]asuk | [K]eluar: ").strip().lower()
    
    if jenis_aktivitas not in ("m", "k"):
        print("❌ Jenis aktivitas salah! Gunakan 'm', 'k', atau 'b'.")
        return

    # 2. Input jumlah barang setelah dipastikan jenis aktivitasnya valid
    jumlah_barang = input_angka("Masukkan Jumlah Barang: ", minimum=1) # Ubah minimum ke 1 agar tidak perlu validasi <= 0 lagi
    keterangan_tambahan = input("Keterangan Tambahan: ")

    if jenis_aktivitas == "m":
        response = input(f"Yakin ingin menambahkan {jumlah_barang} pcs stok barang ini ke gudang? (y/n): ").strip().lower()
        if response == "y":
            smk_mart_db["barang"][id_barang]["Stok Sekarang"] += jumlah_barang
            jenis_aktivitas_teks = "MASUK" 
        else:
            print("❌ Aktivitas gudang dibatalkan.")
            return

    elif jenis_aktivitas == "k":
        if jumlah_barang > smk_mart_db["barang"][id_barang]["Stok Sekarang"]:
            print(f"❌ Gagal! Jumlah barang keluar ({jumlah_barang} pcs) melebihi stok fisik saat ini ({smk_mart_db['barang'][id_barang]['Stok Sekarang']} pcs).")
            return
            
        response = input(f"Yakin ingin mengeluarkan {jumlah_barang} pcs stok barang ini dari gudang? (y/n): ").strip().lower()
        if response == "y":
            smk_mart_db["barang"][id_barang]["Stok Sekarang"] -= jumlah_barang
            jenis_aktivitas_teks = "KELUAR"
        else:
            print("❌ Aktivitas gudang dibatalkan.")
            return

    nomor_gudang += 1
    id_aktivitas = f"GDG{nomor_gudang:03d}"
    smk_mart_db["Gudang"][id_aktivitas] = {
    "id_barang": id_barang,
    "tanggal_barang_masuk": tanggal_barang_masuk,
    "jenis_aktivitas": jenis_aktivitas_teks,
    "jumlah_barang": jumlah_barang,
    "keterangan_tambahan": keterangan_tambahan
}
    simpan_database()
    catat_log_revisi(f"GUDANG-{jenis_aktivitas_teks}", id_barang, f"Jumlah: {jumlah_barang} pcs | Ket: {keterangan_tambahan}")
    print("✅ Aktivitas gudang berhasil dicatat dan stok fisik telah disinkronkan!")
    print(f"Stok barang '{smk_mart_db['barang'][id_barang]['Nama Barang']}' sekarang: {smk_mart_db['barang'][id_barang]['Stok Sekarang']} pcs")

# TAMBAH DATA PENGGUNA
def tambah_data_pengguna():
    print("\n=== MENAMBAHKAN DATA PENGGUNA ===")
    id_user = f"USR{len(smk_mart_db['Pengguna']) + 1:03d}"
    if id_user in smk_mart_db["Pengguna"]:
        print("ID USER sudah ada. Silakan masukkan ID USER yang berbeda.")
        return

    username = input("Masukkan Username : ").strip().lower()
    if not username:
        print("❌ Username tidak boleh kosong!")
        return
    for data in smk_mart_db["Pengguna"].values():
        if data["username"].lower() == username.lower():
            print("❌ Username sudah dipakai!")
            return
    password = input("Masukkan Password : ").strip()
    if not password:
        print("❌ Password tidak boleh kosong!")
        return
    role = input("Masukkan Role (Admin/Kasir/Gudang): ").strip().capitalize()
    if role.lower() not in ("admin", "kasir", "gudang"):
        print("❌ Role tidak valid! Gunakan 'Admin', 'Kasir', atau 'Gudang'.")
        return

    smk_mart_db["Pengguna"][id_user] = {
        "username": username,
        "password": password,
        "role": role
    }
    simpan_database()
    print("Data pengguna berhasil ditambahkan!")

# TAMPILKAN DATA PENGGUNA
def tampilkan_data_pengguna():
    print("\n" + "=" * 16 + " DATA PENGGUNA " + "=" * 17)
    print("=" * 48)
    if not smk_mart_db["Pengguna"]:
        print("Tidak ada data pengguna yang ditemukan.")
        return

    print(f"{'Id user':<15} {'Username':<15} {'Role':<15}")
    print("-" * 48)

    prioritas_role = {
    "admin": 1,
    "gudang": 2,
    "kasir": 3
    }

    # Mengurutkan database pengguna berdasarkan bobot prioritas role
    pengguna_terurut = sorted(
        smk_mart_db["Pengguna"].items(),
        key=lambda x: prioritas_role.get(x[1]["role"].lower(), 99)
    )


    for id_user, data_pengguna in pengguna_terurut:
        data = {
            "Id user": id_user,
            "Username": data_pengguna["username"],
            "Role": data_pengguna["role"],
        }

        print(f"{data['Id user']:<15} {data['Username']:<15} {data['Role']}")
        

       

while True: 
    while True:
        if login_sistem():
            break

    logout = False

    while True:
        cek_stok_minimum()

        if role_aktif.lower() == "admin":
            print("\n===== DASHBOARD UTAMA (ADMIN) =====")
            print("1. Kelola Hak Akses / Pengguna (User Management)")
            print("2. Laporan & Keuangan (Finance)")
            print("3. Pindah Ke MENU KASIR")
            print("4. Pindah Ke MENU GUDANG")
            print("0. Log Out")
            pilihan = input("Pilih menu (1-4): ").strip()

        elif role_aktif.lower() == "kasir":
            print("\n===== MENU UTAMA APLIKASI SMK MART (KASIR) =====")
            print("1. Tampilkan Semua Barang")
            print("2. Searching Data Barang")
            print("3. Tambah Transaksi Penjualan")
            print("0. Log Out")
            pilihan = input("Pilih menu (1-3): ").strip()

        elif role_aktif.lower() == "gudang":
            print("\n===== MENU UTAMA APLIKASI SMK MART (GUDANG) =====")
            print("1. Tambah Data Barang")
            print("2. Catat Aktivitas Gudang")
            print("3. Tampilkan Semua Barang")
            print("4. Searching Data Barang")
            print("5. Edit Data Barang")
            print("6. Hapus Data Barang")
            print("0. Log Out")
            pilihan = input("Pilih menu (1-6): ").strip()

        role = role_aktif.lower()
        if role == "admin":
            if pilihan == "1":
                # SUBMENU USER MANAGEMENT
                while True:
                    print("\n--- KELOLA PENGGUNA ---")
                    print("1. Tambah Data Pengguna")
                    print("2. Tampilkan Semua Pengguna")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-2): ").strip()
                    if sub_pil == "1": tambah_data_pengguna()
                    elif sub_pil == "2": tampilkan_data_pengguna()
                    elif sub_pil == "0": break
                    else: print("❌ Pilihan salah!")
            elif pilihan == "2":
                # SUBMENU LAPORAN & KEUANGAN
                while True:
                    print("\n--- LAPORAN & KEUANGAN ---")
                    print("1. Laporan Penjualan")
                    print("2. Tampilkan Riwayat Transaksi")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-2): ").strip()
                    if sub_pil == "1": laporan_penjualan()
                    elif sub_pil == "2": tampilkan_data_transaksi()
                    elif sub_pil == "0": break
                    else: print("❌ Pilihan salah!")

            elif pilihan == "3":
                while True:
                    print("\n--- MENGAKSES: MENU KASIR ---")
                    print("1. Tampilkan Semua Barang")
                    print("2. Searching Data Barang")
                    print("3. Tambah Transaksi Penjualan")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-3): ").strip()
                    if sub_pil == "1": urutkan_dan_tampilkan_barang()
                    elif sub_pil == "2": searching_data_barang()
                    elif sub_pil == "3": tambah_data_transaksi()
                    elif sub_pil == "0": break
                    else: print("❌ Pilihan salah!")

            elif pilihan == "4":
                while True:
                    print("\n--- MENGAKSES: MENU GUDANG ---")
                    print("1. Tambah Data Barang")
                    print("2. Catat Aktivitas Gudang")
                    print("3. Tampilkan Semua Barang")
                    print("4. Searching Data Barang")
                    print("5. Edit Data Barang")
                    print("6. Hapus Data Barang")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-6): ").strip()
                    if sub_pil == "1": tambah_data_barang()
                    elif sub_pil == "2": tambah_aktivitas_gudang()
                    elif sub_pil == "3": urutkan_dan_tampilkan_barang()
                    elif sub_pil == "4": searching_data_barang()
                    elif sub_pil == "5": edit_data_barang()
                    elif sub_pil == "6": hapus_data_barang()
                    elif sub_pil == "0": break
                    else: print("❌ Pilihan salah!")

        elif role == "kasir":
            if pilihan == "1": urutkan_dan_tampilkan_barang()
            elif pilihan == "2": searching_data_barang()
            elif pilihan == "3": tambah_data_transaksi()
            elif pilihan == "0":
                konfirmasi = input("Apakah Anda yakin ingin log out? (y/n): ").lower()
                if konfirmasi == "y":
                    print("Terima kasih! Log Out dari akun sekarang.")
                    logout = True
                    break
                else:
                    print("Log out dibatalkan. Kembali ke menu utama.")
            else:
                print("Pilihan salah! Silakan masukkan pilihan yang valid.")

                
        elif role == "gudang":
            if pilihan == "1": tambah_data_barang()
            elif pilihan == "2": tambah_aktivitas_gudang()
            elif pilihan == "3": urutkan_dan_tampilkan_barang()
            elif pilihan == "4": searching_data_barang()
            elif pilihan == "5": edit_data_barang()
            elif pilihan == "6": hapus_data_barang()
            elif pilihan == "0":
                konfirmasi = input("Apakah Anda yakin ingin log out? (y/n): ").lower()
                if konfirmasi == "y":
                    print("Terima kasih! Log Out dari akun sekarang.")
                    logout = True
                    break
                else:
                    print("Log out dibatalkan. Kembali ke menu utama.")
            else:
                print("Pilihan salah! Silakan masukkan pilihan yang valid.")

    if logout:
        continue


    
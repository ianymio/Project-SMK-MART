
import json
import os

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

# 1. Membaca data dari JSON saat program baru dibuka
def muat_database():
    if os.path.exists(FILE_DB):
        with open(FILE_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return smk_mart_db

# 2. Menyimpan data terbaru ke JSON
def simpan_database():
    with open(FILE_DB, "w", encoding="utf-8") as f:
        json.dump(smk_mart_db, f, indent=4)

# 3. Mencatat riwayat revisi barang ke TXT (tanpa datetime)
def catat_log_revisi(aksi, id_barang, keterangan):
    with open(FILE_LOG_REVISI, "a", encoding="utf-8") as f:
        f.write(f"({user_aktif}) | {aksi} | ID: {id_barang} | {keterangan}\n")

# 4. Mencatat riwayat transaksi ke TXT
def catat_log_transaksi(id_tx):
    data = smk_mart_db["Transaksi"][id_tx]
    with open(FILE_LOG_TRANSAKSI, "a", encoding="utf-8") as f:
        f.write(f"=== NOTA {id_tx} | Tgl: {data['tanggal']} | Kasir: {data['id_kasir']} ===\n")
        for item in data["items"]:
            f.write(f"- {item['nama_barang']} x{item['jumlah_beli']} = Rp{item['subtotal']}\n")
        f.write(f"Total: Rp{data['total_harga']} ({data['metode_pembayaran']})\n\n")

# Jalankan muat_database() dan sesuaikan nomor urut otomatis
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
    print("================================================")
    print("       SELAMAT DATANG DI APLIKASI SMK MART       ")
    print("================================================")
    print("Silakan login terlebih dahulu.")
    username = input("Username: ")
    password = input("Password: ")
    
    for id_user, data in smk_mart_db["Pengguna"].items():
        if data["username"] == username and data["password"] == password:
            user_aktif = data["username"]
            role_aktif = data["role"]
            print(f"✅ Login Berhasil! Selamat datang, {user_aktif} ({role_aktif}).")
            return True
            
    print("❌ Username atau Password salah!")
    return False

# PENGECEKAN STOK MINIMUM
def cek_stok_minimum():
    ada_peringatan = False
    print("====== SISTEM MONITORING STOK ======")
    if not smk_mart_db["barang"]:
        print("💡 Sistem: Belum ada data barang terdaftar untuk dipindai.")
        print("================================================")
        return
    for id_barang, data in smk_mart_db["barang"].items():
        if data["Stok Sekarang"] <= data["Batas Minimum"]:
            print(f"⚠️ PERINGATAN! Stok barang '{data['Nama Barang']}' (ID: {id_barang}) kritis!")
            print(f"   Stok Saat Ini: {data['Stok Sekarang']} | Batas Minimum: {data['Batas Minimum']}")
            ada_peringatan = True
    if not ada_peringatan:
        print("✅ Semua stok barang berada dalam kondisi aman.")
    print("================================================")

# TAMBAH DATA BARANG
def tambah_data_barang():
    print("=== Menambahkan Data Barang ===")
    id_barang = input("Masukkan ID Barang: ")
    if id_barang in smk_mart_db["barang"]:
        print("ID barang sudah ada! Masukkan ID Barang baru.")
        return

    nama_barang = input("Masukkan Nama Barang: ")
    harga_jual = input_angka("Masukkan Harga Jual: Rp", minimum=0)
    stok_sekarang = input_angka("Masukkan Stok Sekarang: ", minimum=0)
    minimal_stok = input_angka("Masukkan Minimal Stok: ", minimum=0)

    smk_mart_db["barang"][id_barang] = {
        "Nama Barang": nama_barang,
        "Harga Jual": harga_jual,
        "Stok Sekarang": stok_sekarang,
        "Batas Minimum": minimal_stok
    }
    simpan_database()
    catat_log_revisi("TAMBAH", id_barang, f"{nama_barang} | Harga: Rp{harga_jual} | Stok: {stok_sekarang}")

    print(f"Data barang {nama_barang} berhasil ditambahkan!")  

# TAMPILKAN DAN MENGURUTKAN DATA BARANG
def urutkan_dan_tampilkan_barang():
    print("=== DAFTAR DATA BARANG ===")
    if not smk_mart_db["barang"]:
        print("Belum ada data barang di database.")
        return
    
    list_barang = []
    for id_barang, data in smk_mart_db["barang"].items():
        item = {
            "id_barang": id_barang,
            "Nama Barang": data["Nama Barang"],
            "Harga Jual": data["Harga Jual"],
            "Stok Sekarang": data["Stok Sekarang"],
            "Batas Minimum": data["Batas Minimum"]
        }
        list_barang.append(item)
    
    n = len(list_barang)
    for i in range(n):
        for j in range(0, n - i - 1):
            if list_barang[j]["Nama Barang"].lower() > list_barang[j + 1]["Nama Barang"].lower():
                list_barang[j], list_barang[j + 1] = list_barang[j + 1], list_barang[j]
    for data in list_barang:
        print(f"ID Barang     : {data['id_barang']}")
        print(f"Nama Barang   : {data['Nama Barang']}")
        print(f"Harga Jual    : Rp{data['Harga Jual']}")
        print(f"Stok Sekarang : {data['Stok Sekarang']} pcs")
        print(f"Batas Minimum : {data['Batas Minimum']} pcs")
        print("====================================")

# SEARCHING DATA BARANG
def searching_data_barang():
    print("=== SEARCHING DATA BARANG ===")
    if not smk_mart_db["barang"]:
        print("Belum ada data barang di database.")
        return
    
    keyword = input("Masukkan Nama Barang yang dicari: ").lower()
    hasil_pencarian = []

    for id_barang, data in smk_mart_db["barang"].items():
        if keyword in data["Nama Barang"].lower():
            hasil_pencarian.append({
                "id_barang": id_barang,
                "Nama Barang": data["Nama Barang"],
                "Harga Jual": data["Harga Jual"],
                "Stok Sekarang": data["Stok Sekarang"],
                "Batas Minimum": data["Batas Minimum"]
            })
    if not hasil_pencarian:
        print("❌ Tidak ditemukan barang dengan nama tersebut.")
        return
    print(f"✅ Ditemukan {len(hasil_pencarian)} barang:")
    for data in hasil_pencarian:
        print(f"ID Barang     : {data['id_barang']}")
        print(f"Nama Barang   : {data['Nama Barang']}")
        print(f"Harga Jual    : Rp{data['Harga Jual']}")
        print(f"Stok Sekarang : {data['Stok Sekarang']} pcs")
        print(f"Batas Minimum : {data['Batas Minimum']} pcs")
        print("====================================")

# EDIT DATA BARANG
def edit_data_barang():
    print("=== EDIT DATA BARANG ===")
    if not smk_mart_db["barang"]:
            print("Belum ada data barang di database.")
            return
    id_barang = input("Masukkan ID Barang yang ingin diedit: ")
    if id_barang not in smk_mart_db["barang"]:
        print("ID Barang tidak ditemukan!")
        return

    data_lama = smk_mart_db["barang"][id_barang].copy()

    print("=== Masukkan Data Baru ===")
    smk_mart_db["barang"][id_barang]["Nama Barang"] = input("Masukkan Nama Barang Baru: ")
    smk_mart_db["barang"][id_barang]["Harga Jual"] = input_angka("Masukkan Harga Jual Baru: Rp", minimum=0)
    smk_mart_db["barang"][id_barang]["Stok Sekarang"] = input_angka("Masukkan Stok Sekarang Baru: ", minimum=0)
    smk_mart_db["barang"][id_barang]["Batas Minimum"] = input_angka("Masukkan Batas Minimum Baru: ", minimum=0)

    simpan_database()
    catat_log_revisi("EDIT", id_barang, f"Stok {data_lama['Stok Sekarang']} -> {smk_mart_db['barang'][id_barang]['Stok Sekarang']}, Harga Rp{data_lama['Harga Jual']} -> Rp{smk_mart_db['barang'][id_barang]['Harga Jual']}")

    print("✅ Data barang berhasil diperbarui!")
#untuk tambah baran(tambah stok berbeda denan edit data barang) -> revisi

# HAPUS DATA BARANG
def hapus_data_barang():
    print("=== HAPUS DATA BARANG ===")
    if not smk_mart_db["barang"]:
            print("Belum ada data barang di database.")
            return
    id_barang = input("Masukkan ID Barang yang ingin dihapus: ")
    if id_barang not in smk_mart_db["barang"]:
        print("ID Barang tidak ditemukan!")
        return
    nama_lama = smk_mart_db["barang"][id_barang]["Nama Barang"]
    del smk_mart_db["barang"][id_barang]
    simpan_database()
    catat_log_revisi("HAPUS", id_barang, f"Barang '{nama_lama}' dihapus")
    print(f"✅ Data barang dengan ID {id_barang} berhasil dihapus!")

# TAMBAH DATA TRANSAKSI
def tambah_data_transaksi():
    print("=== MELAKUKAN TRANSAKSI ===")
    global nomor_nota
    id_transaksi = f"TX{nomor_nota + 1:03d}"  # nomor nota buat auto (revisi) #dn

    tanggal = input("Masukkan Tanggal (DD-MM-YYYY): ").strip()
    id_kasir = user_aktif

    keranjang_belanja = []
    total_harga_transaksi = 0
    
    while True:
        print("=== Input Barang Belanjaan ===")
        id_barang = input("Masukkan ID Barang (ketik '0' untuk check out, '1' untuk lihat daftar barang): ")

        if id_barang == '0':
            if not keranjang_belanja:
                print("❌ Keranjang masih kosong! Transaksi dibatalkan.")
                return
            else:
                break
        
        if id_barang == '1':
            urutkan_dan_tampilkan_barang()
            continue

        if id_barang not in smk_mart_db["barang"]:
            print("❌ ID Barang tidak ditemukan! Silakan cek kembali daftar barang.")
            continue

        # 4. Proses input jumlah dan konfirmasi
        nama_barang = smk_mart_db['barang'][id_barang]['Nama Barang']
        jumlah_beli = input_angka(f"Masukkan Jumlah Beli untuk '{nama_barang}': ", minimum=1)
        
        konfirmasi = input(f"Apakah Anda yakin ingin membeli {jumlah_beli} pcs '{nama_barang}'? (y/n): ").lower()
        if konfirmasi != 'y':
            print("❌ Pembelian barang ini dibatalkan.")
            continue 

        detail_barang = smk_mart_db["barang"][id_barang]
        
        sudah_di_keranjang = sum(i["jumlah_beli"] for i in keranjang_belanja if i["id_barang"] == id_barang)
        sisa_stok = detail_barang["Stok Sekarang"] - sudah_di_keranjang
        if jumlah_beli > sisa_stok:
            print(f"❌ Stok tidak cukup! Sisa stok barang ini tinggal {sisa_stok} pcs.")
            continue
        
        subtotal = detail_barang["Harga Jual"] * jumlah_beli
        total_harga_transaksi += subtotal
        
        keranjang_belanja.append({
            "id_barang": id_barang,
            "nama_barang": detail_barang["Nama Barang"],
            "harga_satuan": detail_barang["Harga Jual"],
            "jumlah_beli": jumlah_beli,
            "subtotal": subtotal
        })
        print(f"✅ {detail_barang['Nama Barang']} ({jumlah_beli} pcs) berhasil ditambahkan ke keranjang.")

    print("==============================================")
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
    print("=== MENAMPILKAN RIWAYAT TRANSAKSI PENJUALAN ===")
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
    print("=== LAPORAN TRANSAKSI PENJUALAN ===")
    if not smk_mart_db["Transaksi"]:
        print("Belum ada transaksi penjualan yang tercatat.")
        return
    
    total_uang_masuk = 0
    total_barang_terjual = 0
    
    for id_tx, data in smk_mart_db["Transaksi"].items():
        print(f"Nota: {id_tx} | Tgl: {data['tanggal']} | Kasir: {data['id_kasir']} | Via: {data['metode_pembayaran']}")
        for item in data["items"]:
            print(f"  -> {item['nama_barang']} x{item['jumlah_beli']} pcs | Subtotal: Rp{item['subtotal']}")
            total_barang_terjual += item["jumlah_beli"]
        total_uang_masuk += data["total_harga"]

    print(f"Total Uang Masuk     : Rp{total_uang_masuk}")
    print(f"Total Barang Terjual : {total_barang_terjual} pcs")

# TAMBAH AKTIVITAS GUDANG
def tambah_aktivitas_gudang():
    print("=== AKTIVITAS GUDANG ===")
    global nomor_gudang
    id_barang = input("Masukkan ID Barang: ")
    if id_barang not in smk_mart_db["barang"]:
        print("ID Barang tidak ditemukan! Silakan cek kembali daftar barang.")
        return
    tanggal_barang_masuk = input("Masukkan Tanggal Aktivitas (DD-MM-YYYY): ")
    jenis_aktivitas = input("Masukkan Jenis Aktivitas (Masuk/Keluar): ")
    jumlah_barang = input_angka("Masukkan Jumlah Barang: ", minimum=0)
    if jumlah_barang <= 0:
        print("Jumlah barang harus lebih dari 0!")
        return
    keterangan_tambahan = input("Keterangan Tambahan: ")

    if jenis_aktivitas.lower() == "masuk":
        smk_mart_db["barang"][id_barang]["Stok Sekarang"] += jumlah_barang
    elif jenis_aktivitas.lower() == "keluar":
        if jumlah_barang > smk_mart_db["barang"][id_barang]["Stok Sekarang"]:
            print("Gagal! Jumlah barang keluar melebihi stok fisik gudang saat ini.")
            return
        smk_mart_db["barang"][id_barang]["Stok Sekarang"] -= jumlah_barang
    else:
        print("Jenis aktivitas salah! Gunakan kata 'masuk' atau 'keluar'.")
        return

    nomor_gudang += 1
    id_aktivitas = f"GDG{nomor_gudang:03d}"
    smk_mart_db["Gudang"][id_aktivitas] = {
    "id_barang": id_barang,
    "tanggal_barang_masuk": tanggal_barang_masuk,
    "jenis_aktivitas": jenis_aktivitas.upper(),
    "jumlah_barang": jumlah_barang,
    "keterangan_tambahan": keterangan_tambahan
}
    simpan_database()
    catat_log_revisi(f"GUDANG-{jenis_aktivitas.upper()}", id_barang, f"Jumlah: {jumlah_barang} pcs | Ket: {keterangan_tambahan}")
    print("✅ Aktivitas gudang berhasil dicatat dan stok fisik telah disinkronkan!")

# TAMBAH DATA PENGGUNA
def tambah_data_pengguna():
    print("=== MENAMBAHKAN DATA PENGGUNA ===")
    id_user = f"USR{len(smk_mart_db['Pengguna']) + 1:03d}"
    if id_user in smk_mart_db["Pengguna"]:
        print("ID USER sudah ada. Silakan masukkan ID USER yang berbeda.")
        return

    username = input("Masukkan Username : ").strip()
    if not username:
        print("❌ Username tidak boleh kosong!")
        return
    for data in smk_mart_db["Pengguna"].values():
        if data["username"].lower() == username.lower():
            print("❌ Username sudah dipakai!")
            return
    password = input("Masukkan Password : ")
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
    print("=== MENAMPILKAN DATA PENGGUNA ===")
    if not smk_mart_db["Pengguna"]:
        print("Tidak ada data pengguna yang ditemukan.")
        return

    for id_user, data_pengguna in smk_mart_db["Pengguna"].items():
        print(f"ID USER  : {id_user}")
        print(f"Username : {data_pengguna['username']}")
        print(f"Role     : {data_pengguna['role']}")
        print("====================================================")

# ==========================================
logout = False
while True: 
    while True:
        if login_sistem():
            break

    while True:
        cek_stok_minimum()
        if role_aktif.lower() == "admin":
            print("===== MENU UTAMA APLIKASI SMK MART (ADMIN) =====")
            print("1. Tambah Data Barang")
            print("2. Tampilkan Semua Barang")
            print("3. Searching Data Barang")
            print("4. Edit Data Barang")
            print("5. Hapus Data Barang")
            print("6. Tambah Transaksi Penjualan")
            print("7. Tampilkan Riwayat Transaksi")
            print("8. Laporan Penjualan")
            print("9. Catat Aktivitas Gudang")
            print("10. Tambah Data Pengguna")
            print("11. Tampilkan Semua Pengguna")
            print("12. Log Out")
            pilihan = input("Pilih menu (1-12): ")
        elif role_aktif.lower() == "kasir":
            print("===== MENU UTAMA APLIKASI SMK MART (KASIR) =====")
            print("1. Tampilkan Semua Barang")
            print("2. Searching Data Barang")
            print("3. Tambah Transaksi Penjualan")
            print("4. Tampilkan Riwayat Transaksi")
            print("5. Log Out")
            pilihan = input("Pilih menu (1-6): ")
        elif role_aktif.lower() == "gudang":
            print("===== MENU UTAMA APLIKASI SMK MART (GUDANG) =====")
            print("1. Tambah Data Barang")
            print("2. Catat Aktivitas Gudang")
            print("3. Tampilkan Semua Barang")
            print("4. Searching Data Barang")
            print("5. Edit Data Barang")
            print("6. Hapus Data Barang")
            print("7. Log Out")
            pilihan = input("Pilih menu (1-7): ")

        role = role_aktif.lower()
        if role == "admin":
            if pilihan == "1": tambah_data_barang()
            elif pilihan == "2": urutkan_dan_tampilkan_barang()
            elif pilihan == "3": searching_data_barang()
            elif pilihan == "4": edit_data_barang()
            elif pilihan == "5": hapus_data_barang()
            elif pilihan == "6": tambah_data_transaksi()
            elif pilihan == "7": tampilkan_data_transaksi()
            elif pilihan == "8": laporan_penjualan()
            elif pilihan == "9": tambah_aktivitas_gudang()
            elif pilihan == "10": tambah_data_pengguna()
            elif pilihan == "11": tampilkan_data_pengguna()
            elif pilihan == "12":
                pilihan = input("Apakah Anda yakin ingin log out? (y/n): ").lower()
                if pilihan == "y":
                    print("Terima kasih! Log Out dari akun sekarang.")
                    logout = True
                    break
                else:
                    print("Log out dibatalkan. Kembali ke menu utama.")
                print("Terima kasih! Log Out dari akun sekarang.")
                logout = True
                break
            else:
                print("Pilihan salah! Silakan ketik angka 1 sampai 12.")
                
        elif role == "kasir":
            if pilihan == "1": urutkan_dan_tampilkan_barang()
            elif pilihan == "2": searching_data_barang()
            elif pilihan == "3": tambah_data_transaksi()
            elif pilihan == "4": tampilkan_data_transaksi()
            elif pilihan == "5":
                pilihan = input("Apakah Anda yakin ingin log out? (y/n): ").lower()
                if pilihan == "y":
                    print("Terima kasih! Log Out dari akun sekarang.")
                    logout = True
                    break
                else:
                    print("Log out dibatalkan. Kembali ke menu utama.")
                print("Terima kasih! Log Out dari akun sekarang.")
                logout = True
                break
            else:
                print("Pilihan salah! Silakan ketik angka 1 sampai 5.")
                
        elif role == "gudang":
            if pilihan == "1": tambah_data_barang()
            elif pilihan == "2": tambah_aktivitas_gudang()
            elif pilihan == "3": urutkan_dan_tampilkan_barang()
            elif pilihan == "4": searching_data_barang()
            elif pilihan == "5": edit_data_barang()
            elif pilihan == "6": hapus_data_barang()
            elif pilihan == "7":
                pilihan = input("Apakah Anda yakin ingin log out? (y/n): ").lower()
                if pilihan == "y":
                    print("Terima kasih! Log Out dari akun sekarang.")
                    logout = True
                    break
                else:
                    print("Log out dibatalkan. Kembali ke menu utama.")
            else:
                print("Pilihan salah! Silakan ketik angka 1 sampai 7.")



        ##menu ditampilkan bersadarkan dari role, halaman awal hanya login lalu setelah logim silahkan dicek role sebagai apa dan menu yang bisa diakses apa saja

from pprint import pprint


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

nomor_nota = 0
user_aktif = None
role_aktif = None

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
    harga_jual = int(input("Masukkan Harga Jual: Rp"))
    stok_sekarang = int(input("Masukkan Stok Sekarang: "))
    minimal_stok = int(input("Masukkan Minimal Stok: "))

    smk_mart_db["barang"][id_barang] = {
        "Nama Barang": nama_barang,
        "Harga Jual": harga_jual,
        "Stok Sekarang": stok_sekarang,
        "Batas Minimum": minimal_stok
    }
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
    print("=== Masukkan Data Baru ===")
    smk_mart_db["barang"][id_barang]["Nama Barang"] = input("Masukkan Nama Barang Baru: ")
    smk_mart_db["barang"][id_barang]["Harga Jual"] = int(input("Masukkan Harga Jual Baru: Rp"))
    smk_mart_db["barang"][id_barang]["Stok Sekarang"] = int(input("Masukkan Stok Sekarang Baru: "))
    smk_mart_db["barang"][id_barang]["Batas Minimum"] = int(input("Masukkan Batas Minimum Baru: "))
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
    del smk_mart_db["barang"][id_barang]
    print(f"✅ Data barang dengan ID {id_barang} berhasil dihapus!")

# TAMBAH DATA TRANSAKSI
def tambah_data_transaksi():
    print("=== MELAKUKAN TRANSAKSI ===")
    global nomor_nota
    id_transaksi = f"TX{nomor_nota + 1:03d}"  # nomor nota buat auto (revisi)

    tanggal = input("Masukkan Tanggal (DD-MM-YYYY): ")
    id_kasir = input("Masukkan ID Kasir yang melayani: ")

    keranjang_belanja = []
    total_harga_transaksi = 0
    
    while True:
        print("=== Input Barang Belanjaan ===")
        id_barang = input("Masukkan ID Barang (atau ketik '0' untuk check out): ")
        if id_barang == '0':
            if not keranjang_belanja:
                print("❌ Keranjang masih kosong! Transaksi dibatalkan.")
                return
            break
        if id_barang not in smk_mart_db["barang"]:
            print("❌ ID Barang tidak ditemukan! Silakan cek kembali daftar barang.")
            continue
            
        jumlah_beli = int(input(f"Masukkan Jumlah Beli untuk '{smk_mart_db['barang'][id_barang]['Nama Barang']}': "))
        detail_barang = smk_mart_db["barang"][id_barang]
        
        if jumlah_beli > detail_barang["Stok Sekarang"]:
            print(f"❌ Stok tidak cukup! Sisa stok barang ini tinggal {detail_barang['Stok Sekarang']} pcs.")
            continue
            
        subtotal = detail_barang["Harga Jual"] * jumlah_beli
        total_harga_transaksi += subtotal
        smk_mart_db["barang"][id_barang]["Stok Sekarang"] -= jumlah_beli
        
        keranjang_belanja.append({
            "id_barang": id_barang,
            "nama_barang": detail_barang["Nama Barang"],
            "harga_satuan": detail_barang["Harga Jual"],
            "jumlah_beli": jumlah_beli,
            "subtotal": subtotal
        })
        print(f"✅ {detail_barang['Nama Barang']} ({jumlah_beli} pcs) berhasil ditambahkan ke keranjang.")

    print(f"TOTAL YANG HARUS DIBAYAR: Rp{total_harga_transaksi}")
    print("=== METODE PEMBAYARAN ===")
    print("1. Tunai (Cash)")
    print("2. QRIS (Digital)")
    opsi_bayar = input("Pilih metode (1-2): ")
    if opsi_bayar == "1":
        jumlah_bayar = int(input("Masukkan jumlah uang yang dibayarkan: Rp"))
        if jumlah_bayar < total_harga_transaksi:
            print("❌ Uang yang dibayarkan kurang! Transaksi dibatalkan.")
            return
        else:
            kembalian = jumlah_bayar - total_harga_transaksi
    metode = "Tunai" if opsi_bayar == "1" else "QRIS" #jika cash harus ada jumlah bayar dan kembalian (revisi)d

    smk_mart_db["Transaksi"][id_transaksi] = {
        "tanggal": tanggal,
        "id_kasir": id_kasir,
        "items": keranjang_belanja,
        "total_harga": total_harga_transaksi,
        "metode_pembayaran": metode
    }
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
nomor_gudang = 0
def tambah_aktivitas_gudang():
    print("=== AKTIVITAS GUDANG ===")
    global nomor_gudang
    id_barang = input("Masukkan ID Barang: ")
    if id_barang not in smk_mart_db["barang"]:
        print("ID Barang tidak ditemukan! Silakan cek kembali daftar barang.")
        return
    tanggal_barang_masuk = input("Masukkan Tanggal Aktivitas (DD-MM-YYYY): ")
    jenis_aktivitas = input("Masukkan Jenis Aktivitas (Masuk/Keluar): ")
    jumlah_barang = int(input("Masukkan Jumlah Barang: "))
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
    smk_mart_db["Gudang"][id_barang] = {
        "tanggal_barang_masuk": tanggal_barang_masuk,
        "jenis_aktivitas": jenis_aktivitas.upper(),
        "jumlah_barang": jumlah_barang,
        "keterangan_tambahan": keterangan_tambahan
    }
    print("✅ Aktivitas gudang berhasil dicatat dan stok fisik telah disinkronkan!")
    print(f"Data Gudang Saat Ini: {smk_mart_db['Gudang']}")

# TAMBAH DATA PENGGUNA
def tambah_data_pengguna():
    print("=== MENAMBAHKAN DATA PENGGUNA ===")
    id_user = input("Masukkan ID USER : ")
    if id_user in smk_mart_db["Pengguna"]:
        print("ID USER sudah ada. Silakan masukkan ID USER yang berbeda.")
        return

    username = input("Masukkan Username : ")
    password = input("Masukkan Password : ")
    role = input("Masukkan Role (Admin/Kasir/Gudang): ")

    smk_mart_db["Pengguna"][id_user] = {
        "username": username,
        "password": password,
        "role": role
    }
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
            print("12. Keluar dari Program")
            pilihan = input("Pilih menu (1-12): ")
        elif role_aktif.lower() == "kasir":
            print("===== MENU UTAMA APLIKASI SMK MART (KASIR) =====")
            print("1. Tambah Transaksi Penjualan")
            print("2. Tampilkan Riwayat Transaksi")
            print("3. Laporan Penjualan")
            print("4. Keluar dari Program")
            pilihan = input("Pilih menu (1-4): ")
        elif role_aktif.lower() == "gudang":
            print("===== MENU UTAMA APLIKASI SMK MART (GUDANG) =====")
            print("1. Tambah Data Barang")
            print("2. Catat Aktivitas Gudang")
            print("3. Tampilkan Semua Barang")
            print("4. Searching Data Barang")
            print("5. Edit Data Barang")
            print("6. Hapus Data Barang")
            print("7. Keluar dari Program")
            pilihan = input("Pilih menu (1-7): ")

        if pilihan == "1":
            if role_aktif.lower() == "admin" or role_aktif.lower() == "gudang":
                tambah_data_barang()
            elif role_aktif.lower() == "kasir":
                tambah_data_transaksi()
        elif pilihan == "2":
            if role_aktif.lower() == "admin":
                urutkan_dan_tampilkan_barang()
            elif role_aktif.lower() == "kasir":
                tampilkan_data_transaksi()
            elif role_aktif.lower() == "gudang":
                tambah_aktivitas_gudang()
        elif pilihan == "3":
            if role_aktif.lower() == "admin":
                searching_data_barang()
            elif role_aktif.lower() == "kasir":
                laporan_penjualan()
            elif role_aktif.lower() == "gudang":
                urutkan_dan_tampilkan_barang()
        elif pilihan == "4":
            if role_aktif.lower() == "admin":
                edit_data_barang()
            elif role_aktif.lower() == "kasir":
                print("Terima kasih! Keluar dari program SMK Mart.")
                logout = True
                break
            elif role_aktif.lower() == "gudang":
                searching_data_barang()
        elif pilihan == "5":
            if role_aktif.lower() == "admin":
                hapus_data_barang()
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
            elif role_aktif.lower() == "gudang":
                edit_data_barang()
        elif pilihan == "6":
            if role_aktif.lower() == "admin":
                tambah_data_transaksi()
            elif role_aktif.lower() == "gudang":
                hapus_data_barang()
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
        elif pilihan == "7":
            if role_aktif.lower() == "admin":
                tampilkan_data_transaksi()
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
            elif role_aktif.lower() == "gudang":
                print("Terima kasih! Keluar dari program SMK Mart.")
                logout = True
                break
        elif pilihan == "8":
            if role_aktif.lower() == "admin":
                laporan_penjualan()
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
            elif role_aktif.lower() == "gudang":
                print("Pilihan salah! Silakan ketik angka 1 sampai 7.")
        elif pilihan == "9":
            if role_aktif.lower() == "admin":
                tambah_aktivitas_gudang()
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
            elif role_aktif.lower() == "gudang":
                print("Pilihan salah! Silakan ketik angka 1 sampai 7.")
        elif pilihan == "10":
            if role_aktif.lower() == "admin":
                tambah_data_pengguna()
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
            elif role_aktif.lower() == "gudang":
                print("Pilihan salah! Silakan ketik angka 1 sampai 7.")
        elif pilihan == "11":
            if role_aktif.lower() == "admin":
                tampilkan_data_pengguna() 
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
            elif role_aktif.lower() == "gudang":
                print("Pilihan salah! Silakan ketik angka 1 sampai 7.")   
        elif pilihan == "12":
            if role_aktif.lower() == "admin":
                print("Terima kasih! Keluar dari program SMK Mart.")
                logout = True
                break
            elif role_aktif.lower() == "kasir":
                print("Pilihan salah! Silakan ketik angka 1 sampai 4.")
            elif role_aktif.lower() == "gudang":
                print("Pilihan salah! Silakan ketik angka 1 sampai 7.")
        else:
            print("Pilihan salah! Silakan ketik angka 1 sampai 12.")



        ##menu ditampilkan bersadarkan dari role, halaman awal hanya login lalu setelah logim silahkan dicek role sebagai apa dan menu yang bisa diakses apa saja
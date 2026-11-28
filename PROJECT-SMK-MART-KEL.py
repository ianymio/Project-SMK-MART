import os
import sys
import shutil
import getpass
import hashlib
import math
from datetime import datetime, timedelta

# [0] = Kode Barang
# [1] = Nama Barang
# [2] = Kategori
# [3] = Harga Beli
# [4] = Harga Jual 
# [5] = Stok Sekarang 
# [6] = Stok Minimum 

# ==========================================
# 1. KONFIGURASI FOLDER & LOKASI FILE .TXT
# ==========================================
FOLDER_DATA = "data"
FOLDER_STRUK = "struk"
FOLDER_LAPORAN = "laporan"
FOLDER_BACKUP = "backup" 

FILE_PENGGUNA = os.path.join(FOLDER_DATA, "pengguna.txt")
FILE_BARANG = os.path.join(FOLDER_DATA, "barang.txt")
FILE_KATEGORI = os.path.join(FOLDER_DATA, "kategori.txt")
FILE_TRANSAKSI = os.path.join(FOLDER_DATA, "transaksi.txt")
FILE_DETAIL_TRANSAKSI = os.path.join(FOLDER_DATA, "detail_transaksi.txt")
FILE_BARANG_MASUK = os.path.join(FOLDER_DATA, "barang_masuk.txt")
FILE_BARANG_KELUAR = os.path.join(FOLDER_DATA, "barang_keluar.txt")
FILE_LOG_AKTIVITAS = os.path.join(FOLDER_DATA, "log_aktivitas.txt")

user_aktif = None
nama_aktif = None
role_aktif = None


# ==========================================
# 2. TIGA FUNGSI UTAMA PENGELOLA FILE .TXT
# ==========================================
# Membaca isi file .txt menjadi daftar baris (List)
def muat_data(lokasi_file):
    if not os.path.exists(lokasi_file):
        return []
    daftar_data = []
    with open(lokasi_file, "r", encoding="utf-8") as file_txt:
        for baris in file_txt:
            baris_bersih = baris.strip()
            if baris_bersih != "":
                daftar_data.append(baris_bersih.split("|"))
    return daftar_data


# Menyimpan ulang seluruh daftar ke file .txt (dipakai saat Edit atau Hapus)
def simpan_data(lokasi_file, daftar_data):
    with open(lokasi_file, "w", encoding="utf-8") as file_txt:
        for baris in daftar_data:
            baris_teks = "|".join(str(isi) for isi in baris)
            file_txt.write(baris_teks + "\n")

# Menambah 1 baris baru ke bagian paling bawah file .txt
def tambah_data(lokasi_file, baris_baru):
    perlu_newline = False
    if os.path.exists(lokasi_file) and os.path.getsize(lokasi_file) > 0:
        with open(lokasi_file, "rb") as file_cek:
            file_cek.seek(-1, os.SEEK_END)
            if file_cek.read(1) != b"\n":
                perlu_newline = True

    with open(lokasi_file, "a", encoding="utf-8") as file_txt:
        if perlu_newline:
            file_txt.write("\n")
        baris_teks = "|".join(str(isi) for isi in baris_baru)
        file_txt.write(baris_teks + "\n")


# ==========================================
# 3. INISIALISASI FOLDER & DATA AWAL .TXT
# ==========================================
def inisialisasi_sistem():
    for nama_folder in (FOLDER_DATA, FOLDER_STRUK, FOLDER_LAPORAN, FOLDER_BACKUP):
        if not os.path.exists(nama_folder):
            os.makedirs(nama_folder)

    daftar_semua_file = [
        FILE_PENGGUNA,
        FILE_KATEGORI,
        FILE_BARANG,
        FILE_TRANSAKSI,
        FILE_DETAIL_TRANSAKSI,
        FILE_BARANG_MASUK,
        FILE_BARANG_KELUAR,
        FILE_LOG_AKTIVITAS,
    ]

    for lokasi_file_sekarang in daftar_semua_file:
        if not os.path.exists(lokasi_file_sekarang):
            with open(lokasi_file_sekarang, "w", encoding="utf-8") as file_txt:
                pass

    if len(muat_data(FILE_PENGGUNA)) == 0:
        data_pengguna_awal = [
            ["admin", hash_password("admin123"), "Nazwa", "admin", "aktif"],
            ["kasir1", hash_password("kasir123"), "Onit", "kasir", "aktif"],
            ["kasir2", hash_password("kasir123"), "Tasya", "kasir", "nonaktif"],
            ["gudang1", hash_password("gudang123"), "Sukma", "gudang", "aktif"],
        ]
        simpan_data(FILE_PENGGUNA, data_pengguna_awal)


    if len(muat_data(FILE_BARANG)) == 0:
        # [0]=id, [1]=nama, [2]=kategori, [3]=harga beli, [4]=harga jual, [5]=stok, [6]=stok min, [7]=status
        data_barang_awal = [
            ["BRG001", "Beras Premium 5kg", "Sembako", 65000, 72000, 40, 10, "aktif"],
            ["BRG002", "Minyak Goreng 2L", "Sembako", 34000, 38000, 8, 10, "aktif"],
            ["BRG003", "Gula Pasir 1kg", "Sembako", 14500, 16500, 55, 15, "aktif"],
            ["BRG004", "Teh Botol 450ml", "Minuman", 4000, 5500, 100, 30, "aktif"],
            ["BRG005", "Air Mineral 600ml", "Minuman", 2200, 3500, 150, 50, "aktif"],
            ["BRG006", "Kopi Sachet 10s", "Minuman", 10000, 12000, 9, 12, "aktif"],
            ["BRG007", "Deterjen 800g", "Kebersihan", 18000, 21000, 5, 10, "aktif"],
            ["BRG008", "Sabun Mandi", "Kebersihan", 3200, 4500, 80, 20, "aktif"],
            ["BRG009", "Keripik Singkong", "Snack", 7000, 9000, 10, 10, "aktif"],
            ["BRG010", "Mie Instan Goreng", "Makanan", 2800, 3500, 200, 50, "aktif"],
            ["BRG011", "Susu UHT 1L", "Minuman", 15500, 18500, 0, 12, "aktif"],
        ]

        simpan_data(FILE_BARANG, data_barang_awal)

    if len(muat_data(FILE_KATEGORI)) == 0:
        data_kategori_awal = [
            ["KAT001", "Sembako"],
            ["KAT002", "Minuman"],
            ["KAT003", "Kebersihan"],
            ["KAT004", "Snack"],
            ["KAT005", "Makanan"],
        ]
        simpan_data(FILE_KATEGORI, data_kategori_awal)


# ==========================================
# 4. FUNGSI BANTU FORMAT, ID, LOG, & VALIDASI
# ==========================================
def format_rupiah(nominal):
    angka_bulat = int(nominal)
    teks_ribuan = f"{angka_bulat:,}".replace(",", ".")
    return f"Rp {teks_ribuan}"

def hitung_harga_jual_otomatis(harga_beli, persen_untung=0.10, kelipatan=500):
    harga_mentah = harga_beli * (1 + persen_untung)
    return math.ceil(harga_mentah / kelipatan) * kelipatan


def buat_id_otomatis(lokasi_file, awalan, panjang_angka=3):
    daftar_data = muat_data(lokasi_file)
    angka_terbesar = 0
    for baris in daftar_data:
        id_lama = baris[0]
        if id_lama.startswith(awalan):
            bagian_angka = id_lama[len(awalan):]
            if bagian_angka.isdigit():
                nilai_angka = int(bagian_angka)
                if nilai_angka > angka_terbesar:
                    angka_terbesar = nilai_angka
    angka_baru = angka_terbesar + 1
    return f"{awalan}{angka_baru:0{panjang_angka}d}"

def catat_log_aktivitas(keterangan_aksi):
    waktu_sekarang = datetime.now()
    tanggal = waktu_sekarang.strftime("%Y-%m-%d")
    jam = waktu_sekarang.strftime("%H:%M:%S")
    pelaku = user_aktif if user_aktif else "SYSTEM"
    tambah_data(FILE_LOG_AKTIVITAS, [tanggal, jam, pelaku, keterangan_aksi])

def format_tanggal(tanggal_db):
    if len(tanggal_db) == 10 and "-" in tanggal_db:
        bagian = tanggal_db.split("-")
        return f"{bagian[2]}-{bagian[1]}-{bagian[0]}"
    return tanggal_db

def cari_indeks_barang(daftar_barang, kode_barang):
    for nomor_baris, baris_barang in enumerate(daftar_barang):
        if len(baris_barang) >= 7 and baris_barang[0] == kode_barang:
            return nomor_baris
    return -1

def is_barang_aktif(baris_barang):
    if len(baris_barang) >= 8:
        return baris_barang[7].lower() == "aktif"
    return True

def konfirmasi_logout():
    konfirmasi = input("Apakah Anda yakin ingin log out? (y/n): ").strip().lower()
    if konfirmasi == "y":
        catat_log_aktivitas("LOGOUT")
        print("Terima kasih! Log Out dari akun sekarang.")
        return True
    print("Log out dibatalkan. Kembali ke menu utama.")
    return False


def hitung_status_stok(jumlah_stok, batas_minimum):
    if int(jumlah_stok) == 0:
        return "HABIS"
    elif int(jumlah_stok) <= int(batas_minimum):
        return "MINIMUM"
    return "AMAN"

def input_teks_valid(pesan_input, wajib_diisi=True, tanpa_spasi=False, rahasia=False):
    while True:
        if rahasia:
            teks_input = getpass.getpass(pesan_input).strip()
        else:
            teks_input = input(pesan_input).strip()
        if wajib_diisi and teks_input == "":
            print("❌ Input tidak boleh kosong!")
            continue
        if "|" in teks_input:
            print("❌ Input tidak boleh mengandung tanda '|'!")
            continue
        if tanpa_spasi and " " in teks_input:
            print("❌ Input tidak boleh mengandung spasi!")
            continue
        return teks_input

def input_angka(pesan_input, batas_bawah=0):
    while True:
        try:
            teks_input = input(pesan_input).strip()
            if teks_input == "":
                print("❌ Input tidak boleh kosong!")
                continue
            nilai = int(teks_input)
            if nilai < batas_bawah:
                print(f"❌ Angka tidak boleh kurang dari {batas_bawah}!")
                continue
            return nilai
        except ValueError:
            print("❌ Masukkan angka yang valid!")

def hash_password(password_teks):
    return hashlib.sha256(password_teks.encode("utf-8")).hexdigest()

# ==========================================
# 5. SISTEM LOGIN, RINGKASAN, & GANTI PASSWORD
# ==========================================
def login_sistem():
    global user_aktif, nama_aktif, role_aktif
    print("\n================================================")
    print("       SELAMAT DATANG DI APLIKASI SMK MART       ")
    print("================================================")
    print("Silakan login terlebih dahulu.")

    jumlah_percobaan = 0
    batas_percobaan = 3

    while jumlah_percobaan < batas_percobaan:
        username_input = input("Username: ").strip()
        password_input = getpass.getpass("Password: ").strip() 

        daftar_pengguna = muat_data(FILE_PENGGUNA)
        password_hash_input = hash_password(password_input)
        for baris_pengguna in daftar_pengguna:
            if len(baris_pengguna) < 5:
                continue
            if baris_pengguna[0] == username_input and (baris_pengguna[1] == password_hash_input or baris_pengguna[1] == password_input):
                if baris_pengguna[4].lower() != "aktif":
                    print("❌ Akun Anda telah dinonaktifkan. Hubungi Admin!")
                    catat_log_aktivitas(f"LOGIN_DITOLAK_NONAKTIF ({username_input})")
                    return False

                user_aktif = baris_pengguna[0]
                nama_aktif = baris_pengguna[2]
                role_aktif = baris_pengguna[3].lower()
                catat_log_aktivitas("LOGIN")
                print(f"\n✅ Login Berhasil! Selamat datang, {nama_aktif} ({role_aktif}).")
                return True

        jumlah_percobaan += 1
        sisa_percobaan = batas_percobaan - jumlah_percobaan
        if sisa_percobaan > 0:
            print(f"❌ Username atau Password salah! Sisa percobaan: {sisa_percobaan} kali.\n")
        else:
            print("❌ Anda sudah 3 kali salah login. Akses ditolak dan program berhenti!")
            catat_log_aktivitas(f"LOGIN_GAGAL_3X ({username_input})")
            sys.exit()
    return False

def cek_stok_minimum():
    daftar_barang = [brg for brg in muat_data(FILE_BARANG) if len(brg) >= 7 and is_barang_aktif(brg)]
    if len(daftar_barang) == 0:
        print("💡 Sistem: Belum ada data barang aktif terdaftar untuk dipindai.")
        return

    ada_peringatan = False
    for baris_barang in daftar_barang:
        kode_barang = baris_barang[0]
        nama_barang = baris_barang[1]
        stok_sekarang = baris_barang[5]
        stok_minimum = baris_barang[6]

        status_stok = hitung_status_stok(stok_sekarang, stok_minimum)
        if status_stok in ("MINIMUM", "HABIS"):
            label_status = f"[{status_stok}]"
            print(f"{label_status:<9} {kode_barang:<7} {nama_barang:<22} stok {stok_sekarang:<4} min {stok_minimum}")
            ada_peringatan = True

    if not ada_peringatan:
        print("✅ Semua stok barang aktif berada dalam kondisi aman.")


def tampilkan_ringkasan_login():
    waktu_sekarang = datetime.now()
    tanggal_hari_ini_db = waktu_sekarang.strftime("%Y-%m-%d")
    tanggal_hari_ini_tampil = waktu_sekarang.strftime("%d-%m-%Y")

    print("\n===========================================")
    print("    SELAMAT DATANG DI APLIKASI SMK MART")
    print("============================================")
    print(f"Pengguna : {nama_aktif} ({role_aktif})")
    print(f"Tanggal  : {tanggal_hari_ini_tampil}")
    print("------------------------------------------")
    print("RINGKASAN")

    semua_transaksi = muat_data(FILE_TRANSAKSI)
    transaksi_hari_ini = [trx for trx in semua_transaksi if len(trx) >= 7 and trx[1] == tanggal_hari_ini_db]

    if role_aktif in ("admin", "gudang"):
        daftar_barang = [brg for brg in muat_data(FILE_BARANG) if len(brg) >= 7 and is_barang_aktif(brg)]
        jumlah_jenis_barang = len(daftar_barang)
        jumlah_stok_minimum = 0
        jumlah_stok_habis = 0

        for baris_barang in daftar_barang:
            status_sekarang = hitung_status_stok(baris_barang[5], baris_barang[6])
            if status_sekarang == "MINIMUM":
                jumlah_stok_minimum += 1
            elif status_sekarang == "HABIS":
                jumlah_stok_habis += 1

        total_penjualan_hari_ini = sum(int(trx[4]) for trx in transaksi_hari_ini)

        print(f"Jenis barang aktif    : {jumlah_jenis_barang}")
        print(f"Stok minimum / habis  : {jumlah_stok_minimum} / {jumlah_stok_habis}")
        print(f"Penjualan hari ini    : {len(transaksi_hari_ini)} transaksi, {format_rupiah(total_penjualan_hari_ini)}")
        print("------------------------------------------")
        print("PERINGATAN STOK")
        cek_stok_minimum()

    elif role_aktif == "kasir":
        transaksi_kasir_ini = [trx for trx in transaksi_hari_ini if trx[3] == user_aktif]
        total_kasir_ini = sum(int(trx[4]) for trx in transaksi_kasir_ini)
        print(f"Transaksi hari ini    : {len(transaksi_kasir_ini)} transaksi, {format_rupiah(total_kasir_ini)}")

    print("------------------------------------------")


def ganti_password_sendiri():
    print("\n=== GANTI PASSWORD SENDIRI ===")
    pilihan_awal = input("Tekan [Enter] untuk lanjut atau ketik [B]atal: ").strip().lower()
    if pilihan_awal == "b":
        print("❌ Ganti password dibatalkan.")
        return

    daftar_pengguna = muat_data(FILE_PENGGUNA)
    indeks_user = -1
    for i, baris_pengguna in enumerate(daftar_pengguna):
        if len(baris_pengguna) >= 5 and baris_pengguna[0] == user_aktif:
            indeks_user = i
            break

    if indeks_user == -1:
        print("❌ Data pengguna tidak ditemukan!")
        return

    # Verifikasi & sinkronisasi password lama langsung di awal
    password_lama = getpass.getpass("Masukkan Password Lama: ").strip()
    if password_lama == "":
        print("❌ Password lama tidak boleh kosong!")
        return

    password_tersimpan = daftar_pengguna[indeks_user][1]
    if password_tersimpan != hash_password(password_lama) and password_tersimpan != password_lama:
        print("❌ Password lama tidak sesuai! Ganti password dibatalkan.")
        return

    while True:
        password_baru = input_teks_valid("Masukkan Password Baru (min. 6 karakter): ", rahasia=True)
        if len(password_baru) < 6:
            print("❌ Password baru minimal harus 6 karakter!")
            continue
        if password_baru == password_lama:
            print("❌ Password baru tidak boleh sama dengan password lama!")
            continue
        break

    konfirmasi_password = getpass.getpass("Ulangi Password Baru: ").strip()
    if password_baru != konfirmasi_password:
        print("❌ Konfirmasi password baru tidak cocok!")
        return

    daftar_pengguna[indeks_user][1] = hash_password(password_baru)
    simpan_data(FILE_PENGGUNA, daftar_pengguna)
    catat_log_aktivitas("GANTI_PASSWORD_SENDIRI")
    print("✅ Password Anda berhasil diperbarui!")

# ==========================================
# 5B. KELOLA DATA KATEGORI
# ==========================================
def tampilkan_data_kategori():
    print("\n" + "=" * 15 + " DAFTAR KATEGORI BARANG " + "=" * 15)
    daftar_kategori = muat_data(FILE_KATEGORI)
    if len(daftar_kategori) == 0:
        print("Belum ada data kategori tersimpan.")
        return

    daftar_barang = muat_data(FILE_BARANG)
    print(f"{'No.':<5} {'Kode':<10} {'Nama Kategori':<25} {'Jml Barang':<10}")
    print("-" * 55)
    for nomor, kat in enumerate(daftar_kategori, start=1):
        if len(kat) >= 2:
            jml_brg = sum(1 for brg in daftar_barang if len(brg) >= 3 and brg[2].lower() == kat[1].lower())
            print(f"{nomor:<5} {kat[0]:<10} {kat[1]:<25} {jml_brg:<10}")
    print("-" * 55)


def pilih_kategori_barang(pesan="Pilih nomor kategori: "):
    while True:
        daftar_kategori = muat_data(FILE_KATEGORI)
        print("\n--- Pilih Kategori Tersedia ---")
        for nomor, kat in enumerate(daftar_kategori, start=1):
            if len(kat) >= 2:
                print(f"{nomor}. {kat[0]} ({kat[1]})")
        print("0. + Tambah Kategori Baru")

        pilihan = input_angka(pesan, batas_bawah=0)
        if pilihan == 0:
            tambah_data_kategori()
            continue
        elif 1 <= pilihan <= len(daftar_kategori):
            return daftar_kategori[pilihan - 1][1]
        else:
            print(f"❌ Pilihan tidak valid! Masukkan angka 0 sampai {len(daftar_kategori)}.")


def tambah_data_kategori():
    print("\n=== TAMBAH DATA KATEGORI ===")
    pilihan_awal = input("Tekan [Enter] untuk lanjut atau ketik [B]atal: ").strip().lower()
    if pilihan_awal == "b":
        print("❌ Penambahan kategori dibatalkan.")
        return

    daftar_kategori = muat_data(FILE_KATEGORI)
    nama_kategori = input_teks_valid("Masukkan Nama Kategori Baru: ")

    if any(len(kat) >= 2 and kat[1].lower() == nama_kategori.lower() for kat in daftar_kategori):
        print(f"❌ Kategori '{nama_kategori}' sudah ada!")
        return

    kode_kategori_baru = buat_id_otomatis(FILE_KATEGORI, "KAT")
    konfirmasi = input(f"Yakin menambahkan kategori '{nama_kategori}' ({kode_kategori_baru})? (y/n): ").strip().lower()
    if konfirmasi == "y":
        tambah_data(FILE_KATEGORI, [kode_kategori_baru, nama_kategori])
        catat_log_aktivitas(f"TAMBAH_KATEGORI {kode_kategori_baru} ({nama_kategori})")
        print(f"✅ Kategori '{nama_kategori}' berhasil ditambahkan dengan kode {kode_kategori_baru}!")
    else:
        print("❌ Penambahan kategori dibatalkan.")

# ==========================================
# 6. KELOLA DATA BARANG
# ==========================================
def tambah_data_barang():
    print("\n=== Menambahkan Data Barang ===")
    pilihan_awal = input("Tekan [Enter] untuk lanjut atau ketik [B]atal: ").strip().lower()
    if pilihan_awal == "b":
        print("❌ Penambahan barang dibatalkan.")
        return

    nama_barang = input_teks_valid("Masukkan Nama Barang: ")
    kategori_barang = pilih_kategori_barang("Pilih nomor Kategori Barang: ")
    harga_beli = input_angka("Masukkan Harga Beli / Modal (> 0): Rp ", batas_bawah=1)
    saran_harga_jual = hitung_harga_jual_otomatis(harga_beli)
    laba_saran = saran_harga_jual - harga_beli
    persen_aktual = (laba_saran / harga_beli) * 100

    print(
        f"💡 Saran Harga Jual (+10% bulat): {format_rupiah(saran_harga_jual)} "
        f"(Laba: {format_rupiah(laba_saran)} / {persen_aktual:.1f}%)"
    )

    pakai_saran = input("Gunakan saran harga jual ini? (y/n): ").strip().lower()
    if pakai_saran == "y":
        harga_jual = saran_harga_jual
    else:
        harga_jual = input_angka("Masukkan Harga Jual Toko (> 0): Rp ", batas_bawah=1)

    minimal_stok = input_angka("Masukkan Minimal Stok (>= 0): ", batas_bawah=0)

    kode_barang_baru = buat_id_otomatis(FILE_BARANG, "BRG")
    konfirmasi_tambah = input(
        f"Yakin menambahkan '{nama_barang}' [{kategori_barang}] (Beli: {format_rupiah(harga_beli)} | Jual: {format_rupiah(harga_jual)}) dengan kode {kode_barang_baru}? (y/n): "
    ).strip().lower()

    if konfirmasi_tambah == "y":
        baris_barang_baru = [kode_barang_baru, nama_barang, kategori_barang, harga_beli, harga_jual, 0, minimal_stok, "aktif"]
        tambah_data(FILE_BARANG, baris_barang_baru)
        catat_log_aktivitas(f"TAMBAH_BARANG {kode_barang_baru} ({nama_barang})")
        print(f"✅ Data barang '{nama_barang}' berhasil ditambahkan dengan kode {kode_barang_baru}!")
    else:
        print("❌ Penambahan barang dibatalkan.")


def cetak_tabel_barang(daftar_barang_tampil):
    print(f"\n{'Kode':<8} {'Nama Barang':<22} {'Kategori':<13} {'H. Beli':<13} {'H. Jual':<13} {'Stok':<9} {'Min':<8} {'Status':<11}")
    print("-" * 107)
    for baris_barang in daftar_barang_tampil:
        kode_barang = baris_barang[0]
        nama_barang = baris_barang[1]
        kategori_barang = baris_barang[2]
        harga_beli = baris_barang[3]
        harga_jual = baris_barang[4]
        stok_barang = baris_barang[5]
        stok_minimum = baris_barang[6]

        if not is_barang_aktif(baris_barang):
            status_stok = "NONAKTIF"
        else:
            status_stok = hitung_status_stok(stok_barang, stok_minimum)

        harga_beli_teks = format_rupiah(harga_beli)
        harga_jual_teks = format_rupiah(harga_jual)
        stok_teks = f"{stok_barang} pcs"
        minimum_teks = f"{stok_minimum} pcs"

        print(f"{kode_barang:<8} {nama_barang:<22} {kategori_barang:<13} {harga_beli_teks:<13} {harga_jual_teks:<13} {stok_teks:<9} {minimum_teks:<8} {status_stok:<11}")
    print("-" * 107)


def urutkan_dan_tampilkan_barang():
    print("\n" + "=" * 35 + " DAFTAR DATA BARANG " + "=" * 40)
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    if role_aktif == "admin":
        daftar_barang_valid = [baris for baris in daftar_barang if len(baris) >= 7]
    else:
        daftar_barang_valid = [baris for baris in daftar_barang if len(baris) >= 7 and is_barang_aktif(baris)]

    if len(daftar_barang_valid) == 0:
        print("Belum ada data barang aktif di sistem.")
        return

    jumlah_data = len(daftar_barang_valid)
    for indeks_luar in range(jumlah_data):
        for indeks_dalam in range(0, jumlah_data - indeks_luar - 1):
            kunci_sekarang = (
                daftar_barang_valid[indeks_dalam][2].lower(),
                daftar_barang_valid[indeks_dalam][1].lower(),
            )
            kunci_berikutnya = (
                daftar_barang_valid[indeks_dalam + 1][2].lower(),
                daftar_barang_valid[indeks_dalam + 1][1].lower(),
            )
            if kunci_sekarang > kunci_berikutnya:
                daftar_barang_valid[indeks_dalam], daftar_barang_valid[indeks_dalam + 1] = (
                    daftar_barang_valid[indeks_dalam + 1],
                    daftar_barang_valid[indeks_dalam],
                )

    cetak_tabel_barang(daftar_barang_valid)


def searching_data_barang():
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    print("\n" + "=" * 35 + " SEARCHING DATA BARANG " + "=" * 37)
    kata_kunci = input("Masukkan Kode/Nama Barang (kosongkan untuk semua) atau [B]atal: ").strip().lower()
    if kata_kunci == "b":
        print("❌ Pencarian barang dibatalkan.")
        return

    filter_kategori = input("Filter Kategori (kosongkan untuk semua kategori): ").strip().lower()

    hasil_pencarian = []
    for baris_barang in daftar_barang:
        if len(baris_barang) < 7:
            continue
        if role_aktif != "admin" and not is_barang_aktif(baris_barang):
            continue

        kode_barang = baris_barang[0]
        nama_barang = baris_barang[1]
        kategori_barang = baris_barang[2]

        cocok_kata = (kata_kunci in kode_barang.lower()) or (kata_kunci in nama_barang.lower())
        cocok_kategori = (filter_kategori == "") or (filter_kategori in kategori_barang.lower())
        if cocok_kata and cocok_kategori:
            hasil_pencarian.append(baris_barang)

    if len(hasil_pencarian) == 0:
        print("❌ Tidak ditemukan barang yang sesuai.")
        return

    print(f"✅ Ditemukan {len(hasil_pencarian)} barang:")
    cetak_tabel_barang(hasil_pencarian)



def edit_data_barang():
    print("\n=== EDIT DATA BARANG ===")
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    while True:
        print("Navigasi Cepat: [L]ihat Daftar | [B]atal Edit")
        kode_barang_target = input("Masukkan Kode Barang yang ingin diedit: ").strip().upper()
        if kode_barang_target == "L":
            urutkan_dan_tampilkan_barang()
            continue
        if kode_barang_target == "B":
            print("❌ Edit data barang dibatalkan.")
            return
        if kode_barang_target == "":
            print("❌ Kode Barang tidak boleh kosong!")
            continue

        nomor_baris_target = cari_indeks_barang(daftar_barang, kode_barang_target)

        if nomor_baris_target == -1:
            print("❌ Kode Barang tidak ditemukan! Silakan masukkan ulang.")
            continue
        break

    baris_target = daftar_barang[nomor_baris_target]
    nama_baru = baris_target[1]
    kategori_baru = baris_target[2]
    minimal_stok_baru = int(baris_target[6])

    perubahan_terjadi = False

    while True:
        print(f"\n=== Edit Identitas Barang [{kode_barang_target}] ===")
        print(f"1. Nama Barang   : {nama_baru}")
        print(f"2. Kategori      : {kategori_baru}")
        print(f"3. Batas Minimum : {minimal_stok_baru}")
        print("4. Simpan Perubahan")
        print("0. Batal / Keluar")

        pilihan_edit = input("Pilih menu edit (0-4): ").strip()

        if pilihan_edit == "1":
            nama_baru = input_teks_valid("Masukkan Nama Barang Baru: ")
            perubahan_terjadi = True
        elif pilihan_edit == "2":
            kategori_baru = pilih_kategori_barang("Pilih nomor Kategori Baru: ")
            perubahan_terjadi = True
        elif pilihan_edit == "3":
            minimal_stok_baru = input_angka("Masukkan Batas Minimum Baru (>= 0): ", batas_bawah=0)
            perubahan_terjadi = True
        elif pilihan_edit == "4":
            if not perubahan_terjadi:
                print("⚠️ Tidak ada perubahan data yang dibuat.")
                return

            konfirmasi_edit = input("Apakah Anda yakin ingin menyimpan perubahan ini? (y/n): ").strip().lower()
            if konfirmasi_edit == "y":
                daftar_barang[nomor_baris_target][1] = nama_baru
                daftar_barang[nomor_baris_target][2] = kategori_baru
                daftar_barang[nomor_baris_target][6] = minimal_stok_baru
                simpan_data(FILE_BARANG, daftar_barang)
                catat_log_aktivitas(f"EDIT_BARANG {kode_barang_target}")
                print("✅ Data barang berhasil diperbarui!")
            else:
                print("❌ Perubahan data barang dibatalkan.")
            return
        elif pilihan_edit == "0":
            print("❌ Edit data barang dibatalkan.")
            return
        else:
            print("❌ Pilihan tidak valid!")

def hapus_data_barang():
    print("\n=== ARSIPKAN / NONAKTIFKAN DATA BARANG ===")
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    while True:
        print("\nNavigasi Cepat: [L]ihat Daftar | [A]ktifkan Kembali Barang | [B]atal")
        kode_barang_target = input("Masukkan Kode Barang yang ingin dinonaktifkan atau navigasi: ").strip().upper()
        if kode_barang_target == "L":
            urutkan_dan_tampilkan_barang()
            continue
        if kode_barang_target == "B":
            print("❌ Proses dibatalkan.")
            return
        
        if kode_barang_target == "A":
            aktifkan_kembali_barang()
            return

        nomor_baris_target = cari_indeks_barang(daftar_barang, kode_barang_target)
        if nomor_baris_target == -1:
            print("❌ Kode Barang tidak ditemukan! Silakan masukkan ulang.")
            continue

        baris_barang_target = daftar_barang[nomor_baris_target]
        if not is_barang_aktif(baris_barang_target):
            print(f"⚠️ Barang '{baris_barang_target[1]}' ({kode_barang_target}) sudah berstatus NONAKTIF.")
            return
        break

    konfirmasi = input(
        f"Nonaktifkan/arsipkan barang '{baris_barang_target[1]}' ({kode_barang_target})? (y/n): "
    ).strip().lower()
    if konfirmasi != "y":
        print("❌ Proses dibatalkan.")
        return

    if len(daftar_barang[nomor_baris_target]) < 8:
        daftar_barang[nomor_baris_target].append("nonaktif")
    else:
        daftar_barang[nomor_baris_target][7] = "nonaktif"

    simpan_data(FILE_BARANG, daftar_barang)
    catat_log_aktivitas(f"NONAKTIF_BARANG {kode_barang_target} ({baris_barang_target[1]})")
    print(f"✅ Barang '{baris_barang_target[1]}' ({kode_barang_target}) berhasil diarsipkan (NONAKTIF)!")


def aktifkan_kembali_barang():
    daftar_barang = muat_data(FILE_BARANG)
    barang_nonaktif = [brg for brg in daftar_barang if len(brg) >= 8 and not is_barang_aktif(brg)]

    if len(barang_nonaktif) == 0:
        print("💡 Tidak ada barang yang berstatus NONAKTIF.")
        return

    print("\n--- DAFTAR BARANG NONAKTIF (ARSIP) ---")
    cetak_tabel_barang(barang_nonaktif)

    kode_target = input("Masukkan Kode Barang yang ingin diaktifkan kembali (atau [B]atal): ").strip().upper()
    if kode_target == "B":
        print("❌ Proses dibatalkan.")
        return

    nomor_baris = cari_indeks_barang(daftar_barang, kode_target)
    if nomor_baris == -1 or is_barang_aktif(daftar_barang[nomor_baris]):
        print("❌ Kode barang tidak ditemukan di daftar arsip nonaktif!")
        return

    daftar_barang[nomor_baris][7] = "aktif"
    simpan_data(FILE_BARANG, daftar_barang)
    catat_log_aktivitas(f"AKTIFKAN_BARANG {kode_target} ({daftar_barang[nomor_baris][1]})")
    print(f"✅ Barang '{daftar_barang[nomor_baris][1]}' ({kode_target}) berhasil diaktifkan kembali!")

# ==========================================
# 7. ADMINISTRASI GUDANG (MASUK, KELUAR, KARTU STOK)
# ==========================================
def catat_barang_masuk():
    print("\n=== CATAT BARANG MASUK ===")
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    while True:
        print("Navigasi Cepat: [L]ihat Daftar | [B]atal")
        kode_barang_target = input("Masukkan Kode Barang yang masuk: ").strip().upper()
        if kode_barang_target == "L":
            urutkan_dan_tampilkan_barang()
            continue
        if kode_barang_target == "B":
            print("❌ Pencatatan barang masuk dibatalkan.")
            return

        nomor_baris_target = cari_indeks_barang(daftar_barang, kode_barang_target)

        if nomor_baris_target == -1:
            print("❌ Kode Barang tidak ditemukan!")
            continue

        if not is_barang_aktif(daftar_barang[nomor_baris_target]):
            print("❌ Barang ini berstatus NONAKTIF (diarsipkan) dan tidak dapat diproses!")
            continue
        break


    barang_target = daftar_barang[nomor_baris_target]
    nama_barang = barang_target[1]
    harga_beli_lama = int(barang_target[3])
    harga_jual_lama = int(barang_target[4])
    stok_lama = int(barang_target[5])

    laba_lama = harga_jual_lama - harga_beli_lama
    persen_laba_lama = (laba_lama / harga_beli_lama) * 100 if harga_beli_lama > 0 else 0

    print(f"\nInfo Barang : {nama_barang} ({kode_barang_target})")
    print(
        f"Harga Lama  : Beli {format_rupiah(harga_beli_lama)} | "
        f"Jual {format_rupiah(harga_jual_lama)} | "
        f"Laba Lama: {format_rupiah(laba_lama)} ({persen_laba_lama:.1f}%)"
    )

    jumlah_masuk = input_angka("Masukkan Jumlah Barang Masuk (> 0): ", batas_bawah=1)
    nama_pemasok = input_teks_valid("Masukkan Nama Pemasok (Wajib): ")

    harga_beli_baru = harga_beli_lama
    harga_jual_baru = harga_jual_lama

    ubah_harga = input("Apakah ada perubahan harga beli barang? (y/n): ").strip().lower()
    if ubah_harga == "y":
        harga_beli_baru = input_angka(
            f"Masukkan Harga Beli Terbaru (saat ini {format_rupiah(harga_beli_lama)}): Rp ",
            batas_bawah=1,
        )
        harga_jual_baru = hitung_harga_jual_otomatis(harga_beli_baru)

        if harga_beli_baru != harga_beli_lama:
            laba_sementara = harga_jual_baru - harga_beli_baru
            persen_sementara = (laba_sementara / harga_beli_baru) * 100
            print(
                f"💡 Harga jual otomatis diset ke {format_rupiah(harga_jual_baru)} "
                f"(Laba: {format_rupiah(laba_sementara)} / {persen_sementara:.1f}%)."
            )
            ubah_manual = input("Apakah ingin mengubah harga jual secara manual? (y/n): ").strip().lower()
            if ubah_manual == "y":
                while True:
                    harga_manual = input_angka(
                        f"Masukkan Harga Jual Baru (min {format_rupiah(harga_beli_baru)}): Rp ",
                        batas_bawah=1,
                    )
                    if harga_manual < harga_beli_baru:
                        print("⚠️ Harga jual lebih rendah dari harga beli (laba akan minus)!")
                        yakin_rugi = input("Tetap gunakan harga ini? (y/n): ").strip().lower()
                        if yakin_rugi != "y":
                            continue
                    harga_jual_baru = harga_manual
                    break

    laba_baru = harga_jual_baru - harga_beli_baru
    persen_laba_baru = (laba_baru / harga_beli_baru) * 100 if harga_beli_baru > 0 else 0

    id_masuk_baru = buat_id_otomatis(FILE_BARANG_MASUK, "MSK")
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")

    print("\n--- RINGKASAN PERUBAHAN HARGA & LABA ---")
    print(f"Harga Beli : {format_rupiah(harga_beli_lama)} -> {format_rupiah(harga_beli_baru)}")
    print(f"Harga Jual : {format_rupiah(harga_jual_lama)} -> {format_rupiah(harga_jual_baru)}")
    print(f"Laba Lama  : {format_rupiah(laba_lama)} ({persen_laba_lama:.1f}%) / pcs")
    print(f"Laba Baru  : {format_rupiah(laba_baru)} ({persen_laba_baru:.1f}%) / pcs")

    konfirmasi_simpan = input(
        f"\nYakin mencatat masuk {id_masuk_baru}: +{jumlah_masuk} pcs dari '{nama_pemasok}' "
        f"(Beli: {format_rupiah(harga_beli_baru)} | Jual: {format_rupiah(harga_jual_baru)})? (y/n): "
    ).strip().lower()

    if konfirmasi_simpan != "y":
        print("❌ Pencatatan barang masuk dibatalkan.")
        return

    stok_baru = stok_lama + jumlah_masuk
    daftar_barang[nomor_baris_target][3] = harga_beli_baru
    daftar_barang[nomor_baris_target][4] = harga_jual_baru
    daftar_barang[nomor_baris_target][5] = stok_baru
    simpan_data(FILE_BARANG, daftar_barang)

    tambah_data(FILE_BARANG_MASUK, [id_masuk_baru, tanggal_hari_ini, kode_barang_target, jumlah_masuk, nama_pemasok, user_aktif])
    catat_log_aktivitas(
        f"BARANG_MASUK {id_masuk_baru} ({kode_barang_target} +{jumlah_masuk} | Beli:{harga_beli_baru} Jual:{harga_jual_baru})"
    )
    print(f"✅ Barang masuk {id_masuk_baru} berhasil dicatat! Stok '{nama_barang}' sekarang: {stok_baru} pcs.")

def catat_barang_keluar():
    print("\n=== CATAT BARANG KELUAR ===")
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    while True:
        print("Navigasi Cepat: [L]ihat Daftar | [B]atal")
        kode_barang_target = input("Masukkan Kode Barang yang keluar: ").strip().upper()
        if kode_barang_target == "L":
            urutkan_dan_tampilkan_barang()
            continue
        if kode_barang_target == "B":
            print("❌ Pencatatan barang keluar dibatalkan.")
            return

        nomor_baris_target = cari_indeks_barang(daftar_barang, kode_barang_target)

        if nomor_baris_target == -1:
            print("❌ Kode Barang tidak ditemukan!")
            continue

        if not is_barang_aktif(daftar_barang[nomor_baris_target]):
            print("❌ Barang ini berstatus NONAKTIF (diarsipkan) dan tidak dapat diproses!")
            continue
        break

    stok_sekarang = int(daftar_barang[nomor_baris_target][5])
    if stok_sekarang == 0:
        print("❌ Stok barang ini 0 (HABIS), tidak bisa mengeluarkan barang!")
        return

    while True:
        jumlah_keluar = input_angka(f"Masukkan Jumlah Barang Keluar (1 - {stok_sekarang}): ", batas_bawah=1)
        if jumlah_keluar <= stok_sekarang:
            break
        print(f"❌ Gagal! Jumlah keluar ({jumlah_keluar}) melebihi stok yang tersedia ({stok_sekarang}).")

    daftar_alasan = {"1": "RUSAK", "2": "KADALUARSA", "3": "RETUR", "4": "LAINNYA"}
    while True:
        print("Pilih Alasan Barang Keluar:")
        print("1. RUSAK | 2. KADALUARSA | 3. RETUR | 4. LAINNYA")
        pilihan_alasan = input("Pilih alasan (1-4 atau ketik nama alasan): ").strip().upper()
        if pilihan_alasan in daftar_alasan:
            alasan_keluar = daftar_alasan[pilihan_alasan]
            break
        elif pilihan_alasan in daftar_alasan.values():
            alasan_keluar = pilihan_alasan
            break
        print("❌ Pilihan alasan tidak valid!")

    keterangan_tambahan = input_teks_valid("Masukkan Keterangan Tambahan: ", wajib_diisi=False)

    id_keluar_baru = buat_id_otomatis(FILE_BARANG_KELUAR, "KLR")
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")

    konfirmasi_simpan = input(f"Simpan barang keluar {id_keluar_baru} sebanyak {jumlah_keluar} pcs ({alasan_keluar})? (y/n): ").strip().lower()
    if konfirmasi_simpan == "y":
        stok_baru = stok_sekarang - jumlah_keluar
        daftar_barang[nomor_baris_target][5] = stok_baru
        simpan_data(FILE_BARANG, daftar_barang)

        # Format barang_keluar.txt: [0]=id_keluar, [1]=tanggal, [2]=kode_barang, [3]=jumlah, [4]=alasan, [5]=keterangan, [6]=petugas
        tambah_data(FILE_BARANG_KELUAR, [id_keluar_baru, tanggal_hari_ini, kode_barang_target, jumlah_keluar, alasan_keluar, keterangan_tambahan, user_aktif])
        catat_log_aktivitas(f"BARANG_KELUAR {id_keluar_baru} ({kode_barang_target} -{jumlah_keluar} {alasan_keluar})")
        print(f"✅ Barang keluar {id_keluar_baru} berhasil dicatat! Sisa stok: {stok_baru} pcs.")
    else:
        print("❌ Pencatatan barang keluar dibatalkan.")


def lihat_kartu_stok():
    print("\n=== KARTU STOK BARANG ===")
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang.")
        return

    while True:
        print("Navigasi Cepat: [L]ihat Daftar | [B]atal")
        kode_barang_target = input("Masukkan Kode Barang untuk melihat kartu stok: ").strip().upper()
        if kode_barang_target == "L":
            urutkan_dan_tampilkan_barang()
            continue
        if kode_barang_target == "B":
            print("❌ Melihat kartu stok dibatalkan.")
            return

        nomor_baris_target = cari_indeks_barang(daftar_barang, kode_barang_target)
        info_barang = None
        if nomor_baris_target != -1:
            info_barang = daftar_barang[nomor_baris_target]

        if info_barang is None:
            print("❌ Kode Barang tidak ditemukan!")
            continue
        break

    daftar_riwayat = []

    for baris_masuk in muat_data(FILE_BARANG_MASUK):
        if len(baris_masuk) >= 6 and baris_masuk[2] == kode_barang_target:
            daftar_riwayat.append((baris_masuk[1], 1, "MASUK", baris_masuk[0], f"+{baris_masuk[3]}", f"Pemasok: {baris_masuk[4]}"))

    for baris_keluar in muat_data(FILE_BARANG_KELUAR):
        if len(baris_keluar) >= 7 and baris_keluar[2] == kode_barang_target:
            daftar_riwayat.append((baris_keluar[1], 2, "KELUAR", baris_keluar[0], f"-{baris_keluar[3]}", f"{baris_keluar[4]}: {baris_keluar[5]}"))

    peta_tanggal_transaksi = {}
    for baris_transaksi in muat_data(FILE_TRANSAKSI):
        if len(baris_transaksi) >= 2:
            peta_tanggal_transaksi[baris_transaksi[0]] = baris_transaksi[1]

    for baris_detail in muat_data(FILE_DETAIL_TRANSAKSI):
        if len(baris_detail) >= 5 and baris_detail[1] == kode_barang_target:
            tanggal_transaksi = peta_tanggal_transaksi.get(baris_detail[0], "0000-00-00")
            daftar_riwayat.append((tanggal_transaksi, 3, "TERJUAL", baris_detail[0], f"-{baris_detail[4]}", "Penjualan Kasir"))

    daftar_riwayat.sort(key=lambda item: (item[0], item[1], item[3]))

    print(f"\nKartu Stok    : {info_barang[1]} ({kode_barang_target}) | Kategori: {info_barang[2]}")
    print(f"Stok Saat Ini : {info_barang[5]} pcs (Status: {hitung_status_stok(info_barang[5], info_barang[6])})")
    print("-" * 78)
    print(f"{'Tanggal':<12} {'Jenis':<10} {'Ref ID':<10} {'Mutasi':<8} {'Keterangan':<32}")
    print("-" * 78)
    if len(daftar_riwayat) == 0:
        print("Belum ada riwayat mutasi stok untuk barang ini.")
    else:
        for tanggal_db, _, jenis_mutasi, id_referensi, jumlah_mutasi, keterangan_mutasi in daftar_riwayat:
            tanggal_tampil = format_tanggal(tanggal_db)
            print(f"{tanggal_tampil:<12} {jenis_mutasi:<10} {id_referensi:<10} {jumlah_mutasi:<8} {keterangan_mutasi:<32}")
    print("-" * 78)


# ==========================================
# 8. TRANSAKSI PENJUALAN & STRUK
# ==========================================
def tambah_data_transaksi():
    while True:
        print("\n=== TRANSAKSI PENJUALAN KASIR ===")
        daftar_barang = muat_data(FILE_BARANG)
        if len(daftar_barang) == 0:
            print("❌ Belum ada data barang di sistem.")
            return

        keranjang_belanja = []

        while True:
            print("\n--- Input Barang Belanjaan ---")
            print("Navigasi: [L]ihat Daftar | [E]dit Keranjang | [S]elesai / Bayar | [B]atal Transaksi")
            kata_kunci = input("Masukkan Kode atau Nama Barang / Navigasi: ").strip()

            if kata_kunci == "":
                print("❌ Input tidak boleh kosong! Masukkan kode/nama barang atau navigasi.")
                continue

            navigasi = kata_kunci.upper()
            if navigasi == "L":
                urutkan_dan_tampilkan_barang()
                continue

            if navigasi == "B":
                print("❌ Transaksi dibatalkan.")
                return

            if navigasi == "S":
                if len(keranjang_belanja) == 0:
                    print("⚠️ Keranjang belanja masih kosong!")
                    continue
                break

            if navigasi == "E":
                if len(keranjang_belanja) == 0:
                    print("⚠️ Keranjang belanja masih kosong!")
                    continue

                print("\n--- ISI KERANJANG BELANJA ---")
                for nomor_urut, item in enumerate(keranjang_belanja, start=1):
                    print(f"{nomor_urut}. {item['nama']} ({item['kode']}) | {item['qty']} pcs x {format_rupiah(item['harga'])} = {format_rupiah(item['subtotal'])}")
                print("0. Kembali")

                pilih_item = input_angka("Pilih nomor barang yang diubah (0 untuk kembali): ", batas_bawah=0)
                if pilih_item == 0:
                    continue
                if pilih_item > len(keranjang_belanja):
                    print("❌ Nomor urut tidak valid!")
                    continue

                item_ubah = keranjang_belanja[pilih_item - 1]
                stok_fisik = 0
                for baris_barang in daftar_barang:
                    if baris_barang[0] == item_ubah["kode"]:
                        stok_fisik = int(baris_barang[5])
                        break

                jumlah_baru = input_angka(f"Masukkan jumlah baru untuk '{item_ubah['nama']}' (0 untuk hapus, maks {stok_fisik}): ", batas_bawah=0)
                if jumlah_baru == 0:
                    keranjang_belanja.pop(pilih_item - 1)
                    print(f"🗑️ '{item_ubah['nama']}' dihapus dari keranjang.")
                elif jumlah_baru > stok_fisik:
                    print(f"❌ Gagal! Stok fisik hanya tersedia {stok_fisik} pcs.")
                else:
                    item_ubah["qty"] = jumlah_baru
                    item_ubah["subtotal"] = jumlah_baru * item_ubah["harga"]
                    print(f"✅ Jumlah '{item_ubah['nama']}' diperbarui menjadi {jumlah_baru} pcs.")
                continue

            daftar_cocok = []
            for baris_barang in daftar_barang:
                if len(baris_barang) < 7 or not is_barang_aktif(baris_barang):
                    continue
                kode_barang = baris_barang[0]
                nama_barang = baris_barang[1]
                if kata_kunci.upper() == kode_barang.upper() or kata_kunci.lower() in nama_barang.lower():
                    daftar_cocok.append(baris_barang)

            if len(daftar_cocok) == 0:
                print("❌ Barang tidak ditemukan! Coba masukkan kode atau sebagian nama barang yang valid.")
                continue

            barang_terpilih = None
            if len(daftar_cocok) == 1:
                barang_terpilih = daftar_cocok[0]
            else:
                print(f"\nDitemukan {len(daftar_cocok)} barang yang cocok:")
                for nomor_urut, baris_barang in enumerate(daftar_cocok, start=1):
                    print(f"{nomor_urut}. [{baris_barang[0]}] {baris_barang[1]} ({baris_barang[2]}) - {format_rupiah(baris_barang[4])} | Stok: {baris_barang[5]}")
                print("0. Batal pilih")

                pilih_barang = input_angka("Pilih nomor barang: ", batas_bawah=0)
                if pilih_barang == 0:
                    continue
                if pilih_barang > len(daftar_cocok):
                    print("❌ Nomor urut tidak valid!")
                    continue
                barang_terpilih = daftar_cocok[pilih_barang - 1]

            kode_brg, nama_brg, _, _, harga_str, stok_str = barang_terpilih[:6]
            harga_brg = int(harga_str)
            stok_brg = int(stok_str)

            if stok_brg == 0:
                print(f"❌ Stok '{nama_brg}' sudah HABIS (0 pcs), tidak dapat ditransaksikan!")
                continue

            sudah_di_keranjang = sum(item["qty"] for item in keranjang_belanja if item["kode"] == kode_brg)
            sisa_stok = stok_brg - sudah_di_keranjang

            if sisa_stok <= 0:
                print(f"❌ Semua stok '{nama_brg}' ({stok_brg} pcs) sudah masuk ke keranjang belanja!")
                continue


            while True:
                jumlah_beli = input_angka(f"Masukkan jumlah beli '{nama_brg}' (tersedia {sisa_stok} pcs): ", batas_bawah=1)
                if jumlah_beli <= sisa_stok:
                    break
                print(f"❌ Stok tidak mencukupi! Sisa tersedia: {sisa_stok} pcs.")

            sudah_ada = False
            for item in keranjang_belanja:
                if item["kode"] == kode_brg:
                    item["qty"] += jumlah_beli
                    item["subtotal"] = item["qty"] * harga_brg
                    sudah_ada = True
                    break

            if not sudah_ada:
                keranjang_belanja.append({
                    "kode": kode_brg,
                    "nama": nama_brg,
                    "harga": harga_brg,
                    "qty": jumlah_beli,
                    "subtotal": jumlah_beli * harga_brg,
                })

            print(f"✅ '{nama_brg}' ({jumlah_beli} pcs) ditambahkan ke keranjang.")

        while True:
            total_bayar = sum(item["subtotal"] for item in keranjang_belanja)
            print("\n==============================================")
            print("               RINGKASAN BELANJA              ")
            print("==============================================")
            for nomor_urut, item in enumerate(keranjang_belanja, start=1):
                print(f"{nomor_urut}. {item['nama']} ({item['qty']} x {format_rupiah(item['harga'])}) = {format_rupiah(item['subtotal'])}")
            print("----------------------------------------------")
            print(f"TOTAL TAGIHAN : {format_rupiah(total_bayar)}")
            print("==============================================")

            konfirmasi_edit = input("Apakah ingin mengedit/menghapus item sebelum bayar? (y/n): ").strip().lower()
            if konfirmasi_edit == "y":
                print("\n--- EDIT KERANJANG BELANJA ---")
                for nomor_urut, item in enumerate(keranjang_belanja, start=1):
                    print(f"{nomor_urut}. {item['nama']} ({item['kode']}) | {item['qty']} pcs x {format_rupiah(item['harga'])} = {format_rupiah(item['subtotal'])}")
                print("0. Selesai Edit / Lanjut Bayar")

                pilih_item = input_angka("Pilih nomor barang yang diubah (0 untuk lanjut bayar): ", batas_bawah=0)
                if pilih_item == 0:
                    break
                if pilih_item > len(keranjang_belanja):
                    print("❌ Nomor urut tidak valid!")
                    continue

                item_ubah = keranjang_belanja[pilih_item - 1]
                stok_fisik = 0
                for baris_barang in daftar_barang:
                    if baris_barang[0] == item_ubah["kode"]:
                        stok_fisik = int(baris_barang[5])
                        break

                jumlah_baru = input_angka(
                    f"Masukkan jumlah baru untuk '{item_ubah['nama']}' (0 untuk hapus, maks {stok_fisik}): ",
                    batas_bawah=0,
                )
                if jumlah_baru == 0:
                    keranjang_belanja.pop(pilih_item - 1)
                    print(f"🗑️ '{item_ubah['nama']}' dihapus dari keranjang.")
                    if len(keranjang_belanja) == 0:
                        print("⚠️ Keranjang belanja kosong! Transaksi dibatalkan.")
                        return
                elif jumlah_baru > stok_fisik:
                    print(f"❌ Gagal! Stok fisik hanya tersedia {stok_fisik} pcs.")
                else:
                    item_ubah["qty"] = jumlah_baru
                    item_ubah["subtotal"] = jumlah_baru * item_ubah["harga"]
                    print(f"✅ Jumlah '{item_ubah['nama']}' diperbarui menjadi {jumlah_baru} pcs.")
            elif konfirmasi_edit == "n":
                break
            else:
                print("❌ Pilihan tidak valid! Ketik 'y' untuk edit atau 'n' untuk lanjut bayar.")

        while True:
            print("\n=== 💸 METODE PEMBAYARAN 💸 ===")
            print("1. Tunai (Cash)")
            print("2. QRIS (Digital)")
            opsi_bayar = input("Pilih metode (1-2): ").strip()
            if opsi_bayar == "1":
                metode_bayar = "Tunai"
                break
            elif opsi_bayar == "2":
                metode_bayar = "QRIS"
                break
            print("❌ Metode pembayaran tidak valid! Pilih 1 atau 2.")

        if opsi_bayar == "1":
            while True:
                uang_bayar = input_angka(f"Masukkan uang pembayaran (min {format_rupiah(total_bayar)}): Rp ", batas_bawah=0)
                if uang_bayar >= total_bayar:
                    break
                print(f"❌ Uang bayar kurang! Total tagihan adalah {format_rupiah(total_bayar)}.")
            kembalian = uang_bayar - total_bayar
        else:
            uang_bayar = total_bayar
            kembalian = 0
            print(f"Pembayaran QRIS sebesar {format_rupiah(total_bayar)} (Uang Pas).")

        print(f"Kembalian     : {format_rupiah(kembalian)}")
        konfirmasi_checkout = input("Konfirmasi pembayaran dan potong stok? (y/n): ").strip().lower()
        if konfirmasi_checkout != "y":
            print("❌ Transaksi dibatalkan, stok tidak berubah.")
            return

        peringatan_stok_kasir = []
        for item in keranjang_belanja:
            for baris_barang in daftar_barang:
                if baris_barang[0] == item["kode"]:
                    stok_baru = int(baris_barang[5]) - item["qty"]
                    baris_barang[5] = stok_baru
                    status_baru = hitung_status_stok(stok_baru, baris_barang[6])
                    if status_baru in ("MINIMUM", "HABIS"):
                        peringatan_stok_kasir.append(f"'{baris_barang[1]}' ({baris_barang[0]}) -> Status: {status_baru} (Sisa: {stok_baru} pcs)")
                    break

        simpan_data(FILE_BARANG, daftar_barang)

        id_transaksi_baru = buat_id_otomatis(FILE_TRANSAKSI, "TRX")
        waktu_sekarang = datetime.now()
        tanggal_hari_ini = waktu_sekarang.strftime("%Y-%m-%d")
        jam_sekarang = waktu_sekarang.strftime("%H:%M:%S")

        # Format transaksi.txt: [0]=no_trx, [1]=tanggal, [2]=waktu, [3]=kasir, [4]=total, [5]=bayar, [6]=kembalian, [7]=metode
        tambah_data(FILE_TRANSAKSI, [id_transaksi_baru, tanggal_hari_ini, jam_sekarang, user_aktif, total_bayar, uang_bayar, kembalian, metode_bayar])

        # Format detail_transaksi.txt: [0]=no_transaksi, [1]=kode_barang, [2]=nama_barang, [3]=harga, [4]=jumlah, [5]=subtotal
        for item in keranjang_belanja:
            tambah_data(FILE_DETAIL_TRANSAKSI, [id_transaksi_baru, item["kode"], item["nama"], item["harga"], item["qty"], item["subtotal"]])

        catat_log_aktivitas(f"TRANSAKSI {id_transaksi_baru} ({metode_bayar})")
        cetak_struk_digital(id_transaksi_baru)

        if len(peringatan_stok_kasir) > 0:
            print("\n⚠️ INFO STOK UNTUK KASIR (Laporkan ke Gudang/Admin):")
            for info in peringatan_stok_kasir:
                print(f"   - {info}")

        lanjut_transaksi = input("\nBuat transaksi baru lagi? (y/n): ").strip().lower()
        if lanjut_transaksi != "y":
            break

def cetak_struk_digital(id_transaksi):
    daftar_transaksi = muat_data(FILE_TRANSAKSI)
    header_transaksi = None
    for baris_transaksi in daftar_transaksi:
        if len(baris_transaksi) >= 7 and baris_transaksi[0] == id_transaksi:
            header_transaksi = baris_transaksi
            break

    if header_transaksi is None:
        print("❌ Data transaksi tidak ditemukan untuk dicetak!")
        return

    _, tanggal_db, jam_db, username_kasir, total, bayar, kembalian = header_transaksi[:7]
    metode_bayar = header_transaksi[7] if len(header_transaksi) >= 8 else "Tunai"
    tanggal_tampil = format_tanggal(tanggal_db)

    nama_kasir_tampil = username_kasir
    for baris_pengguna in muat_data(FILE_PENGGUNA):
        if len(baris_pengguna) >= 3 and baris_pengguna[0] == username_kasir:
            nama_kasir_tampil = baris_pengguna[2]
            break

    daftar_detail = [detail for detail in muat_data(FILE_DETAIL_TRANSAKSI) if len(detail) >= 6 and detail[0] == id_transaksi]

    baris_struk = [
        "==========================================",
        "          STRUK DIGITAL SMK MART",          
        "==========================================",
        f"No. Transaksi : {id_transaksi}",
        f"Tanggal       : {tanggal_tampil} {jam_db}",
        f"Kasir         : {nama_kasir_tampil}",
        f"Metode Bayar  : {metode_bayar}",
        "------------------------------------------",
    ]

    for detail in daftar_detail:
        _, _, nama_brg, harga_brg, qty_brg, sub_brg = detail
        harga_fmt = f"{int(harga_brg):,}".replace(",", ".")
        sub_fmt = f"{int(sub_brg):,}".replace(",", ".")
        baris_struk.append(f"{nama_brg}")
        kiri_item = f"  {qty_brg} x {harga_fmt}"
        baris_struk.append(kiri_item + sub_fmt.rjust(42 - len(kiri_item)))

    baris_struk.extend([
        "------------------------------------------",
        f"{'TOTAL':<25} {format_rupiah(total):>16}",
        f"{'BAYAR':<25} {format_rupiah(bayar):>16}",
        f"{'KEMBALI':<25} {format_rupiah(kembalian):>16}",
        "==========================================",
        "      Terima kasih telah berbelanja!",
    ])

    teks_struk = "\n".join(baris_struk)
    print("\n" + teks_struk)

    lokasi_struk = os.path.join(FOLDER_STRUK, f"{id_transaksi}.txt")
    with open(lokasi_struk, "w", encoding="utf-8") as file_struk:
        file_struk.write(teks_struk + "\n")
    print(f"📄 Struk berhasil disimpan ke: {lokasi_struk}")


def input_rentang_tanggal():
    while True:
        tanggal_awal_str = input("Masukkan Tanggal Awal (DD-MM-YYYY) atau [B]atal: ").strip()
        if tanggal_awal_str.lower() == "b":
            return None, None, None, None
        tanggal_akhir_str = input("Masukkan Tanggal Akhir (DD-MM-YYYY): ").strip()
        try:
            dt_awal = datetime.strptime(tanggal_awal_str, "%d-%m-%Y")
            dt_akhir = datetime.strptime(tanggal_akhir_str, "%d-%m-%Y")
            if dt_awal > dt_akhir:
                print("❌ Tanggal awal tidak boleh lebih besar dari tanggal akhir!")
                continue
            return dt_awal.strftime("%Y-%m-%d"), dt_akhir.strftime("%Y-%m-%d"), tanggal_awal_str, tanggal_akhir_str
        except ValueError:
            print("❌ Format tanggal salah! Gunakan DD-MM-YYYY (contoh: 17-11-2026).")


def tampilkan_data_transaksi():
    print("\n=== RIWAYAT TRANSAKSI PENJUALAN ===")
    daftar_transaksi = muat_data(FILE_TRANSAKSI)
    if len(daftar_transaksi) == 0:
        print("Belum ada riwayat transaksi penjualan.")
        return

    daftar_detail = muat_data(FILE_DETAIL_TRANSAKSI)
    for baris_transaksi in daftar_transaksi:
        if len(baris_transaksi) < 7:
            continue
        id_tx, tanggal_db, jam_db, kasir, total, _, _ = baris_transaksi[:7]
        metode = baris_transaksi[7] if len(baris_transaksi) >= 8 else "Tunai"
        tanggal_tampil = format_tanggal(tanggal_db)
        print(f"No. Nota : {id_tx} | Tanggal: {tanggal_tampil} {jam_db} | Kasir: {kasir} | Metode: {metode}")
        for detail in daftar_detail:
            if len(detail) >= 6 and detail[0] == id_tx:
                print(f"   - {detail[2]} ({detail[4]} pcs) : {format_rupiah(detail[5])}")
        print(f"Total    : {format_rupiah(total)}")
        print("=" * 65)


def cari_riwayat_transaksi():
    print("\n=== CARI RIWAYAT TRANSAKSI ===")
    daftar_transaksi = muat_data(FILE_TRANSAKSI)
    if len(daftar_transaksi) == 0:
        print("Belum ada riwayat transaksi penjualan.")
        return

    waktu_sekarang = datetime.now()
    hari_ini_tampil = waktu_sekarang.strftime("%d-%m-%Y")
    kemarin_tampil = (waktu_sekarang - timedelta(days=1)).strftime("%d-%m-%Y")

    print(f" 1. Hari Ini ({hari_ini_tampil})")
    print(f" 2. Kemarin  ({kemarin_tampil})")
    print(" 3. Rentang Tanggal (Contoh: 17-11-2026 hingga 20-11-2026)")
    print("Atau ketik 1 tanggal manual (Format: DD-MM-YYYY)")

    pilihan = input("Pilih opsi [1/2/3], ketik tanggal, atau [B]atal: ").strip().lower()
    if pilihan == "b":
        print("❌ Pencarian riwayat dibatalkan.")
        return

    if pilihan == "1":
        tanggal_awal_db = waktu_sekarang.strftime("%Y-%m-%d")
        tanggal_akhir_db = tanggal_awal_db
        label_pencarian = f"Tanggal {hari_ini_tampil}"
    elif pilihan == "2":
        tanggal_awal_db = (waktu_sekarang - timedelta(days=1)).strftime("%Y-%m-%d")
        tanggal_akhir_db = tanggal_awal_db
        label_pencarian = f"Tanggal {kemarin_tampil}"
    elif pilihan == "3":
        tanggal_awal_db, tanggal_akhir_db, label_awal, label_akhir = input_rentang_tanggal()
        if tanggal_awal_db is None:
            print("❌ Pencarian riwayat dibatalkan.")
            return
        label_pencarian = f"Periode {label_awal} s.d. {label_akhir}"
    else:
        try:
            tanggal_awal_db = datetime.strptime(pilihan, "%d-%m-%Y").strftime("%Y-%m-%d")
            tanggal_akhir_db = tanggal_awal_db
            label_pencarian = f"Tanggal {pilihan}"
        except ValueError:
            print("❌ Format tanggal salah! Gunakan format DD-MM-YYYY (contoh: 17-11-2026).")
            return

    daftar_detail = muat_data(FILE_DETAIL_TRANSAKSI)
    ditemukan = False
    total_periode = 0
    jumlah_nota = 0

    print(f"\n=== HASIL PENCARIAN ({label_pencarian}) ===")
    for baris_transaksi in daftar_transaksi:
        if len(baris_transaksi) >= 7 and tanggal_awal_db <= baris_transaksi[1] <= tanggal_akhir_db:
            ditemukan = True
            jumlah_nota += 1
            id_tx, tanggal_db, jam_db, kasir, total, _, _ = baris_transaksi[:7]
            metode = baris_transaksi[7] if len(baris_transaksi) >= 8 else "Tunai"
            total_periode += int(total)
            tanggal_tampil = format_tanggal(tanggal_db)
            print(f"No. Nota : {id_tx} | Tanggal: {tanggal_tampil} {jam_db} | Kasir: {kasir} | Metode: {metode}")

            for detail in daftar_detail:
                if len(detail) >= 6 and detail[0] == id_tx:
                    print(f"   - {detail[2]} ({detail[4]} pcs) : {format_rupiah(detail[5])}")
            print(f"Total    : {format_rupiah(total)}")
            print("=" * 65)

    if not ditemukan:
        print(f"❌ Tidak ditemukan transaksi pada {label_pencarian}.")
    else:
        print(f"Ringkasan: {jumlah_nota} transaksi | Total: {format_rupiah(total_periode)}")

# ==========================================
# 9. LAPORAN PENJUALAN & GUDANG
# ==========================================
def laporan_penjualan():
    print("\n" + "=" * 35 + " LAPORAN PENJUALAN " + "=" * 35)
    tanggal_awal_db, tanggal_akhir_db, label_awal, label_akhir = input_rentang_tanggal()
    if tanggal_awal_db is None:
        return

    semua_transaksi = muat_data(FILE_TRANSAKSI)
    semua_detail = muat_data(FILE_DETAIL_TRANSAKSI)
    semua_barang = muat_data(FILE_BARANG)

    transaksi_terfilter = [trx for trx in semua_transaksi if len(trx) >= 7 and tanggal_awal_db <= trx[1] <= tanggal_akhir_db]

    if len(transaksi_terfilter) == 0:
        print(f"\n⚠️ Tidak ada data penjualan pada periode {label_awal} s.d. {label_akhir}.")
        return

    peta_harga_beli = {}
    for brg in semua_barang:
        if len(brg) >= 7:
            peta_harga_beli[brg[0]] = int(brg[3])

    id_transaksi_valid = {trx[0] for trx in transaksi_terfilter}
    total_pendapatan = sum(int(trx[4]) for trx in transaksi_terfilter)
    jumlah_transaksi = len(transaksi_terfilter)
    total_modal = 0

    rekap_kasir = {}
    for trx in transaksi_terfilter:
        username_kasir = trx[3]
        if username_kasir not in rekap_kasir:
            rekap_kasir[username_kasir] = {"jumlah": 0, "total": 0}
        rekap_kasir[username_kasir]["jumlah"] += 1
        rekap_kasir[username_kasir]["total"] += int(trx[4])

    rekap_barang = {}
    for detail in semua_detail:
        if len(detail) >= 6 and detail[0] in id_transaksi_valid:
            kode_brg = detail[1]
            nama_brg = detail[2]
            harga_jual_satuan = int(detail[3])
            qty_brg = int(detail[4])
            sub_brg = int(detail[5])

            harga_beli_satuan = peta_harga_beli.get(kode_brg, harga_jual_satuan)
            modal_item = harga_beli_satuan * qty_brg
            laba_item = sub_brg - modal_item
            total_modal += modal_item

            if kode_brg not in rekap_barang:
                rekap_barang[kode_brg] = {
                    "kode": kode_brg,
                    "nama": nama_brg,
                    "qty": 0,
                    "omzet": 0,
                    "laba": 0,
                }
            rekap_barang[kode_brg]["qty"] += qty_brg
            rekap_barang[kode_brg]["omzet"] += sub_brg
            rekap_barang[kode_brg]["laba"] += laba_item

    total_profit = total_pendapatan - total_modal
    top_5_barang = sorted(rekap_barang.values(), key=lambda item: (-item["qty"], item["kode"]))[:5]

    baris_laporan = [
        "======================================================================",
        f"LAPORAN PENJUALAN & PROFIT SMK MART ({label_awal} s.d. {label_akhir})",
        "======================================================================",
        f"{'No. Nota':<12} {'Tanggal':<12} {'Jam':<10} {'Kasir':<15} {'Total':<14}",
        "-" * 70,
    ]

    for trx in transaksi_terfilter:
        id_tx, tanggal_db, jam_db, kasir, total, _, _ = trx[:7]
        tanggal_tampil = format_tanggal(tanggal_db)
        baris_laporan.append(f"{id_tx:<12} {tanggal_tampil:<12} {jam_db:<10} {kasir:<15} {format_rupiah(total):<14}")

    baris_laporan.extend([
        "-" * 70,
        f"Jumlah Transaksi     : {jumlah_transaksi} transaksi",
        f"Total Omzet Kotor    : {format_rupiah(total_pendapatan)}",
        f"Total Modal (HPP)    : {format_rupiah(total_modal)}",
        f"Total Profit Bersih  : {format_rupiah(total_profit)}",
        "\n--- TOTAL PENJUALAN PER KASIR ---",
    ])

    for kasir, info in sorted(rekap_kasir.items()):
        baris_laporan.append(f"- {kasir:<15} : {info['jumlah']} transaksi, {format_rupiah(info['total'])}")

    rekap_hari = {}
    for trx in transaksi_terfilter:
        if trx[1] not in rekap_hari:
            rekap_hari[trx[1]] = {"jumlah": 0, "total": 0}
        rekap_hari[trx[1]]["jumlah"] += 1
        rekap_hari[trx[1]]["total"] += int(trx[4])

    baris_laporan.append("\n--- PENJUALAN PER HARI ---")
    for tanggal_hari, info in sorted(rekap_hari.items()):
        tanggal_hari_tampil = format_tanggal(tanggal_hari)
        baris_laporan.append(f"- {tanggal_hari_tampil} : {info['jumlah']} transaksi, {format_rupiah(info['total'])}")

    baris_laporan.append("\n--- 5 BARANG TERLARIS & KONTRIBUSI LABA ---")
    for nomor_urut, item in enumerate(top_5_barang, start=1):
        baris_laporan.append(
            f"{nomor_urut}. [{item['kode']}] {item['nama']} - Terjual: {item['qty']} pcs | Omzet: {format_rupiah(item['omzet'])} | Profit: {format_rupiah(item['laba'])}"
        )
    baris_laporan.append("======================================================================")

    teks_laporan = "\n".join(baris_laporan)
    print("\n" + teks_laporan)

    konfirmasi_simpan = input("\nSimpan laporan penjualan ini ke folder laporan/? (y/n): ").strip().lower()
    if konfirmasi_simpan == "y":
        nama_file = f"laporan_penjualan_{tanggal_awal_db}_sd_{tanggal_akhir_db}.txt"
        lokasi_simpan = os.path.join(FOLDER_LAPORAN, nama_file)
        with open(lokasi_simpan, "w", encoding="utf-8") as file_laporan:
            file_laporan.write(teks_laporan + "\n")
        catat_log_aktivitas(f"SIMPAN_LAPORAN_PENJUALAN ({nama_file})")
        print(f"✅ Laporan berhasil disimpan ke: {lokasi_simpan}")


def laporan_stok_gudang():
    print("\n" + "=" * 32 + " LAPORAN STOK & GUDANG " + "=" * 32)
    tanggal_awal_db, tanggal_akhir_db, label_awal, label_akhir = input_rentang_tanggal()
    if tanggal_awal_db is None:
        return

    daftar_barang = muat_data(FILE_BARANG)
    barang_masuk = [masuk for masuk in muat_data(FILE_BARANG_MASUK) if len(masuk) >= 6 and tanggal_awal_db <= masuk[1] <= tanggal_akhir_db]
    barang_keluar = [keluar for keluar in muat_data(FILE_BARANG_KELUAR) if len(keluar) >= 7 and tanggal_awal_db <= keluar[1] <= tanggal_akhir_db]

    total_masuk = sum(int(masuk[3]) for masuk in barang_masuk)
    total_keluar = sum(int(keluar[3]) for keluar in barang_keluar)

    baris_laporan = [
        "=================================================================================================",
        f"LAPORAN STOK, NILAI PERSEDIAAN & AKTIVITAS GUDANG SMK MART ({label_awal} s.d. {label_akhir})",
        "=================================================================================================",
        "--- DAFTAR STOK & NILAI PERSEDIAAN BARANG SAAT INI (URUT KATEGORI) ---",
        f"{'Kode':<8} {'Nama Barang':<22} {'Kategori':<13} {'Harga':<12} {'Stok':<6} {'Status':<11} {'Nilai Aset':<15}",
        "-" * 99,
    ]

    total_nilai_persediaan = 0
    daftar_barang_valid = [baris for baris in daftar_barang if len(baris) >= 7 and is_barang_aktif(baris)]

    # Urutkan data barang berdasarkan Kategori (indeks 2), lalu Nama Barang (indeks 1)
    daftar_barang_urut = sorted(daftar_barang_valid, key=lambda item: (item[2].lower(), item[1].lower()))

    if len(daftar_barang_urut) == 0:
        baris_laporan.append("Tidak ada data barang.")
    else:
        for baris_barang in daftar_barang_urut:
            kode, nama, kategori, harga_beli, harga_jual, stok, stok_min = baris_barang[:7]

            status = hitung_status_stok(stok, stok_min)
            nilai_barang = int(harga_beli) * int(stok)
            total_nilai_persediaan += nilai_barang
            baris_laporan.append(
                f"{kode:<8} {nama:<22} {kategori:<13} {format_rupiah(harga_beli):<12} {stok:<6} {status:<11} {format_rupiah(nilai_barang):<15}"
            )

    baris_laporan.extend([
        "-" * 99,
        f"TOTAL NILAI PERSEDIAAN GUDANG : {format_rupiah(total_nilai_persediaan)}",
        "-" * 99,
        f"\n--- BARANG MASUK ({len(barang_masuk)} transaksi | Total: {total_masuk} pcs) ---",
    ])
    if len(barang_masuk) == 0:
        baris_laporan.append("Tidak ada data barang masuk pada rentang tanggal ini.")
    else:
        for masuk in barang_masuk:
            tanggal_tampil = format_tanggal(masuk[1])
            baris_laporan.append(f"{masuk[0]} | {tanggal_tampil} | Kode: {masuk[2]} | +{masuk[3]} pcs | Pemasok: {masuk[4]} | Petugas: {masuk[5]}")

    baris_laporan.extend([
        f"\n--- BARANG KELUAR ({len(barang_keluar)} transaksi | Total: {total_keluar} pcs) ---",
    ])
    if len(barang_keluar) == 0:
        baris_laporan.append("Tidak ada data barang keluar pada rentang tanggal ini.")
    else:
        for keluar in barang_keluar:
            tanggal_tampil = format_tanggal(keluar[1])
            baris_laporan.append(f"{keluar[0]} | {tanggal_tampil} | Kode: {keluar[2]} | -{keluar[3]} pcs | {keluar[4]} ({keluar[5]}) | Petugas: {keluar[6]}")

    baris_laporan.append("=================================================================================================")

    teks_laporan = "\n".join(baris_laporan)
    print("\n" + teks_laporan)

    konfirmasi_simpan = input("\nSimpan laporan stok & gudang ini ke folder laporan/? (y/n): ").strip().lower()
    if konfirmasi_simpan == "y":
        nama_file = f"laporan_stok_{tanggal_awal_db}_sd_{tanggal_akhir_db}.txt"
        lokasi_simpan = os.path.join(FOLDER_LAPORAN, nama_file)
        with open(lokasi_simpan, "w", encoding="utf-8") as file_laporan:
            file_laporan.write(teks_laporan + "\n")
        catat_log_aktivitas(f"SIMPAN_LAPORAN_STOK ({nama_file})")
        print(f"✅ Laporan berhasil disimpan ke: {lokasi_simpan}")


# ==========================================
# 10. KELOLA DATA PENGGUNA & LOG AKTIVITAS
# ==========================================
def tambah_data_pengguna():
    print("\n=== MENAMBAHKAN DATA PENGGUNA ===")
    pilihan = input("Tekan [Enter] untuk lanjut atau ketik [B]atal: ").strip().lower()
    if pilihan == "b":
        print("❌ Tambah data pengguna dibatalkan.")
        return

    daftar_pengguna = muat_data(FILE_PENGGUNA)

    while True:
        username = input_teks_valid("Masukkan Username (unik, tanpa spasi): ", tanpa_spasi=True).lower()
        if any(baris[0].lower() == username for baris in daftar_pengguna):
            print("❌ Username sudah digunakan oleh pengguna lain!")
            continue
        break

    nama_lengkap = input_teks_valid("Masukkan Nama Lengkap: ")

    while True:
        password = input_teks_valid("Masukkan Password (min. 6 karakter): ")
        if len(password) < 6:
            print("❌ Password minimal 6 karakter!")
            continue
        break

    while True:
        role = input("Masukkan Role (admin/kasir/gudang): ").strip().lower()
        if role in ("admin", "kasir", "gudang"):
            break
        print("❌ Role tidak valid! Pilih admin, kasir, atau gudang.")

    konfirmasi = input(f"Yakin menambah '{nama_lengkap}' ({username}) sebagai {role}? (y/n): ").strip().lower()
    if konfirmasi == "y":
        tambah_data(FILE_PENGGUNA, [username, hash_password(password), nama_lengkap, role, "aktif"])
        catat_log_aktivitas(f"TAMBAH_USER ({username})")
        print(f"✅ Pengguna '{nama_lengkap}' ({username}) berhasil ditambahkan!")
    else:
        print("❌ Penambahan pengguna dibatalkan.")


def edit_pengguna():
    print("\n=== EDIT DATA & STATUS PENGGUNA ===")
    tampilkan_data_pengguna()
    daftar_pengguna = muat_data(FILE_PENGGUNA)
    if len(daftar_pengguna) == 0:
        return

    username_target = input("Masukkan Username yang ingin diubah (atau [B]atal): ").strip().lower()
    if username_target == "b":
        print("❌ Edit Pengguna dibatalkan. Kembali ke menu.")
        return

    nomor_baris_target = -1
    for nomor_baris, baris_pengguna in enumerate(daftar_pengguna):
        if len(baris_pengguna) >= 5 and baris_pengguna[0].lower() == username_target:
            nomor_baris_target = nomor_baris
            break

    if nomor_baris_target == -1:
        print("❌ Username tidak ditemukan!")
        return

    target = daftar_pengguna[nomor_baris_target]
    print(f"\nData saat ini: {target[2]} ({target[0]}) | Role: {target[3]} | Status: {target[4]}")
    print("1. Ubah Nama Lengkap")
    print("2. Ubah Role")
    print("3. Ubah Status (Aktif / Nonaktif)")
    print("0. Batal")

    pilih = input("Pilih perubahan (0-3): ").strip()
    if pilih == "1":
        nama_baru = input_teks_valid("Masukkan Nama Lengkap Baru: ")
        konfirmasi = input(f"Yakin mengubah nama menjadi '{nama_baru}'? (y/n): ").strip().lower()
        if konfirmasi != "y":
            return
        daftar_pengguna[nomor_baris_target][2] = nama_baru
    elif pilih == "2":
        if target[0] == user_aktif:
            print("❌ Tidak bisa mengubah role akun sendiri yang sedang login!")
            return
        while True:
            role_baru = input("Masukkan Role Baru (admin/kasir/gudang): ").strip().lower()
            if role_baru in ("admin", "kasir", "gudang"):
                break
            print("❌ Role tidak valid!")

        if target[3].lower() == "admin" and target[4].lower() == "aktif" and role_baru != "admin":
            jumlah_admin_aktif = sum(1 for pengguna in daftar_pengguna if len(pengguna) >= 5 and pengguna[3].lower() == "admin" and pengguna[4].lower() == "aktif")
            if jumlah_admin_aktif <= 1:
                print("❌ Gagal! Minimal harus ada 1 akun Admin yang aktif di sistem.")
                return
        konfirmasi = input(f"Yakin mengubah role menjadi '{role_baru}'? (y/n): ").strip().lower()
        if konfirmasi != "y":
            return
        daftar_pengguna[nomor_baris_target][3] = role_baru 
    elif pilih == "3":
        if target[0] == user_aktif:
            print("❌ Tidak bisa menonaktifkan akun sendiri yang sedang login!")
            return
        status_baru = "nonaktif" if target[4].lower() == "aktif" else "aktif"
        if target[3].lower() == "admin" and status_baru == "nonaktif":
            jumlah_admin_aktif = sum(1 for pengguna in daftar_pengguna if len(pengguna) >= 5 and pengguna[3].lower() == "admin" and pengguna[4].lower() == "aktif")
            if jumlah_admin_aktif <= 1:
                print("❌ Gagal! Minimal harus ada 1 akun Admin yang aktif di sistem.")
                return
        konfirmasi = input(f"Yakin mengubah status '{target[0]}' menjadi {status_baru.upper()}? (y/n): ").strip().lower()
        if konfirmasi != "y":
            return
        daftar_pengguna[nomor_baris_target][4] = status_baru
    else:
        return

    simpan_data(FILE_PENGGUNA, daftar_pengguna)
    catat_log_aktivitas(f"EDIT_USER ({target[0]})")
    print("✅ Data pengguna berhasil diperbarui dan disimpan!")


def reset_password_pengguna():
    print("\n=== RESET PASSWORD PENGGUNA (ADMIN) ===")
    tampilkan_data_pengguna()
    daftar_pengguna = muat_data(FILE_PENGGUNA)
    if len(daftar_pengguna) == 0:
        return

    username_target = input("Masukkan Username yang password-nya akan direset (atau [B]atal): ").strip().lower()
    if username_target == "b":
        print("❌ Reset password pengguna dibatalkan.")
        return


    for baris_pengguna in daftar_pengguna:
        if len(baris_pengguna) >= 5 and baris_pengguna[0].lower() == username_target:
            while True:
                password_baru = input_teks_valid(f"Masukkan Password Baru untuk '{baris_pengguna[0]}' (min. 6 karakter): ")
                if len(password_baru) >= 6:
                    break
                print("❌ Password minimal 6 karakter!")
            konfirmasi = input(f"Yakin reset password untuk akun '{baris_pengguna[0]}'? (y/n): ").strip().lower()
            if konfirmasi == "y":
                baris_pengguna[1] = hash_password(password_baru)
                simpan_data(FILE_PENGGUNA, daftar_pengguna)
                catat_log_aktivitas(f"RESET_PASSWORD ({baris_pengguna[0]})")
                print(f"✅ Password akun '{baris_pengguna[0]}' berhasil direset!")
            return

    print("❌ Username tidak ditemukan!")


def tampilkan_data_pengguna():
    print("\n" + "=" * 25 + " DATA PENGGUNA " + "=" * 25)
    daftar_pengguna = muat_data(FILE_PENGGUNA)
    if len(daftar_pengguna) == 0:
        print("Tidak ada data pengguna.")
        return

    print(f"{'Username':<15} {'Nama Lengkap':<25} {'Role':<10} {'Status':<10}")
    print("-" * 65)
    for baris_pengguna in daftar_pengguna:
        if len(baris_pengguna) >= 5:
            print(f"{baris_pengguna[0]:<15} {baris_pengguna[2]:<25} {baris_pengguna[3]:<10} {baris_pengguna[4]:<10}")
    print("-" * 65)


def tampilkan_log_aktivitas():
    print("\n" + "=" * 25 + " 20 LOG AKTIVITAS TERAKHIR " + "=" * 25)
    daftar_log = muat_data(FILE_LOG_AKTIVITAS)
    if len(daftar_log) == 0:
        print("Belum ada log aktivitas tercatat.")
        return

    dua_puluh_terakhir = daftar_log[-20:]
    print(f"{'Tanggal':<12} {'Waktu':<10} {'Username':<15} {'Aktivitas'}")
    print("-" * 77)
    for baris_log in dua_puluh_terakhir:
        if len(baris_log) >= 4:
            tanggal_tampil = format_tanggal(baris_log[0])
            print(f"{tanggal_tampil:<12} {baris_log[1]:<10} {baris_log[2]:<15} {baris_log[3]}")
    print("-" * 77)

# ==========================================
# 10B. BACKUP & RESTORE DATA
# ==========================================
def backup_data():
    print("\n=== BACKUP DATA SISTEM ===")
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    nama_folder_backup = f"backup_{waktu_sekarang}"
    tujuan_backup = os.path.join(FOLDER_BACKUP, nama_folder_backup)

    konfirmasi = input(f"Buat cadangan seluruh folder '{FOLDER_DATA}' ke '{tujuan_backup}'? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("❌ Proses backup dibatalkan.")
        return

    try:
        shutil.copytree(FOLDER_DATA, tujuan_backup)
        catat_log_aktivitas(f"BACKUP_DATA ({nama_folder_backup})")
        print(f"✅ Backup berhasil dibuat di: {tujuan_backup}")
    except Exception as error:
        print(f"❌ Gagal membuat backup: {error}")


def restore_data():
    print("\n=== RESTORE DATA SISTEM ===")
    if not os.path.exists(FOLDER_BACKUP):
        print("❌ Folder backup belum tersedia.")
        return

    daftar_backup = sorted(
        [nama for nama in os.listdir(FOLDER_BACKUP) if os.path.isdir(os.path.join(FOLDER_BACKUP, nama))],
        reverse=True,
    )

    if len(daftar_backup) == 0:
        print("⚠️ Belum ada file cadangan (backup) yang tersimpan.")
        return

    print("Daftar Cadangan Tersedia (Terbaru di atas):")
    for nomor_urut, nama_folder in enumerate(daftar_backup, start=1):
        print(f"{nomor_urut}. {nama_folder}")
    print("0. Batal")

    pilih = input_angka("Pilih nomor backup yang akan dipulihkan: ", batas_bawah=0)
    if pilih == 0:
        print("❌ Proses restore dibatalkan.")
        return
    if pilih > len(daftar_backup):
        print("❌ Nomor pilihan tidak valid!")
        return

    folder_terpilih = daftar_backup[pilih - 1]
    sumber_restore = os.path.join(FOLDER_BACKUP, folder_terpilih)

    print("⚠️ PERINGATAN: Seluruh data saat ini akan ditimpa dengan data dari backup tersebut!")
    konfirmasi = input(f"Yakin ingin memulihkan data dari '{folder_terpilih}'? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("❌ Proses restore dibatalkan.")
        return

    try:
        shutil.copytree(sumber_restore, FOLDER_DATA, dirs_exist_ok=True)
        catat_log_aktivitas(f"RESTORE_DATA ({folder_terpilih})")
        print(f"✅ Data berhasil dipulihkan dari: {folder_terpilih}")
    except Exception as error:
        print(f"❌ Gagal memulihkan data: {error}")

# ==========================================
# 11. PROGRAM UTAMA
# ==========================================
inisialisasi_sistem()

while True:
    while True:
        if login_sistem():
            break

    tampilkan_ringkasan_login()
    logout = False

    while True:
        role = role_aktif.lower()

        if role == "admin":
            print("\n===== DASHBOARD UTAMA (ADMIN) =====")
            print("1. Kelola Pengguna (User Management)")
            print("2. Kelola Data Barang & Stok")
            print("3. Laporan & Riwayat Transaksi")
            print("4. Laporan Stok & Aktivitas Gudang")
            print("5. Lihat Log Aktivitas (20 Terakhir)")
            print("6. Ganti Password Sendiri")
            print("7. Backup & Restore Data")
            print("0. Log Out")
            pilihan = input("Pilih menu (0-7): ").strip()


            if pilihan == "1":
                while True:
                    print("\n--- KELOLA PENGGUNA ---")
                    print("1. Tambah Data Pengguna")
                    print("2. Tampilkan Semua Pengguna")
                    print("3. Edit Data & Status Pengguna")
                    print("4. Reset Password Pengguna")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-4): ").strip()
                    if sub_pil == "1":
                        tambah_data_pengguna()
                    elif sub_pil == "2":
                        tampilkan_data_pengguna()
                    elif sub_pil == "3":
                        edit_pengguna()
                    elif sub_pil == "4":
                        reset_password_pengguna()
                    elif sub_pil == "0":
                        break
                    else:
                        print("Pilihan salah! Silakan masukan pilihan yang valid.")
                        
            elif pilihan == "2":
                while True:
                    print("\n--- KELOLA DATA BARANG, KATEGORI & STOK ---")
                    print("1. Tambah Data Barang")
                    print("2. Tampilkan Daftar Barang & Stok")
                    print("3. Pencarian Barang & Filter Kategori")
                    print("4. Edit Data Barang")
                    print("5. Nonaktifkan / Aktifkan Barang (Arsip)")
                    print("6. Lihat Kartu Stok Barang")
                    print("7. Kelola Kategori")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-7): ").strip()
                    if sub_pil == "1":
                        tambah_data_barang()
                    elif sub_pil == "2":
                        urutkan_dan_tampilkan_barang()
                    elif sub_pil == "3":
                        searching_data_barang()
                    elif sub_pil == "4":
                        edit_data_barang()
                    elif sub_pil == "5":
                        hapus_data_barang()
                    elif sub_pil == "6":
                        lihat_kartu_stok()
                    elif sub_pil == "7":
                        while True:
                            print("\n=== KELOLA KATEGORI ===")
                            print("1. Tampilkan Daftar Kategori")
                            print("2. Tambah Kategori")
                            print("0. Kembali")
                            pil_kat = input("Pilih (0-2): ").strip()
                            if pil_kat == "1":
                                tampilkan_data_kategori()
                            elif pil_kat == "2":
                                tambah_data_kategori()
                            elif pil_kat == "0":
                                break
                            else:
                                print("❌ Pilihan tidak valid!")
                    elif sub_pil == "0":
                        break
                    else:
                        print("Pilihan salah! Silakan masukkan pilihan yang valid.")

            elif pilihan == "3":
                while True:
                    print("\n--- LAPORAN & RIWAYAT TRANSAKSI ---")
                    print("1. Laporan Penjualan")
                    print("2. Tampilkan Riwayat Transaksi")
                    print("3. Cari Riwayat Transaksi Berdasarkan Tanggal")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-3): ").strip()
                    if sub_pil == "1":
                        laporan_penjualan()
                    elif sub_pil == "2":
                        tampilkan_data_transaksi()
                    elif sub_pil == "3":
                        cari_riwayat_transaksi()
                    elif sub_pil == "0":
                        break
                    else:
                        print("Pilihan salah! Silakan masukan pilihan yang valid.")

            elif pilihan == "4":
                laporan_stok_gudang()
            elif pilihan == "5":
                tampilkan_log_aktivitas()
            elif pilihan == "6":
                ganti_password_sendiri()
            elif pilihan == "7":
                while True:
                    print("\n--- BACKUP & RESTORE DATA ---")
                    print("1. Backup Data Sekarang")
                    print("2. Restore Data dari Backup")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-2): ").strip()
                    if sub_pil == "1":
                        backup_data()
                    elif sub_pil == "2":
                        restore_data()
                    elif sub_pil == "0":
                        break
                    else:
                        print("❌ Pilihan tidak valid!")
            elif pilihan == "0":
                if konfirmasi_logout():
                    logout = True
                    break
            else:
                print("Pilihan salah! Silakan masukkan pilihan yang valid.")

        elif role == "kasir":
            print("\n===== MENU UTAMA APLIKASI SMK MART (KASIR) =====")
            print("1. Tampilkan Daftar Barang")
            print("2. Pencarian Barang & Filter Kategori")
            print("3. Transaksi Penjualan")
            print("4. Ganti Password Sendiri")
            print("0. Log Out")
            pilihan = input("Pilih menu (0-4): ").strip()

            if pilihan == "1":
                urutkan_dan_tampilkan_barang()
            elif pilihan == "2":
                searching_data_barang()
            elif pilihan == "3":
                tambah_data_transaksi()
            elif pilihan == "4":
                ganti_password_sendiri()
            elif pilihan == "0":
                if konfirmasi_logout():
                    logout = True
                    break
            else:
                print("Pilihan salah! Silakan masukkan pilihan yang valid.")

        elif role == "gudang":
            print("\n===== MENU UTAMA APLIKASI SMK MART (GUDANG) =====")
            print("1. Catat Barang Masuk")
            print("2. Catat Barang Keluar")
            print("3. Tampilkan Daftar Stok & Status")
            print("4. Pencarian Barang & Filter Kategori")
            print("5. Lihat Kartu Stok Barang")
            print("6. Laporan Stok & Aktivitas Gudang")
            print("7. Ganti Password Sendiri")
            print("0. Log Out")
            pilihan = input("Pilih menu (0-7): ").strip()

            if pilihan == "1":
                catat_barang_masuk()
            elif pilihan == "2":
                catat_barang_keluar()
            elif pilihan == "3":
                urutkan_dan_tampilkan_barang()
            elif pilihan == "4":
                searching_data_barang()
            elif pilihan == "5":
                lihat_kartu_stok()
            elif pilihan == "6":
                laporan_stok_gudang()
            elif pilihan == "7":
                ganti_password_sendiri()
            elif pilihan == "0":
                if konfirmasi_logout():
                    logout = True
                    break
            else:
                print("Pilihan salah! Silakan masukkan pilihan yang valid.")

    if logout:
        user_aktif = None
        nama_aktif = None
        role_aktif = None
        continue
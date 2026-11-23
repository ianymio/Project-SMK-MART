import os
import sys
import getpass
from datetime import datetime, timedelta

# ==========================================
# 1. KONFIGURASI FOLDER & LOKASI FILE .TXT
# ==========================================
FOLDER_DATA = "data"
FOLDER_STRUK = "struk"
FOLDER_LAPORAN = "laporan"

FILE_PENGGUNA = os.path.join(FOLDER_DATA, "pengguna.txt")
FILE_BARANG = os.path.join(FOLDER_DATA, "barang.txt")
FILE_TRANSAKSI = os.path.join(FOLDER_DATA, "transaksi.txt")
FILE_DETAIL_TRANSAKSI = os.path.join(FOLDER_DATA, "detail_transaksi.txt")
FILE_BARANG_MASUK = os.path.join(FOLDER_DATA, "barang_masuk.txt")
FILE_BARANG_KELUAR = os.path.join(FOLDER_DATA, "barang_keluar.txt")
FILE_LOG_AKTIVITAS = os.path.join(FOLDER_DATA, "log_aktivitas.txt")

# Variabel penyimpan akun yang sedang login
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
    with open(lokasi_file, "a", encoding="utf-8") as file_txt:
        baris_teks = "|".join(str(isi) for isi in baris_baru)
        file_txt.write(baris_teks + "\n")


# ==========================================
# 3. INISIALISASI FOLDER & DATA AWAL .TXT
# ==========================================
def inisialisasi_sistem():
    # Buat 3 folder utama jika belum ada
    for nama_folder in (FOLDER_DATA, FOLDER_STRUK, FOLDER_LAPORAN):
        if not os.path.exists(nama_folder):
            os.makedirs(nama_folder)

    # Buat 7 file .txt kosong jika belum ada
    daftar_semua_file = [
        FILE_PENGGUNA,
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

    # Isi pengguna.txt jika masih kosong
    if len(muat_data(FILE_PENGGUNA)) == 0:
        data_pengguna_awal = [
            ["admin", "admin123", "Administrator SMK MART", "admin", "aktif"],
            ["kasir1", "kasir123", "Dewi Lestari", "kasir", "aktif"],
            ["kasir2", "kasir123", "Rian Saputra", "kasir", "aktif"],
            ["kasir3", "kasir123", "Sari Wulandari", "kasir", "nonaktif"],
            ["gudang1", "gudang123", "Budi Santoso", "gudang", "aktif"],
        ]
        simpan_data(FILE_PENGGUNA, data_pengguna_awal)

# ==========================================
# 4. FUNGSI BANTU FORMAT, ID, LOG, & VALIDASI
# ==========================================
def format_rupiah(nominal):
    angka_bulat = int(nominal)
    teks_ribuan = f"{angka_bulat:,}".replace(",", ".")
    return f"Rp {teks_ribuan}"


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
    # Ubah format simpan YYYY-MM-DD menjadi format tampil DD-MM-YYYY
    if len(tanggal_db) == 10 and "-" in tanggal_db:
        bagian = tanggal_db.split("-")
        return f"{bagian[2]}-{bagian[1]}-{bagian[0]}"
    return tanggal_db


def cari_indeks_barang(daftar_barang, kode_barang):
    # Mengembalikan nomor baris barang dengan kode tersebut, atau -1 jika tidak ada
    for nomor_baris, baris_barang in enumerate(daftar_barang):
        if len(baris_barang) >= 6 and baris_barang[0] == kode_barang:
            return nomor_baris
    return -1


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
        for baris_pengguna in daftar_pengguna:
            if len(baris_pengguna) < 5:
                continue
            # Indeks pengguna.txt: [0]=username, [1]=password, [2]=nama_lengkap, [3]=peran, [4]=status
            if baris_pengguna[0] == username_input and baris_pengguna[1] == password_input:
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
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("💡 Sistem: Belum ada data barang terdaftar untuk dipindai.")
        return

    ada_peringatan = False
    for baris_barang in daftar_barang:
        if len(baris_barang) < 6:
            continue
        kode_barang = baris_barang[0]
        nama_barang = baris_barang[1]
        stok_sekarang = baris_barang[4]
        stok_minimum = baris_barang[5]

        status_stok = hitung_status_stok(stok_sekarang, stok_minimum)
        if status_stok in ("MINIMUM", "HABIS"):
            label_status = f"[{status_stok}]"
            print(f"{label_status:<9} {kode_barang:<7} {nama_barang:<22} stok {stok_sekarang:<4} min {stok_minimum}")
            ada_peringatan = True

    if not ada_peringatan:
        print("✅ Semua stok barang berada dalam kondisi aman.")


def tampilkan_ringkasan_login():
    waktu_sekarang = datetime.now()
    tanggal_hari_ini_db = waktu_sekarang.strftime("%Y-%m-%d")
    tanggal_hari_ini_tampil = waktu_sekarang.strftime("%d-%m-%Y")

    print("\n==========================================")
    print("          SMK MART - SISTEM TOKO")
    print("==========================================")
    print(f"Pengguna : {nama_aktif} ({role_aktif})")
    print(f"Tanggal  : {tanggal_hari_ini_tampil}")
    print("------------------------------------------")
    print("RINGKASAN")

    semua_transaksi = muat_data(FILE_TRANSAKSI)
    transaksi_hari_ini = [trx for trx in semua_transaksi if len(trx) >= 7 and trx[1] == tanggal_hari_ini_db]

    if role_aktif in ("admin", "gudang"):
        daftar_barang = muat_data(FILE_BARANG)
        jumlah_jenis_barang = len(daftar_barang)
        jumlah_stok_minimum = 0
        jumlah_stok_habis = 0

        for baris_barang in daftar_barang:
            if len(baris_barang) >= 6:
                status_sekarang = hitung_status_stok(baris_barang[4], baris_barang[5])
                if status_sekarang == "MINIMUM":
                    jumlah_stok_minimum += 1
                elif status_sekarang == "HABIS":
                    jumlah_stok_habis += 1

        total_penjualan_hari_ini = sum(int(trx[4]) for trx in transaksi_hari_ini)

        print(f"Jenis barang          : {jumlah_jenis_barang}")
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
    password_lama = getpass.getpass("Masukkan Password Lama: ").strip()

    while True:
        password_baru = input_teks_valid("Masukkan Password Baru (min. 6 karakter): ", rahasia=True)
        if len(password_baru) < 6:
            print("❌ Password baru minimal harus 6 karakter!")
            continue
        break

    konfirmasi_password = getpass.getpass("Ulangi Password Baru: ").strip()
    if password_baru != konfirmasi_password:
        print("❌ Konfirmasi password baru tidak cocok!")
        return

    daftar_pengguna = muat_data(FILE_PENGGUNA)
    for baris_pengguna in daftar_pengguna:
        if baris_pengguna[0] == user_aktif:
            if baris_pengguna[1] != password_lama:
                print("❌ Password lama yang Anda masukkan salah!")
                return
            baris_pengguna[1] = password_baru
            simpan_data(FILE_PENGGUNA, daftar_pengguna)
            catat_log_aktivitas("GANTI_PASSWORD_SENDIRI")
            print("✅ Password Anda berhasil diperbarui!")
            return


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
    kategori_barang = input_teks_valid("Masukkan Kategori Barang: ")
    harga_jual = input_angka("Masukkan Harga Jual Toko (> 0): Rp ", batas_bawah=1)
    minimal_stok = input_angka("Masukkan Minimal Stok (>= 0): ", batas_bawah=0)

    kode_barang_baru = buat_id_otomatis(FILE_BARANG, "BRG")
    konfirmasi_tambah = input(
        f"Apakah Anda yakin ingin menambahkan barang '{nama_barang}' dengan kode {kode_barang_baru} (stok awal 0)? (y/n): "
    ).strip().lower()

    if konfirmasi_tambah == "y":
        # Format barang.txt: [0]=kode, [1]=nama, [2]=kategori, [3]=harga, [4]=stok, [5]=stok_min
        baris_barang_baru = [kode_barang_baru, nama_barang, kategori_barang, harga_jual, 0, minimal_stok]
        tambah_data(FILE_BARANG, baris_barang_baru)
        catat_log_aktivitas(f"TAMBAH_BARANG {kode_barang_baru} ({nama_barang})")
        print(f"✅ Data barang '{nama_barang}' berhasil ditambahkan dengan kode {kode_barang_baru}!")
    else:
        print("❌ Penambahan barang dibatalkan.")


def cetak_tabel_barang(daftar_barang_tampil):
    print(f"\n{'Kode':<10} {'Nama Barang':<24} {'Kategori':<15} {'Harga':<14} {'Stok':<10} {'Min':<8} {'Status':<10}")
    print("-" * 95)
    for baris_barang in daftar_barang_tampil:
        kode_barang = baris_barang[0]
        nama_barang = baris_barang[1]
        kategori_barang = baris_barang[2]
        harga_barang = baris_barang[3]
        stok_barang = baris_barang[4]
        stok_minimum = baris_barang[5]

        status_stok = hitung_status_stok(stok_barang, stok_minimum)
        harga_teks = format_rupiah(harga_barang)
        stok_teks = f"{stok_barang} pcs"
        minimum_teks = f"{stok_minimum} pcs"
        print(f"{kode_barang:<10} {nama_barang:<24} {kategori_barang:<15} {harga_teks:<14} {stok_teks:<10} {minimum_teks:<8} {status_stok:<10}")
    print("-" * 95)


def urutkan_dan_tampilkan_barang():
    print("\n" + "=" * 35 + " DAFTAR DATA BARANG " + "=" * 40)
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    daftar_barang_valid = [baris for baris in daftar_barang if len(baris) >= 6]

    # Bubble Sort berdasarkan Nama Barang (indeks ke-1)
    jumlah_data = len(daftar_barang_valid)
    for indeks_luar in range(jumlah_data):
        for indeks_dalam in range(0, jumlah_data - indeks_luar - 1):
            if daftar_barang_valid[indeks_dalam][1].lower() > daftar_barang_valid[indeks_dalam + 1][1].lower():
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
        if len(baris_barang) < 6:
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

    data_barang_lama = daftar_barang[nomor_baris_target]
    nama_baru = data_barang_lama[1]
    kategori_baru = data_barang_lama[2]
    harga_baru = int(data_barang_lama[3])
    stok_sekarang = data_barang_lama[4]
    minimal_stok_baru = int(data_barang_lama[5])

    perubahan_terjadi = False

    while True:
        print(f"\n=== Edit Data Barang [{kode_barang_target}] (Stok saat ini: {stok_sekarang} pcs) ===")
        print(f"1. Nama Barang   : {nama_baru}")
        print(f"2. Kategori      : {kategori_baru}")
        print(f"3. Harga Jual    : {format_rupiah(harga_baru)}")
        print(f"4. Batas Minimum : {minimal_stok_baru}")
        print("5. Simpan Perubahan")
        print("0. Batal / Keluar")

        pilihan_edit = input("Pilih menu edit (0-5): ").strip()

        if pilihan_edit == "1":
            nama_baru = input_teks_valid("Masukkan Nama Barang Baru: ")
            perubahan_terjadi = True
        elif pilihan_edit == "2":
            kategori_baru = input_teks_valid("Masukkan Kategori Baru: ")
            perubahan_terjadi = True
        elif pilihan_edit == "3":
            harga_baru = input_angka("Masukkan Harga Jual Baru (> 0): Rp ", batas_bawah=1)
            perubahan_terjadi = True
        elif pilihan_edit == "4":
            minimal_stok_baru = input_angka("Masukkan Batas Minimum Baru (>= 0): ", batas_bawah=0)
            perubahan_terjadi = True
        elif pilihan_edit == "5":
            if not perubahan_terjadi:
                print("⚠️ Tidak ada perubahan data yang dibuat.")
                return

            konfirmasi_edit = input("Apakah Anda yakin ingin menyimpan perubahan ini? (y/n): ").strip().lower()
            if konfirmasi_edit == "y":
                daftar_barang[nomor_baris_target] = [
                    kode_barang_target,
                    nama_baru,
                    kategori_baru,
                    harga_baru,
                    stok_sekarang,
                    minimal_stok_baru,
                ]
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
    print("\n=== HAPUS DATA BARANG ===")
    daftar_barang = muat_data(FILE_BARANG)
    if len(daftar_barang) == 0:
        print("Belum ada data barang di sistem.")
        return

    while True:
        print("\nNavigasi Cepat: [L]ihat Daftar | [B]atal")
        kode_barang_target = input("Masukkan Kode Barang yang ingin dihapus atau masukkan navigasi cepat: ").strip().upper()
        if kode_barang_target == "L":
            urutkan_dan_tampilkan_barang()
            continue
        if kode_barang_target == "B":
            print("❌ Penghapusan barang dibatalkan.")
            return

        nomor_baris_target = cari_indeks_barang(daftar_barang, kode_barang_target)
        baris_barang_target = None
        if nomor_baris_target != -1:
            baris_barang_target = daftar_barang[nomor_baris_target]

        if baris_barang_target is None:
            print("❌ Kode Barang tidak ditemukan! Silakan masukkan ulang.")
            continue
        break

    pernah_terjual = any(len(detail) >= 2 and detail[1] == kode_barang_target for detail in muat_data(FILE_DETAIL_TRANSAKSI))
    pernah_masuk = any(len(masuk) >= 3 and masuk[2] == kode_barang_target for masuk in muat_data(FILE_BARANG_MASUK))
    pernah_keluar = any(len(keluar) >= 3 and keluar[2] == kode_barang_target for keluar in muat_data(FILE_BARANG_KELUAR))

    if pernah_terjual or pernah_masuk or pernah_keluar:
        print(f"❌ Ditolak! Barang '{baris_barang_target[1]}' ({kode_barang_target}) sudah pernah tercatat pada transaksi/barang masuk/keluar sehingga tidak boleh dihapus.")
        return

    konfirmasi_hapus = input(f"Apakah Anda yakin ingin menghapus barang '{baris_barang_target[1]}' dengan kode '{kode_barang_target}'? (y/n): ").strip().lower()
    if konfirmasi_hapus != "y":
        print("❌ Penghapusan barang dibatalkan.")
        return

    daftar_barang_baru = [baris for baris in daftar_barang if baris[0] != kode_barang_target]
    simpan_data(FILE_BARANG, daftar_barang_baru)
    catat_log_aktivitas(f"HAPUS_BARANG {kode_barang_target} ({baris_barang_target[1]})")
    print(f"✅ Data barang dengan kode {kode_barang_target} berhasil dihapus!")


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
        break

    jumlah_masuk = input_angka("Masukkan Jumlah Barang Masuk (> 0): ", batas_bawah=1)
    nama_pemasok = input_teks_valid("Masukkan Nama Pemasok (Wajib): ")

    id_masuk_baru = buat_id_otomatis(FILE_BARANG_MASUK, "MSK")
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")

    konfirmasi_simpan = input(f"Yakin ingin mencatat barang masuk {id_masuk_baru} sebanyak {jumlah_masuk} pcs dari '{nama_pemasok}'? (y/n): ").strip().lower()
    if konfirmasi_simpan != "y":
        print("❌ Pencatatan barang masuk dibatalkan.")
        return

    stok_baru = int(daftar_barang[nomor_baris_target][4]) + jumlah_masuk
    daftar_barang[nomor_baris_target][4] = stok_baru
    simpan_data(FILE_BARANG, daftar_barang)

    # Format barang_masuk.txt: [0]=id_masuk, [1]=tanggal, [2]=kode_barang, [3]=jumlah, [4]=pemasok, [5]=petugas
    tambah_data(FILE_BARANG_MASUK, [id_masuk_baru, tanggal_hari_ini, kode_barang_target, jumlah_masuk, nama_pemasok, user_aktif])
    catat_log_aktivitas(f"BARANG_MASUK {id_masuk_baru} ({kode_barang_target} +{jumlah_masuk})")
    print(f"✅ Barang masuk {id_masuk_baru} berhasil dicatat! Stok '{daftar_barang[nomor_baris_target][1]}' sekarang: {stok_baru} pcs.")


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
        break

    stok_sekarang = int(daftar_barang[nomor_baris_target][4])
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
        daftar_barang[nomor_baris_target][4] = stok_baru
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
    print(f"Stok Saat Ini : {info_barang[4]} pcs (Status: {hitung_status_stok(info_barang[4], info_barang[5])})")
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
                        stok_fisik = int(baris_barang[4])
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
                if len(baris_barang) < 6:
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
                    print(f"{nomor_urut}. [{baris_barang[0]}] {baris_barang[1]} ({baris_barang[2]}) - {format_rupiah(baris_barang[3])} | Stok: {baris_barang[4]}")
                print("0. Batal pilih")

                pilih_barang = input_angka("Pilih nomor barang: ", batas_bawah=0)
                if pilih_barang == 0:
                    continue
                if pilih_barang > len(daftar_cocok):
                    print("❌ Nomor urut tidak valid!")
                    continue
                barang_terpilih = daftar_cocok[pilih_barang - 1]

            kode_brg, nama_brg, _, harga_str, stok_str, _ = barang_terpilih
            harga_brg = int(harga_str)
            stok_brg = int(stok_str)

            sudah_di_keranjang = sum(item["qty"] for item in keranjang_belanja if item["kode"] == kode_brg)
            sisa_stok = stok_brg - sudah_di_keranjang

            if sisa_stok <= 0:
                print(f"❌ Stok '{nama_brg}' habis atau sudah masuk semua ke keranjang!")
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

        total_bayar = sum(item["subtotal"] for item in keranjang_belanja)
        print("\n==============================================")
        print("           RINGKASAN BELANJA AKHIR            ")
        print("==============================================")
        for nomor_urut, item in enumerate(keranjang_belanja, start=1):
            print(f"{nomor_urut}. {item['nama']} ({item['qty']} x {format_rupiah(item['harga'])}) = {format_rupiah(item['subtotal'])}")
        print("----------------------------------------------")
        print(f"TOTAL TAGIHAN : {format_rupiah(total_bayar)}")
        print("==============================================")

        while True:
            print("\n=== 💸 METODE PEMBAYARAN 💸 ===")
            print("1. Tunai (Cash)")
            print("2. QRIS (Digital)")
            opsi_bayar = input("Pilih metode (1-2): ").strip()
            if opsi_bayar in ("1", "2"):
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

        print(f"Kembalian     : {format_rupiah(kembalian)}")
        konfirmasi_checkout = input("Konfirmasi pembayaran dan potong stok? (y/n): ").strip().lower()
        if konfirmasi_checkout != "y":
            print("❌ Transaksi dibatalkan, stok tidak berubah.")
            return

        peringatan_stok_kasir = []
        for item in keranjang_belanja:
            for baris_barang in daftar_barang:
                if baris_barang[0] == item["kode"]:
                    stok_baru = int(baris_barang[4]) - item["qty"]
                    baris_barang[4] = stok_baru
                    status_baru = hitung_status_stok(stok_baru, baris_barang[5])
                    if status_baru in ("MINIMUM", "HABIS"):
                        peringatan_stok_kasir.append(f"'{baris_barang[1]}' ({baris_barang[0]}) -> Status: {status_baru} (Sisa: {stok_baru} pcs)")
                    break

        simpan_data(FILE_BARANG, daftar_barang)

        id_transaksi_baru = buat_id_otomatis(FILE_TRANSAKSI, "TRX")
        waktu_sekarang = datetime.now()
        tanggal_hari_ini = waktu_sekarang.strftime("%Y-%m-%d")
        jam_sekarang = waktu_sekarang.strftime("%H:%M:%S")

        # Format transaksi.txt: [0]=no_transaksi, [1]=tanggal, [2]=waktu, [3]=kasir, [4]=total, [5]=bayar, [6]=kembalian
        tambah_data(FILE_TRANSAKSI, [id_transaksi_baru, tanggal_hari_ini, jam_sekarang, user_aktif, total_bayar, uang_bayar, kembalian])

        # Format detail_transaksi.txt: [0]=no_transaksi, [1]=kode_barang, [2]=nama_barang, [3]=harga, [4]=jumlah, [5]=subtotal
        for item in keranjang_belanja:
            tambah_data(FILE_DETAIL_TRANSAKSI, [id_transaksi_baru, item["kode"], item["nama"], item["harga"], item["qty"], item["subtotal"]])

        catat_log_aktivitas(f"TRANSAKSI {id_transaksi_baru}")
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

    _, tanggal_db, jam_db, username_kasir, total, bayar, kembalian = header_transaksi
    tanggal_tampil = format_tanggal(tanggal_db)

    nama_kasir_tampil = username_kasir
    for baris_pengguna in muat_data(FILE_PENGGUNA):
        if len(baris_pengguna) >= 3 and baris_pengguna[0] == username_kasir:
            nama_kasir_tampil = baris_pengguna[2]
            break

    daftar_detail = [detail for detail in muat_data(FILE_DETAIL_TRANSAKSI) if len(detail) >= 6 and detail[0] == id_transaksi]

    baris_struk = [
        "==========================================",
        "                 SMK MART",
        "==========================================",
        f"No. Transaksi : {id_transaksi}",
        f"Tanggal       : {tanggal_tampil} {jam_db}",
        f"Kasir         : {nama_kasir_tampil}",
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
        id_tx, tanggal_db, jam_db, kasir, total, _, _ = baris_transaksi
        tanggal_tampil = format_tanggal(tanggal_db)
        print(f"No. Nota : {id_tx} | Tanggal: {tanggal_tampil} {jam_db} | Kasir: {kasir}")
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
            id_tx, tanggal_db, jam_db, kasir, total, _, _ = baris_transaksi
            total_periode += int(total)
            tanggal_tampil = format_tanggal(tanggal_db)
            print(f"No. Nota : {id_tx} | Tanggal: {tanggal_tampil} {jam_db} | Kasir: {kasir}")
            for detail in daftar_detail:
                if len(detail) >= 6 and detail[0] == id_tx:
                    print(f"   - {detail[2]} ({detail[4]} pcs) : {format_rupiah(detail[5])}")
            print(f"Total    : {format_rupiah(total)}")
            print("=" * 65)

    if not ditemukan:
        print(f"❌ Tidak ditemukan transaksi pada {label_pencarian}.")
    else:
        print(f"Ringkasan: {jumlah_nota} transaksi | Total: {format_rupiah(total_periode)}")


# LAPORAN PENJUALAN (Rentang tanggal, 5 terlaris urut kode, total per kasir, simpan ke laporan/*.txt)
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

    transaksi_terfilter = [trx for trx in semua_transaksi if len(trx) >= 7 and tanggal_awal_db <= trx[1] <= tanggal_akhir_db]

    if len(transaksi_terfilter) == 0:
        print(f"\n⚠️ Tidak ada data penjualan pada periode {label_awal} s.d. {label_akhir}.")
        return

    id_transaksi_valid = {trx[0] for trx in transaksi_terfilter}
    total_pendapatan = sum(int(trx[4]) for trx in transaksi_terfilter)
    jumlah_transaksi = len(transaksi_terfilter)

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
            qty_brg = int(detail[4])
            sub_brg = int(detail[5])
            if kode_brg not in rekap_barang:
                rekap_barang[kode_brg] = {"kode": kode_brg, "nama": nama_brg, "qty": 0, "omzet": 0}
            rekap_barang[kode_brg]["qty"] += qty_brg
            rekap_barang[kode_brg]["omzet"] += sub_brg

    top_5_barang = sorted(rekap_barang.values(), key=lambda item: (-item["qty"], item["kode"]))[:5]

    baris_laporan = [
        "======================================================================",
        f"LAPORAN PENJUALAN SMK MART ({label_awal} s.d. {label_akhir})",
        "======================================================================",
        f"{'No. Nota':<12} {'Tanggal':<12} {'Jam':<10} {'Kasir':<15} {'Total':<14}",
        "-" * 70,
    ]

    for trx in transaksi_terfilter:
        id_tx, tanggal_db, jam_db, kasir, total, _, _ = trx
        tanggal_tampil = format_tanggal(tanggal_db)
        baris_laporan.append(f"{id_tx:<12} {tanggal_tampil:<12} {jam_db:<10} {kasir:<15} {format_rupiah(total):<14}")

    baris_laporan.extend([
        "-" * 70,
        f"Jumlah Transaksi : {jumlah_transaksi} transaksi",
        f"Total Penjualan  : {format_rupiah(total_pendapatan)}",
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

    baris_laporan.append("\n--- 5 BARANG TERLARIS ---")
    for nomor_urut, item in enumerate(top_5_barang, start=1):
        baris_laporan.append(f"{nomor_urut}. [{item['kode']}] {item['nama']} - Terjual: {item['qty']} pcs ({format_rupiah(item['omzet'])})")
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
        "=================================================================================",
        f"LAPORAN STOK & AKTIVITAS GUDANG SMK MART ({label_awal} s.d. {label_akhir})",
        "=================================================================================",
        "--- DAFTAR STOK BARANG SAAT INI ---",
        f"{'Kode':<10} {'Nama Barang':<24} {'Kategori':<15} {'Stok':<8} {'Min':<8} {'Status':<10}",
        "-" * 81,
    ]

    if len(daftar_barang) == 0:
        baris_laporan.append("Tidak ada data barang.")
    else:
        for baris_barang in daftar_barang:
            kode, nama, kategori, _, stok, stok_min = baris_barang
            status = hitung_status_stok(stok, stok_min)
            baris_laporan.append(f"{kode:<10} {nama:<24} {kategori:<15} {stok:<8} {stok_min:<8} {status:<10}")

    baris_laporan.extend([
        "-" * 81,
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

    baris_laporan.append("=================================================================================")

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
        tambah_data(FILE_PENGGUNA, [username, password, nama_lengkap, role, "aktif"])
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
                baris_pengguna[1] = password_baru
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
            print("0. Log Out")
            pilihan = input("Pilih menu (0-6): ").strip()

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
                    print("\n--- KELOLA DATA BARANG & STOK ---")
                    print("1. Tambah Data Barang")
                    print("2. Tampilkan Daftar Barang & Stok")
                    print("3. Pencarian Barang & Filter Kategori")
                    print("4. Edit Data Barang")
                    print("5. Hapus Data Barang")
                    print("6. Lihat Kartu Stok Barang")
                    print("0. Kembali ke Dashboard Utama")
                    sub_pil = input("Pilih (0-6): ").strip()
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
                    elif sub_pil == "0":
                        break
                    else:
                        print("Pilihan salah! Silakan masukan pilihan yang valid.")

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
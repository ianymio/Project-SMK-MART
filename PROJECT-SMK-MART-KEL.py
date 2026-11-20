
import os
import getpass
from datetime import datetime, timedelta

# 1. KONFIGURASI FOLDER & FILE DATA (.txt)
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

user_aktif = None
nama_aktif = None
role_aktif = None

def baca_file(path_file):
    if not os.path.exists(path_file):
        return []
    hasil = []
    with open(path_file, "r", encoding="utf-8") as f:
        for baris in f:
            baris_bersih = baris.strip()
            if baris_bersih:
                hasil.append(baris_bersih.split("|"))
    return hasil


def tulis_ulang_file(path_file, daftar_baris):
    with open(path_file, "w", encoding="utf-8") as f:
        for baris in daftar_baris:
            baris_teks = "|".join(str(kolom) for kolom in baris)
            f.write(baris_teks + "\n")


def tambah_baris_file(path_file, baris_baru):
    with open(path_file, "a", encoding="utf-8") as f:
        baris_teks = "|".join(str(kolom) for kolom in baris_baru)
        f.write(baris_teks + "\n")


def inisialisasi_sistem():
    for folder in (FOLDER_DATA, FOLDER_STRUK, FOLDER_LAPORAN):
        if not os.path.exists(folder):
            os.makedirs(folder)

    semua_file = [
        FILE_PENGGUNA,
        FILE_BARANG,
        FILE_TRANSAKSI,
        FILE_DETAIL_TRANSAKSI,
        FILE_BARANG_MASUK,
        FILE_BARANG_KELUAR,
        FILE_LOG_AKTIVITAS,
    ]
    for path in semua_file:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                pass

    data_pengguna = baca_file(FILE_PENGGUNA)
    if not data_pengguna:
        akun_default = [
            ["USR001", "admin", "admin123", "Admin", "Admin", "aktif"],
            ["USR002", "kasir", "kasir123", "Kasir", "Kasir", "aktif"],
            ["USR003", "gudang", "gudang123", "Staf Gudang", "Gudang", "aktif"],
        ]
        tulis_ulang_file(FILE_PENGGUNA, akun_default)


def format_rupiah(nominal):
    angka_int = int(nominal)
    teks_ribuan = f"{angka_int:,}".replace(",", ".")
    return f"Rp {teks_ribuan}"


def buat_id_otomatis(path_file, awalan, panjang_angka=3):
    data = baca_file(path_file)
    angka_terbesar = 0
    for baris in data:
        id_lama = baris[0]
        if id_lama.startswith(awalan):
            bagian_angka = id_lama[len(awalan):]
            if bagian_angka.isdigit():
                nilai = int(bagian_angka)
                if nilai > angka_terbesar:
                    angka_terbesar = nilai
    angka_baru = angka_terbesar + 1
    return f"{awalan}{angka_baru:0{panjang_angka}d}"


def catat_log_aktivitas(aksi):
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%Y-%m-%d")
    waktu = sekarang.strftime("%H:%M:%S")
    pengguna = user_aktif if user_aktif else "SYSTEM"
    tambah_baris_file(FILE_LOG_AKTIVITAS, [tanggal, waktu, pengguna, aksi])


inisialisasi_sistem()


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
    global user_aktif, nama_aktif, role_aktif
    print("\n================================================")
    print("       SELAMAT DATANG DI APLIKASI SMK MART       ")
    print("================================================")
    print("Silakan login terlebih dahulu.")

    percobaan = 0
    maks_percobaan = 3

    while percobaan < maks_percobaan:
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

        daftar_pengguna = baca_file(FILE_PENGGUNA)
        for baris in daftar_pengguna:
            if len(baris) < 6:
                continue
            if baris[1] == username and baris[2] == password:
                if baris[5].lower() != "aktif":
                    print("❌ Akun Anda berstatus nonaktif. Akses ditolak! Hubungi Admin.")
                    catat_log_aktivitas(f"LOGIN_DITOLAK_NONAKTIF ({username})")
                    return False

                user_aktif = baris[1]
                nama_aktif = baris[3]
                role_aktif = baris[4]
                catat_log_aktivitas("LOGIN")
                print(f"\n✅ Login Berhasil! Selamat datang, {nama_aktif} ({role_aktif}).")
                return True

        percobaan += 1
        sisa = maks_percobaan - percobaan
        if sisa > 0:
            print(f"❌ Username atau Password salah! Sisa percobaan: {sisa} kali.\n")
        else:
            print("❌ Anda sudah 3 kali salah login. Akses ditolak dan program berhenti!")
            catat_log_aktivitas(f"LOGIN_GAGAL_3X ({username})")
            exit()

    return False

def ganti_password_sendiri():
    print("\n=== GANTI PASSWORD SENDIRI ===")
    password_lama = getpass.getpass("Masukkan Password Lama : ")
    password_baru = getpass.getpass("Masukkan Password Baru (min. 6 karakter): ").strip()

    if len(password_baru) < 6:
        print("❌ Password baru minimal harus 6 karakter!")
        return
    if "|" in password_baru:
        print("❌ Password tidak boleh mengandung karakter '|'!")
        return

    konfirmasi_pw = getpass.getpass("Ulangi Password Baru   : ").strip()
    if password_baru != konfirmasi_pw:
        print("❌ Konfirmasi password baru tidak cocok!")
        return

    daftar_pengguna = baca_file(FILE_PENGGUNA)
    berhasil = False

    for baris in daftar_pengguna:
        if baris[1] == user_aktif:
            if baris[2] != password_lama:
                print("❌ Password lama yang Anda masukkan salah!")
                return
            baris[2] = password_baru
            berhasil = True
            break

    if berhasil:
        tulis_ulang_file(FILE_PENGGUNA, daftar_pengguna)
        catat_log_aktivitas("GANTI_PASSWORD_SENDIRI")
        print("✅ Password Anda berhasil diperbarui!")

# HELPER STATUS STOK (HABIS / MINIMUM / AMAN)
def hitung_status_stok(stok, stok_min):
    if int(stok) == 0:
        return "HABIS"
    elif int(stok) <= int(stok_min):
        return "MINIMUM"
    return "AMAN"

# PENGECEKAN STOK MINIMUM
def cek_stok_minimum():
    ada_peringatan = False
    print("\n============ SISTEM MONITORING STOK ============")
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("💡 Sistem: Belum ada data barang terdaftar untuk dipindai.")
        print("=" * 48)
        return

    for baris in daftar_barang:
        if len(baris) < 6:
            continue
        kode, nama, kategori, harga, stok, stok_min = baris
        status = hitung_status_stok(stok, stok_min)
        if status in ("HABIS", "MINIMUM"):
            print(f"⚠️ [{status}] '{nama}' ({kode}) -> Stok: {stok} | Min: {stok_min}")
            ada_peringatan = True

    if not ada_peringatan:
        print("✅ Semua stok barang berada dalam kondisi AMAN.")
    print("=" * 48)


# TAMBAH DATA BARANG
def tambah_data_barang():
    print("\n=== TAMBAH DATA BARANG ===")
    navigasi = input("Tekan [Enter] untuk lanjut atau ketik [B]atal: ").strip().lower()
    if navigasi == "b":
        print("❌ Penambahan barang dibatalkan.")
        return

    nama_barang = input("Masukkan Nama Barang: ").strip()
    if not nama_barang or "|" in nama_barang:
        print("❌ Nama Barang tidak boleh kosong atau mengandung karakter '|'!")
        return

    kategori = input("Masukkan Kategori Barang: ").strip()
    if not kategori or "|" in kategori:
        print("❌ Kategori tidak boleh kosong atau mengandung karakter '|'!")
        return

    harga = input_angka("Masukkan Harga Jual (> 0): Rp ", minimum=1)
    stok_min = input_angka("Masukkan Batas Stok Minimum (>= 0): ", minimum=0)

    kode_barang = buat_id_otomatis(FILE_BARANG, "BRG")
    konfirmasi = input(f"Simpan barang '{nama_barang}' ({kode_barang}) dengan stok awal 0? (y/n): ").strip().lower()
    if konfirmasi == "y":
        # Format: kode|nama|kategori|harga|stok|stok_min
        baris_baru = [kode_barang, nama_barang, kategori, harga, 0, stok_min]
        tambah_baris_file(FILE_BARANG, baris_baru)
        catat_log_aktivitas(f"TAMBAH_BARANG {kode_barang} ({nama_barang})")
        print(f"✅ Barang '{nama_barang}' berhasil ditambahkan dengan kode {kode_barang} (Stok awal: 0).")
    else:
        print("❌ Penambahan barang dibatalkan.")

# FUNGSI CETAK TABEL BARANG (Dipakai untuk daftar barang, stok, dan pencarian)
def cetak_tabel_barang(daftar_barang, tampilkan_peringatan=False):
    if not daftar_barang:
        print("Belum ada data barang yang sesuai.")
        return

    print(f"\n{'Kode':<10} {'Nama Barang':<24} {'Kategori':<15} {'Harga':<14} {'Stok':<8} {'Min':<8} {'Status':<10}")
    print("-" * 93)
    for baris in daftar_barang:
        kode, nama, kategori, harga, stok, stok_min = baris
        status = hitung_status_stok(stok, stok_min)
        harga_teks = format_rupiah(harga)
        print(f"{kode:<10} {nama:<24} {kategori:<15} {harga_teks:<14} {stok:<8} {stok_min:<8} {status:<10}")
    print("-" * 93)

    if tampilkan_peringatan and role_aktif and role_aktif.lower() in ("admin", "gudang"):
        kritis = [b for b in daftar_barang if hitung_status_stok(b[4], b[5]) in ("HABIS", "MINIMUM")]
        if kritis:
            print(f"⚠️ Peringatan: Terdapat {len(kritis)} barang dengan status MINIMUM atau HABIS!")


# TAMPILKAN & URUTKAN DATA BARANG 
def urutkan_dan_tampilkan_barang():
    print("\n" + "=" * 35 + " DAFTAR BARANG & STOK " + "=" * 36)
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("Belum ada data barang di database.")
        return

    # Bubble Sort berdasarkan Nama Barang
    n = len(daftar_barang)
    for i in range(n):
        for j in range(0, n - i - 1):
            if daftar_barang[j][1].lower() > daftar_barang[j + 1][1].lower():
                daftar_barang[j], daftar_barang[j + 1] = daftar_barang[j + 1], daftar_barang[j]

    cetak_tabel_barang(daftar_barang, tampilkan_peringatan=True)

# SEARCHING DATA BARANG
def searching_data_barang():
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("Belum ada data barang di database.")
        return

    print("\n" + "=" * 35 + " PENCARIAN DATA BARANG " + "=" * 35)
    keyword = input("Masukkan Kode/Nama Barang (kosongkan untuk semua, [B]atal): ").strip().lower()
    if keyword == "b":
        print("❌ Pencarian barang dibatalkan.")
        return

    filter_kat = input("Filter Kategori (kosongkan untuk semua kategori): ").strip().lower()

    hasil = []
    for baris in daftar_barang:
        kode, nama, kategori, harga, stok, stok_min = baris
        cocok_kata = (keyword in kode.lower()) or (keyword in nama.lower())
        cocok_kat = (not filter_kat) or (filter_kat in kategori.lower())
        if cocok_kata and cocok_kat:
            hasil.append(baris)

    print(f"\n✅ Ditemukan {len(hasil)} barang:")
    cetak_tabel_barang(hasil, tampilkan_peringatan=False)

# EDIT DATA BARANG
def edit_data_barang():
    print("\n=== EDIT DATA BARANG ===")
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("Belum ada data barang di database.")
        return

    urutkan_dan_tampilkan_barang()
    kode_target = input("Masukkan Kode Barang yang ingin diedit (atau [B]atal): ").strip().upper()
    if kode_target == "B":
        return

    index_target = -1
    for i, baris in enumerate(daftar_barang):
        if baris == kode_target:
            index_target = i
            break

    if index_target == -1:
        print("❌ Kode Barang tidak ditemukan!")
        return

    target = daftar_barang[index_target]
    nama_baru = target
    kategori_baru = target
    harga_baru = int(target)
    stok_min_baru = int(target)
    berubah = False

    while True:
        print(f"\n=== Edit Barang [{kode_target}] (Stok saat ini: {target}) ===")
        print(f"1. Nama Barang   : {nama_baru}")
        print(f"2. Kategori      : {kategori_baru}")
        print(f"3. Harga Jual    : {format_rupiah(harga_baru)}")
        print(f"4. Stok Minimum  : {stok_min_baru}")
        print("5. Simpan Perubahan")
        print("0. Batal")

        pilihan = input("Pilih menu edit (0-5): ").strip()
        if pilihan == "1":
            inp = input("Masukkan Nama Barang Baru: ").strip()
            if not inp or "|" in inp:
                print("❌ Nama tidak valid!")
            else:
                nama_baru = inp
                berubah = True
        elif pilihan == "2":
            inp = input("Masukkan Kategori Baru: ").strip()
            if not inp or "|" in inp:
                print("❌ Kategori tidak valid!")
            else:
                kategori_baru = inp
                berubah = True
        elif pilihan == "3":
            harga_baru = input_angka("Masukkan Harga Jual Baru (> 0): Rp ", minimum=1)
            berubah = True
        elif pilihan == "4":
            stok_min_baru = input_angka("Masukkan Stok Minimum Baru (>= 0): ", minimum=0)
            berubah = True
        elif pilihan == "5":
            if not berubah:
                print("⚠️ Tidak ada perubahan data.")
                return
            daftar_barang[index_target] = [
                kode_target,
                nama_baru,
                kategori_baru,
                harga_baru,
                target,
                stok_min_baru,
            ]
            tulis_ulang_file(FILE_BARANG, daftar_barang)
            catat_log_aktivitas(f"EDIT_BARANG {kode_target}")
            print("✅ Data barang berhasil diperbarui!")
            return
        elif pilihan == "0":
            print("❌ Edit dibatalkan.")
            return
        else:
            print("❌ Pilihan tidak valid!")

# HAPUS DATA BARANG
def hapus_data_barang():
    print("\n=== HAPUS DATA BARANG ===")
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("Belum ada data barang di database.")
        return

    urutkan_dan_tampilkan_barang()
    kode_target = input("Masukkan Kode Barang yang ingin dihapus (atau [B]atal): ").strip().upper()
    if kode_target == "B":
        return

    target_baris = None
    for baris in daftar_barang:
        if baris[0] == kode_target:
            target_baris = baris
            break

    if not target_baris:
        print("❌ Kode Barang tidak ditemukan!")
        return

    # Cek riwayat di detail_transaksi.txt, barang_masuk.txt, dan barang_keluar.txt
    pernah_terjual = any(len(d) > 2 and d[2] == kode_target for d in baca_file(FILE_DETAIL_TRANSAKSI))
    pernah_masuk = any(len(m) > 3 and m[3] == kode_target for m in baca_file(FILE_BARANG_MASUK))
    pernah_keluar = any(len(k) > 3 and k[3] == kode_target for k in baca_file(FILE_BARANG_KELUAR))

    if pernah_terjual or pernah_masuk or pernah_keluar:
        print(f"❌ Ditolak! Barang '{target_baris[1]}' ({kode_target}) sudah memiliki riwayat transaksi/gudang sehingga tidak dapat dihapus.")
        return

    konfirmasi = input(f"Yakin ingin menghapus permanen barang '{target_baris[1]}' ({kode_target})? (y/n): ").strip().lower()
    if konfirmasi == "y":
        daftar_baru = [b for b in daftar_barang if b[0] != kode_target]
        tulis_ulang_file(FILE_BARANG, daftar_baru)
        catat_log_aktivitas(f"HAPUS_BARANG {kode_target} ({target_baris[1]})")
        print(f"✅ Barang '{target_baris[1]}' ({kode_target}) berhasil dihapus!")
    else:
        print("❌ Penghapusan dibatalkan.")


# CATAT BARANG MASUK
def catat_barang_masuk():
    print("\n=== CATAT BARANG MASUK ===")
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("Belum ada data barang di sistem.")
        return

    urutkan_dan_tampilkan_barang()
    kode_target = input("Masukkan Kode Barang yang masuk (atau [B]atal): ").strip().upper()
    if kode_target == "B":
        return

    index_target = -1
    for i, baris in enumerate(daftar_barang):
        if baris[0] == kode_target:
            index_target = i
            break

    if index_target == -1:
        print("❌ Kode Barang tidak ditemukan!")
        return

    jumlah = input_angka("Masukkan Jumlah Barang Masuk (> 0): ", minimum=1)
    pemasok = input("Masukkan Nama Pemasok (Wajib): ").strip()
    if not pemasok or "|" in pemasok:
        print("❌ Nama pemasok wajib diisi dan tidak boleh mengandung '|'!")
        return

    id_msk = buat_id_otomatis(FILE_BARANG_MASUK, "MSK")
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%Y-%m-%d")
    waktu = sekarang.strftime("%H:%M:%S")

    konfirm = input(f"Simpan barang masuk {id_msk} sebanyak {jumlah} pcs dari '{pemasok}'? (y/n): ").strip().lower()
    if konfirm == "y":
        stok_baru = int(daftar_barang[index_target][4]) + jumlah
        daftar_barang[index_target][4] = stok_baru
        tulis_ulang_file(FILE_BARANG, daftar_barang)

        # Format barang_masuk.txt: id_masuk|tanggal|waktu|kode_barang|jumlah|pemasok|petugas
        tambah_baris_file(FILE_BARANG_MASUK, [id_msk, tanggal, waktu, kode_target, jumlah, pemasok, user_aktif])
        catat_log_aktivitas(f"BARANG_MASUK {id_msk} ({kode_target} +{jumlah})")
        print(f"✅ Barang masuk {id_msk} berhasil dicatat! Stok saat ini: {stok_baru} pcs.")
    else:
        print("❌ Pencatatan barang masuk dibatalkan.")


# CATAT BARANG KELUAR
def catat_barang_keluar():
    print("\n=== CATAT BARANG KELUAR ===")
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("Belum ada data barang di sistem.")
        return

    urutkan_dan_tampilkan_barang()
    kode_target = input("Masukkan Kode Barang yang keluar (atau [B]atal): ").strip().upper()
    if kode_target == "B":
        return

    index_target = -1
    for i, baris in enumerate(daftar_barang):
        if baris[0] == kode_target:
            index_target = i
            break

    if index_target == -1:
        print("❌ Kode Barang tidak ditemukan!")
        return

    stok_sekarang = int(daftar_barang[index_target][4])
    if stok_sekarang == 0:
        print("❌ Stok barang ini 0 (HABIS), tidak bisa mengeluarkan barang!")
        return

    jumlah = input_angka(f"Masukkan Jumlah Barang Keluar (1 - {stok_sekarang}): ", minimum=1)
    if jumlah > stok_sekarang:
        print(f"❌ Gagal! Jumlah keluar ({jumlah}) melebihi stok yang tersedia ({stok_sekarang}).")
        return

    print("Pilih Alasan Barang Keluar:")
    print("1. RUSAK")
    print("2. KADALUARSA")
    print("3. RETUR")
    print("4. LAINNYA")
    pilih_alasan = input("Pilih alasan (1-4): ").strip()
    peta_alasan = {"1": "RUSAK", "2": "KADALUARSA", "3": "RETUR", "4": "LAINNYA"}
    if pilih_alasan not in peta_alasan:
        print("❌ Pilihan alasan tidak valid!")
        return

    alasan = peta_alasan[pilih_alasan]
    keterangan = input("Masukkan Keterangan Tambahan: ").strip()
    if "|" in keterangan:
        print("❌ Keterangan tidak boleh mengandung karakter '|'!")
        return

    id_klr = buat_id_otomatis(FILE_BARANG_KELUAR, "KLR")
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%Y-%m-%d")
    waktu = sekarang.strftime("%H:%M:%S")

    konfirm = input(f"Simpan barang keluar {id_klr} sebanyak {jumlah} pcs ({alasan})? (y/n): ").strip().lower()
    if konfirm == "y":
        stok_baru = stok_sekarang - jumlah
        daftar_barang[index_target][4] = stok_baru
        tulis_ulang_file(FILE_BARANG, daftar_barang)

        # Format barang_keluar.txt: id_keluar|tanggal|waktu|kode_barang|jumlah|alasan|keterangan|petugas
        tambah_baris_file(FILE_BARANG_KELUAR, [id_klr, tanggal, waktu, kode_target, jumlah, alasan, keterangan, user_aktif])
        catat_log_aktivitas(f"BARANG_KELUAR {id_klr} ({kode_target} -{jumlah} {alasan})")
        print(f"✅ Barang keluar {id_klr} berhasil dicatat! Sisa stok: {stok_baru} pcs.")
    else:
        print("❌ Pencatatan barang keluar dibatalkan.")

def lihat_kartu_stok():
    print("\n=== KARTU STOK BARANG ===")
    daftar_barang = baca_file(FILE_BARANG)
    if not daftar_barang:
        print("Belum ada data barang.")
        return

    urutkan_dan_tampilkan_barang()
    kode_target = input("Masukkan Kode Barang untuk melihat kartu stok (atau [B]atal): ").strip().upper()
    if kode_target == "B":
        return

    barang_info = None
    for b in daftar_barang:
        if b[0] == kode_target:
            barang_info = b
            break

    if not barang_info:
        print("❌ Kode Barang tidak ditemukan!")
        return

    riwayat = []

    # 1. Dari barang_masuk.txt
    for m in baca_file(FILE_BARANG_MASUK):
        if len(m) >= 7 and m[3] == kode_target:
            riwayat.append((m[1], m[2], "MASUK", m[0], f"+{m[4]}", f"Pemasok: {m[5]}"))

    # 2. Dari barang_keluar.txt
    for k in baca_file(FILE_BARANG_KELUAR):
        if len(k) >= 8 and k[3] == kode_target:
            riwayat.append((k[1], k[2], "KELUAR", k[0], f"-{k[4]}", f"{k[5]}: {k[6]}"))

    # 3. Dari transaksi.txt & detail_transaksi.txt
    peta_trx = {}
    for t in baca_file(FILE_TRANSAKSI):
        if len(t) >= 3:
            peta_trx[t[0]] = (t[1], t[2])
    for d in baca_file(FILE_DETAIL_TRANSAKSI):
        if len(d) >= 5 and d[2] == kode_target:
            tgl_tx, jam_tx = peta_trx.get(d[1], ("0000-00-00", "00:00:00"))
            riwayat.append((tgl_tx, jam_tx, "TERJUAL", d[1], f"-{d[3]}", "Penjualan Kasir"))

    riwayat.sort(key=lambda x: (x[0], x[1]))

    print(f"\nKartu Stok: {barang_info[1]} ({kode_target}) | Kategori: {barang_info[2]}")
    print(f"Stok Saat Ini: {barang_info[4]} pcs (Status: {hitung_status_stok(barang_info[4], barang_info[5])})")
    print("-" * 82)
    print(f"{'Tanggal':<12} {'Jam':<10} {'Jenis':<10} {'Ref ID':<10} {'Mutasi':<8} {'Keterangan':<25}")
    print("-" * 82)
    if not riwayat:
        print("Belum ada riwayat mutasi stok untuk barang ini.")
    else:
        for tgl, jam, jenis, ref, mutasi, ket in riwayat:
            tgl_tampil = datetime.strptime(tgl, "%Y-%m-%d").strftime("%d-%m-%Y") if "-" in tgl and len(tgl) == 10 else tgl
            print(f"{tgl_tampil:<12} {jam:<10} {jenis:<10} {ref:<10} {mutasi:<8} {ket:<25}")
    print("-" * 82)

# TAMBAH DATA TRANSAKSI
# TAMBAH DATA TRANSAKSI
def tambah_data_transaksi():
    while True:
        print("\n=== TRANSAKSI PENJUALAN KASIR ===")
        daftar_barang = baca_file(FILE_BARANG)
        if not daftar_barang:
            print("❌ Belum ada data barang di sistem.")
            return

        keranjang = []  # Menyimpan dict: kode, nama, harga, qty, subtotal

        while True:
            print("\n--- Input Barang Belanjaan ---")
            print("Navigasi: [L]ihat Daftar | [E]dit Keranjang | [S]elesai / Bayar | [B]atal Transaksi")
            kata_kunci = input("Masukkan Kode atau Nama Barang / Navigasi: ").strip().upper()

            if not kata_kunci:
                continue

            nav = kata_kunci.upper()
            if nav == "L":
                urutkan_dan_tampilkan_barang()
                continue

            if nav == "B":
                print("❌ Transaksi dibatalkan.")
                return

            if nav == "S":
                if not keranjang:
                    print("⚠️ Keranjang belanja masih kosong!")
                    continue
                break

            if nav == "E":
                if not keranjang:
                    print("⚠️ Keranjang belanja masih kosong!")
                    continue

                print("\n--- ISI KERANJANG BELANJA ---")
                for idx, item in enumerate(keranjang, start=1):
                    print(f"{idx}. {item['nama']} ({item['kode']}) | {item['qty']} pcs x {format_rupiah(item['harga'])} = {format_rupiah(item['subtotal'])}")
                print("0. Kembali")

                pilih_item = input_angka("Pilih nomor barang yang diubah (0 untuk kembali): ", minimum=0)
                if pilih_item == 0:
                    continue
                if pilih_item > len(keranjang):
                    print("❌ Nomor urut tidak valid!")
                    continue

                item_ubah = keranjang[pilih_item - 1]
                stok_fisik = 0
                for b in daftar_barang:
                    if b == item_ubah["kode"]:
                        stok_fisik = int(b)
                        break

                qty_baru = input_angka(f"Masukkan jumlah baru untuk '{item_ubah['nama']}' (0 untuk hapus, maks {stok_fisik}): ", minimum=0)
                if qty_baru == 0:
                    keranjang.pop(pilih_item - 1)
                    print(f"🗑️ '{item_ubah['nama']}' dihapus dari keranjang.")
                elif qty_baru > stok_fisik:
                    print(f"❌ Gagal! Stok fisik hanya tersedia {stok_fisik} pcs.")
                else:
                    item_ubah["qty"] = qty_baru
                    item_ubah["subtotal"] = qty_baru * item_ubah["harga"]
                    print(f"✅ Jumlah '{item_ubah['nama']}' diperbarui menjadi {qty_baru} pcs.")
                continue

            cocok = []
            for b in daftar_barang:
                kode_barang = b[0]
                nama_barang = b[1]
                
                if kata_kunci.upper() == kode_barang.upper() or kata_kunci.lower() in nama_barang.lower():
                    cocok.append(b)

            if not cocok:
                print("❌ Barang tidak ditemukan! Coba masukkan kode atau sebagian nama barang yang valid.")
                continue

            barang_terpilih = None
            if len(cocok) == 1:
                # Ambil index ke-0 (satu-satunya barang yang cocok)
                barang_terpilih = cocok[0]
            else:
                print(f"\nDitemukan {len(cocok)} barang yang cocok:")
                for idx, b in enumerate(cocok, start=1):
                    # b[0]=kode, b[1]=nama, b[2]=kategori, b[3]=harga, b[4]=stok
                    print(f"{idx}. [{b[0]}] {b[1]} ({b[2]}) - {format_rupiah(b[3])} | Stok: {b[4]}")
                print("0. Batal pilih")
                
                pilih_brg = input_angka("Pilih nomor barang: ", minimum=0)
                if pilih_brg == 0 or pilih_brg > len(cocok):
                    continue
                barang_terpilih = cocok[pilih_brg - 1]


            kode_brg, nama_brg, _, harga_str, stok_str, _ = barang_terpilih
            harga_brg = int(harga_str)
            stok_brg = int(stok_str)

            sudah_di_keranjang = sum(i["qty"] for i in keranjang if i["kode"] == kode_brg)
            sisa_stok = stok_brg - sudah_di_keranjang

            if sisa_stok <= 0:
                print(f"❌ Stok '{nama_brg}' habis atau sudah masuk semua ke keranjang!")
                continue

            qty = input_angka(f"Masukkan jumlah beli '{nama_brg}' (tersedia {sisa_stok} pcs): ", minimum=1)
            if qty > sisa_stok:
                print(f"❌ Stok tidak mencukupi! Sisa tersedia: {sisa_stok} pcs.")
                continue

            sudah_ada = False
            for item in keranjang:
                if item["kode"] == kode_brg:
                    item["qty"] += qty
                    item["subtotal"] = item["qty"] * harga_brg
                    sudah_ada = True
                    break

            if not sudah_ada:
                keranjang.append({
                    "kode": kode_brg,
                    "nama": nama_brg,
                    "harga": harga_brg,
                    "qty": qty,
                    "subtotal": qty * harga_brg,
                })

            print(f"✅ '{nama_brg}' ({qty} pcs) ditambahkan ke keranjang.")

        # Ringkasan & Konfirmasi Akhir Sebelum Stok Dikurangi
        total_bayar = sum(item["subtotal"] for item in keranjang)
        print("\n==============================================")
        print("           RINGKASAN BELANJA AKHIR            ")
        print("==============================================")
        for idx, item in enumerate(keranjang, start=1):
            print(f"{idx}. {item['nama']} ({item['qty']} x {format_rupiah(item['harga'])}) = {format_rupiah(item['subtotal'])}")
        print("----------------------------------------------")
        print(f"TOTAL TAGIHAN : {format_rupiah(total_bayar)}")
        print("==============================================")

        konfirm_checkout = input("Lanjutkan proses pembayaran dan potong stok? (y/n): ").strip().lower()
        if konfirm_checkout != "y":
            print("❌ Transaksi dibatalkan, stok tidak berubah.")
            return

        print("\n=== 💸 METODE PEMBAYARAN 💸 ===")
        print("1. Tunai (Cash)")
        print("2. QRIS (Digital)")
        opsi_bayar = input("Pilih metode (1-2): ").strip()
        if opsi_bayar not in ("1", "2"):
            print("❌ Metode pembayaran tidak valid! Transaksi dibatalkan.")
            return

        if opsi_bayar == "1":
            metode = "Tunai"
            uang_bayar = input_angka(f"Masukkan uang pembayaran (min {format_rupiah(total_bayar)}): Rp ", minimum=total_bayar)
            kembalian = uang_bayar - total_bayar
        else:
            metode = "QRIS"
            uang_bayar = total_bayar
            kembalian = 0

        # Kurangi stok barang dan simpan ulang barang.txt
        peringatan_stok_kasir = []
        for item in keranjang:
            for b in daftar_barang:
                if b == item["kode"]:
                    stok_baru = int(b) - item["qty"]
                    b = stok_baru
                    status_baru = hitung_status_stok(stok_baru, b)
                    if status_baru in ("MINIMUM", "HABIS"):
                        peringatan_stok_kasir.append(f"'{b}' ({b}) -> Status: {status_baru} (Sisa: {stok_baru} pcs)")
                    break

        tulis_ulang_file(FILE_BARANG, daftar_barang)

        # Buat ID TRX001 dan simpan ke transaksi.txt & detail_transaksi.txt
        id_trx = buat_id_otomatis(FILE_TRANSAKSI, "TRX")
        sekarang = datetime.now()
        tanggal = sekarang.strftime("%Y-%m-%d")
        waktu = sekarang.strftime("%H:%M:%S")
        kasir_tampil = nama_aktif if nama_aktif else user_aktif

        tambah_baris_file(FILE_TRANSAKSI, [id_trx, tanggal, waktu, kasir_tampil, total_bayar, metode, uang_bayar, kembalian])

        # Format detail_transaksi.txt: id_transaksi|kode_barang|nama_barang|harga|jumlah|subtotal
        for item in keranjang:
            tambah_baris_file(FILE_DETAIL_TRANSAKSI, [id_trx, item["kode"], item["nama"], item["harga"], item["qty"], item["subtotal"]])

        catat_log_aktivitas(f"TRANSAKSI {id_trx} ({format_rupiah(total_bayar)})")
        cetak_struk_digital(id_trx)

        # Pesan stok minimum untuk kasir setelah transaksi selesai
        if peringatan_stok_kasir:
            print("\n⚠️ INFO STOK UNTUK KASIR (Laporkan ke Gudang/Admin):")
            for info in peringatan_stok_kasir:
                print(f"   - {info}")

        lanjut = input("\nBuat transaksi baru lagi? (y/n): ").strip().lower()
        if lanjut != "y":
            break


# CETAK STRUK KE LAYAR & SIMPAN KE FOLDER struk/TRX001.txt
def cetak_struk_digital(id_transaksi):
    daftar_trx = baca_file(FILE_TRANSAKSI)
    header = None
    for t in daftar_trx:
        if len(t) >= 8 and t[0] == id_transaksi:
            header = t
            break

    if not header:
        print("❌ Data transaksi tidak ditemukan untuk dicetak!")
        return

    _, tgl, jam, kasir, total, metode, bayar, kembalian = header
    tgl_tampil = datetime.strptime(tgl, "%Y-%m-%d").strftime("%d-%m-%Y") if "-" in tgl and len(tgl) == 10 else tgl

    daftar_detail = [d for d in baca_file(FILE_DETAIL_TRANSAKSI) if len(d) >= 6 and d[0] == id_transaksi]

    baris_struk = [
        "========================================",
        "          STRUK DIGITAL SMK MART        ",
        "========================================",
        f"No. Nota    : {id_transaksi}",
        f"Tanggal     : {tgl_tampil} {jam}",
        f"Kasir       : {kasir}",
        "----------------------------------------",
    ]

    for d in daftar_detail:
        _, _, nama_brg, harga_brg, qty_brg, sub_brg = d
        baris_struk.append(f"{nama_brg}")
        baris_struk.append(f"  {qty_brg} pcs x {format_rupiah(harga_brg)} = {format_rupiah(sub_brg)}")

    baris_struk.extend([
        "----------------------------------------",
        f"Metode      : {metode}",
        f"TOTAL BAYAR : {format_rupiah(total)}",
        f"UANG BAYAR  : {format_rupiah(bayar)}",
        f"KEMBALIAN   : {format_rupiah(kembalian)}",
        "========================================",
        "    Terima Kasih Atas Kunjungan Anda    ",
        "========================================",
    ])

    teks_struk = "\n".join(baris_struk)
    print("\n" + teks_struk)

    path_struk = os.path.join(FOLDER_STRUK, f"{id_transaksi}.txt")
    with open(path_struk, "w", encoding="utf-8") as f:
        f.write(teks_struk + "\n")
    print(f"📄 Struk berhasil disimpan ke: {path_struk}")


# TAMPILKAN SEMUA RIWAYAT TRANSAKSI
def tampilkan_data_transaksi():
    print("\n=== RIWAYAT TRANSAKSI PENJUALAN ===")
    daftar_trx = baca_file(FILE_TRANSAKSI)
    if not daftar_trx:
        print("Belum ada riwayat transaksi penjualan.")
        return

    daftar_detail = baca_file(FILE_DETAIL_TRANSAKSI)
    for t in daftar_trx:
        if len(t) < 8:
            continue
        id_tx, tgl, jam, kasir, total, metode, _, _ = t
        tgl_tampil = datetime.strptime(tgl, "%Y-%m-%d").strftime("%d-%m-%Y") if "-" in tgl and len(tgl) == 10 else tgl
        print(f"No. Nota : {id_tx} | Tanggal: {tgl_tampil} {jam} | Kasir: {kasir} | Metode: {metode}")
        for d in daftar_detail:
            if len(d) >= 6 and d[0] == id_tx:
                print(f"   - {d[2]} ({d[4]} pcs) : {format_rupiah(d[5])}")
        print(f"Total    : {format_rupiah(total)}")
        print("=" * 65)


# CARI RIWAYAT TRANSAKSI BERDASARKAN TANGGAL (Input DD-MM-YYYY, pencocokan YYYY-MM-DD)
def cari_riwayat_transaksi():
    print("\n=== CARI RIWAYAT TRANSAKSI ===")
    daftar_trx = baca_file(FILE_TRANSAKSI)
    if not daftar_trx:
        print("Belum ada riwayat transaksi penjualan.")
        return

    sekarang = datetime.now()
    hari_ini_tampil = sekarang.strftime("%d-%m-%Y")
    kemarin_tampil = (sekarang - timedelta(days=1)).strftime("%d-%m-%Y")

    print(f"[1] Hari Ini ({hari_ini_tampil})")
    print(f"[2] Kemarin  ({kemarin_tampil})")
    print("Atau ketik tanggal manual (Format: DD-MM-YYYY)")

    pilihan = input("Pilih opsi [1/2], ketik tanggal, atau [B]atal: ").strip().lower()
    if pilihan == "b":
        print("❌ Pencarian riwayat dibatalkan.")
        return

    if pilihan == "1":
        target_tgl_db = sekarang.strftime("%Y-%m-%d")
        label_tgl = hari_ini_tampil
    elif pilihan == "2":
        target_tgl_db = (sekarang - timedelta(days=1)).strftime("%Y-%m-%d")
        label_tgl = kemarin_tampil
    else:
        try:
            dt = datetime.strptime(pilihan, "%d-%m-%Y")
            target_tgl_db = dt.strftime("%Y-%m-%d")
            label_tgl = pilihan
        except ValueError:
            print("❌ Format tanggal salah! Gunakan format DD-MM-YYYY (contoh: 19-11-2026).")
            return

    daftar_detail = baca_file(FILE_DETAIL_TRANSAKSI)
    ditemukan = False
    print(f"\n=== HASIL PENCARIAN TANGGAL {label_tgl} ===")
    for t in daftar_trx:
        if len(t) >= 8 and t[1] == target_tgl_db:
            ditemukan = True
            id_tx, _, jam, kasir, total, metode, _, _ = t
            print(f"No. Nota : {id_tx} | Jam: {jam} | Kasir: {kasir} | Metode: {metode}")
            for d in daftar_detail:
                if len(d) >= 6 and d[0] == id_tx:
                    print(f"   - {d[2]} ({d[4]} pcs) : {format_rupiah(d[5])}")
            print(f"Total    : {format_rupiah(total)}")
            print("=" * 65)

    if not ditemukan:
        print(f"❌ Tidak ditemukan transaksi pada tanggal '{label_tgl}'.")

def input_rentang_tanggal():
    while True:
        tgl_awal_str = input("Masukkan Tanggal Awal (DD-MM-YYYY) atau [B]atal: ").strip()
        if tgl_awal_str.lower() == "b":
            return None, None, None, None
        tgl_akhir_str = input("Masukkan Tanggal Akhir (DD-MM-YYYY): ").strip()
        try:
            dt_awal = datetime.strptime(tgl_awal_str, "%d-%m-%Y")
            dt_akhir = datetime.strptime(tgl_akhir_str, "%d-%m-%Y")
            if dt_awal > dt_akhir:
                print("❌ Tanggal awal tidak boleh lebih besar dari tanggal akhir!")
                continue
            return dt_awal.strftime("%Y-%m-%d"), dt_akhir.strftime("%Y-%m-%d"), tgl_awal_str, tgl_akhir_str
        except ValueError:
            print("❌ Format tanggal salah! Gunakan DD-MM-YYYY (contoh: 19-11-2026).")


# LAPORAN PENJUALAN (Rentang tanggal, 5 terlaris urut kode, total per kasir, simpan ke laporan/*.txt)
def laporan_penjualan():
    print("\n" + "=" * 35 + " LAPORAN PENJUALAN " + "=" * 35)
    tgl_awal_db, tgl_akhir_db, label_awal, label_akhir = input_rentang_tanggal()
    if not tgl_awal_db:
        return

    semua_trx = baca_file(FILE_TRANSAKSI)
    semua_detail = baca_file(FILE_DETAIL_TRANSAKSI)

    trx_terfilter = []
    for t in semua_trx:
        if len(t) >= 8 and tgl_awal_db <= t <= tgl_akhir_db:
            trx_terfilter.append(t)

    if not trx_terfilter:
        print(f"\n⚠️ Tidak ada data penjualan pada periode {label_awal} s.d. {label_akhir}.")
        return

    id_trx_valid = {t for t in trx_terfilter}
    total_pendapatan = sum(int(t) for t in trx_terfilter)
    jumlah_transaksi = len(trx_terfilter)

    # Hitung total penjualan per kasir & rekap barang terlaris
    rekap_kasir = {}
    for t in trx_terfilter:
        nama_kasir = t
        rekap_kasir[nama_kasir] = rekap_kasir.get(nama_kasir, 0) + int(t)

    rekap_barang = {}  # kode -> {"nama": ..., "qty": ..., "omzet": ...}
    for d in semua_detail:
        if len(d) >= 6 and d in id_trx_valid:
            kode_b = d
            nama_b = d
            qty_b = int(d)
            sub_b = int(d)
            if kode_b not in rekap_barang:
                rekap_barang[kode_b] = {"kode": kode_b, "nama": nama_b, "qty": 0, "omzet": 0}
            rekap_barang[kode_b]["qty"] += qty_b
            rekap_barang[kode_b]["omzet"] += sub_b

    top_5_barang = sorted(rekap_barang.values(), key=lambda x: (-x["qty"], x["kode"]))[:5]

    baris_laporan = [
        "==========================================================================",
        f"LAPORAN PENJUALAN SMK MART ({label_awal} s.d. {label_akhir})",
        "==========================================================================",
        f"{'No. Nota':<12} {'Tanggal':<12} {'Jam':<10} {'Kasir':<18} {'Metode':<8} {'Total':<14}",
        "-" * 74,
    ]

    for t in trx_terfilter:
        id_tx, tgl, jam, kasir, total, metode, _, _ = t
        tgl_tampil = datetime.strptime(tgl, "%Y-%m-%d").strftime("%d-%m-%Y")
        baris_laporan.append(f"{id_tx:<12} {tgl_tampil:<12} {jam:<10} {kasir:<18} {metode:<8} {format_rupiah(total):<14}")

    baris_laporan.extend([
        "-" * 74,
        f"Jumlah Transaksi : {jumlah_transaksi} transaksi",
        f"Total Penjualan  : {format_rupiah(total_pendapatan)}",
        "\n--- TOTAL PENJUALAN PER KASIR ---",
    ])

    for kasir, nominal in rekap_kasir.items():
        baris_laporan.append(f"- {kasir:<20} : {format_rupiah(nominal)}")

    baris_laporan.append("\n--- 5 BARANG TERLARIS ---")
    for idx, item in enumerate(top_5_barang, start=1):
        baris_laporan.append(f"{idx}. [{item['kode']}] {item['nama']} - Terjual: {item['qty']} pcs ({format_rupiah(item['omzet'])})")
    baris_laporan.append("==========================================================================")

    teks_laporan = "\n".join(baris_laporan)
    print("\n" + teks_laporan)

    simpan = input("\nSimpan laporan penjualan ini ke folder laporan/? (y/n): ").strip().lower()
    if simpan == "y":
        nama_file = f"laporan_penjualan_{tgl_awal_db}_sd_{tgl_akhir_db}.txt"
        path_simpan = os.path.join(FOLDER_LAPORAN, nama_file)
        with open(path_simpan, "w", encoding="utf-8") as f:
            f.write(teks_laporan + "\n")
        catat_log_aktivitas(f"SIMPAN_LAPORAN_PENJUALAN ({nama_file})")
        print(f"✅ Laporan berhasil disimpan ke: {path_simpan}")

# LAPORAN STOK & AKTIVITAS GUDANG (Untuk Gudang & Admin)
def laporan_stok_gudang():
    print("\n" + "=" * 32 + " LAPORAN STOK & GUDANG " + "=" * 32)
    tgl_awal_db, tgl_akhir_db, label_awal, label_akhir = input_rentang_tanggal()
    if not tgl_awal_db:
        return

    daftar_barang = baca_file(FILE_BARANG)
    barang_masuk = [m for m in baca_file(FILE_BARANG_MASUK) if len(m) >= 7 and tgl_awal_db <= m <= tgl_akhir_db]
    barang_keluar = [k for k in baca_file(FILE_BARANG_KELUAR) if len(k) >= 8 and tgl_awal_db <= k <= tgl_akhir_db]

    total_masuk = sum(int(m) for m in barang_masuk)
    total_keluar = sum(int(k) for k in barang_keluar)

    baris_laporan = [
        "=================================================================================",
        f"LAPORAN STOK & AKTIVITAS GUDANG SMK MART ({label_awal} s.d. {label_akhir})",
        "=================================================================================",
        "--- DAFTAR STOK BARANG SAAT INI ---",
        f"{'Kode':<10} {'Nama Barang':<24} {'Kategori':<15} {'Stok':<8} {'Min':<8} {'Status':<10}",
        "-" * 81,
    ]

    if not daftar_barang:
        baris_laporan.append("Tidak ada data barang.")
    else:
        for b in daftar_barang:
            kode, nama, kat, _, stok, stok_min = b
            status = hitung_status_stok(stok, stok_min)
            baris_laporan.append(f"{kode:<10} {nama:<24} {kat:<15} {stok:<8} {stok_min:<8} {status:<10}")

    baris_laporan.extend([
        "-" * 81,
        f"\n--- BARANG MASUK ({len(barang_masuk)} transaksi | Total: {total_masuk} pcs) ---",
    ])
    if not barang_masuk:
        baris_laporan.append("Tidak ada data barang masuk pada rentang tanggal ini.")
    else:
        for m in barang_masuk:
            tgl_tampil = datetime.strptime(m, "%Y-%m-%d").strftime("%d-%m-%Y")
            baris_laporan.append(f"{m} | {tgl_tampil} {m} | Kode: {m} | +{m} pcs | Pemasok: {m}")

    baris_laporan.extend([
        f"\n--- BARANG KELUAR ({len(barang_keluar)} transaksi | Total: {total_keluar} pcs) ---",
    ])
    if not barang_keluar:
        baris_laporan.append("Tidak ada data barang keluar pada rentang tanggal ini.")
    else:
        for k in barang_keluar:
            tgl_tampil = datetime.strptime(k, "%Y-%m-%d").strftime("%d-%m-%Y")
            baris_laporan.append(f"{k} | {tgl_tampil} {k} | Kode: {k} | -{k} pcs | {k} ({k})")

    baris_laporan.append("=================================================================================")

    teks_laporan = "\n".join(baris_laporan)
    print("\n" + teks_laporan)

    simpan = input("\nSimpan laporan stok & gudang ini ke folder laporan/? (y/n): ").strip().lower()
    if simpan == "y":
        nama_file = f"laporan_stok_{tgl_awal_db}_sd_{tgl_akhir_db}.txt"
        path_simpan = os.path.join(FOLDER_LAPORAN, nama_file)
        with open(path_simpan, "w", encoding="utf-8") as f:
            f.write(teks_laporan + "\n")
        catat_log_aktivitas(f"SIMPAN_LAPORAN_STOK ({nama_file})")
        print(f"✅ Laporan berhasil disimpan ke: {path_simpan}")

# TAMBAH DATA PENGGUNA
def tambah_data_pengguna():
    print("\n=== MENAMBAHKAN DATA PENGGUNA ===")
    pilihan = input("Tekan [Enter] untuk lanjut atau ketik [B]atal: ").strip().lower()
    if pilihan == "b":
        return

    daftar_pengguna = baca_file(FILE_PENGGUNA)

    username = input("Masukkan Username (unik, tanpa spasi): ").strip().lower()
    if not username or "|" in username or " " in username:
        print("❌ Username tidak valid atau mengandung karakter terlarang!")
        return

    for baris in daftar_pengguna:
        if baris[1].lower() == username:
            print("❌ Username sudah digunakan oleh pengguna lain!")
            return

    nama_lengkap = input("Masukkan Nama Lengkap: ").strip()
    if not nama_lengkap or "|" in nama_lengkap:
        print("❌ Nama lengkap tidak boleh kosong atau mengandung karakter '|'!")
        return

    password = input("Masukkan Password (min. 6 karakter): ").strip()
    if len(password) < 6 or "|" in password:
        print("❌ Password minimal 6 karakter dan tidak boleh mengandung '|'!")
        return

    role = input("Masukkan Role (Admin/Kasir/Gudang): ").strip().capitalize()
    if role.lower() not in ("admin", "kasir", "gudang"):
        print("❌ Role tidak valid! Pilih Admin, Kasir, atau Gudang.")
        return

    konfirm = input(f"Yakin menambah '{nama_lengkap}' ({username}) sebagai {role}? (y/n): ").strip().lower()
    if konfirm == "y":
        id_user = buat_id_otomatis(FILE_PENGGUNA, "USR")
        baris_baru = [id_user, username, password, nama_lengkap, role, "aktif"]
        tambah_baris_file(FILE_PENGGUNA, baris_baru)
        catat_log_aktivitas(f"TAMBAH_USER {id_user} ({username})")
        print(f"✅ Pengguna '{nama_lengkap}' berhasil ditambahkan dengan ID {id_user}!")
    else:
        print("❌ Penambahan pengguna dibatalkan.")


# EDIT DATA PENGGUNA
def edit_pengguna():
    print("\n=== EDIT DATA & STATUS PENGGUNA ===")
    tampilkan_data_pengguna()
    daftar_pengguna = baca_file(FILE_PENGGUNA)
    if not daftar_pengguna:
        return

    id_user = input("Masukkan ID User yang ingin diubah (atau [B]atal): ").strip().upper()
    if id_user == "B":
        return

    index_target = -1
    for i, baris in enumerate(daftar_pengguna):
        if baris[0] == id_user:
            index_target = i
            break

    if index_target == -1:
        print("❌ ID User tidak ditemukan!")
        return

    target = daftar_pengguna[index_target]
    print(f"\nData saat ini: {target[3]} ({target[1]}) | Role: {target[4]} | Status: {target[5]}")
    print("1. Ubah Nama Lengkap")
    print("2. Ubah Role")
    print("3. Ubah Status (Aktif / Nonaktif)")
    print("0. Batal")

# belum ada konfirmasi untuk pengubahan

    pilih = input("Pilih perubahan (0-3): ").strip()
    if pilih == "1":
        nama_baru = input("Masukkan Nama Lengkap Baru: ").strip()
        if not nama_baru or "|" in nama_baru:
            print("❌ Nama tidak valid!")
            return
        daftar_pengguna[index_target][3] = nama_baru
    elif pilih == "2":
        if target[1] == user_aktif:
            print("❌ Tidak bisa mengubah role akun sendiri yang sedang login!")
            return
        role_baru = input("Masukkan Role Baru (Admin/Kasir/Gudang): ").strip().capitalize()

        if role_baru.lower() not in ("admin", "kasir", "gudang"):
            print("❌ Role tidak valid!")
            return

        if target[4].lower() == "admin" and target[5].lower() == "aktif" and role_baru.lower() != "admin":
            jumlah_admin_aktif = sum(1 for u in daftar_pengguna if u[4].lower() == "admin" and u[5].lower() == "aktif")
            if jumlah_admin_aktif <= 1:
                print("❌ Gagal! Minimal harus ada 1 akun Admin yang aktif di sistem.")
                return
        daftar_pengguna[index_target][4] = role_baru
    elif pilih == "3":
        if target[1] == user_aktif:
            print("❌ Tidak bisa menonaktifkan akun sendiri yang sedang login!")
            return
        status_baru = "nonaktif" if target[5].lower() == "aktif" else "aktif"
        if target[4].lower() == "admin" and status_baru == "nonaktif":
            jumlah_admin_aktif = sum(1 for u in daftar_pengguna if u[4].lower() == "admin" and u[5].lower() == "aktif")
            if jumlah_admin_aktif <= 1:
                print("❌ Gagal! Minimal harus ada 1 akun Admin yang aktif di sistem.")
                return
        daftar_pengguna[index_target][5] = status_baru
        print(f"Status pengguna diubah menjadi: {status_baru.upper()}")
    else:
        return

    tulis_ulang_file(FILE_PENGGUNA, daftar_pengguna)
    catat_log_aktivitas(f"EDIT_USER {id_user}")
    print("✅ Data pengguna berhasil diperbarui dan disimpan!")

def reset_password_pengguna():
    print("\n=== RESET PASSWORD PENGGUNA (ADMIN) ===")
    tampilkan_data_pengguna()
    daftar_pengguna = baca_file(FILE_PENGGUNA)
    if not daftar_pengguna:
        return

    id_user = input("Masukkan ID User yang password-nya akan direset (atau [B]atal): ").strip().upper()
    if id_user == "B":
        return

    for baris in daftar_pengguna:
        if baris[0] == id_user:
            pw_baru = input(f"Masukkan Password Baru untuk '{baris[1]}' (min. 6 karakter): ").strip()
            if len(pw_baru) < 6 or "|" in pw_baru:
                print("❌ Password minimal 6 karakter dan tidak boleh mengandung '|'!")
                return
            konfirm = input(f"Yakin reset password untuk akun '{baris[1]}'? (y/n): ").strip().lower()
            if konfirm == "y":
                baris[2] = pw_baru
                tulis_ulang_file(FILE_PENGGUNA, daftar_pengguna)
                catat_log_aktivitas(f"RESET_PASSWORD {id_user} ({baris[1]})")
                print(f"✅ Password akun '{baris[1]}' berhasil direset!")
            return

    print("❌ ID User tidak ditemukan!")

# TAMPILKAN DATA PENGGUNA
def tampilkan_data_pengguna():
    print("\n" + "=" * 28 + " DATA PENGGUNA " + "=" * 28)
    daftar_pengguna = baca_file(FILE_PENGGUNA)
    if not daftar_pengguna:
        print("Tidak ada data pengguna.")
        return

    print(f"{'ID User':<10} {'Username':<15} {'Nama Lengkap':<22} {'Role':<10} {'Status':<10}")
    print("-" * 71)
    for baris in daftar_pengguna:
        print(f"{baris[0]:<10} {baris[1]:<15} {baris[3]:<22} {baris[4]:<10} {baris[5].capitalize():<10}")
    print("-" * 71)

# FUNGSI TAMPILAN LOG AKTIVITAS (20 TERAKHIR UNTUK ADMIN)
def tampilkan_log_aktivitas():
    print("\n" + "=" * 25 + " 20 LOG AKTIVITAS TERAKHIR " + "=" * 25)
    daftar_log = baca_file(FILE_LOG_AKTIVITAS)
    if not daftar_log:
        print("Belum ada log aktivitas tercatat.")
        return

    dua_puluh_terakhir = daftar_log[-20:]
    print(f"{'Tanggal':<12} {'Waktu':<10} {'Username':<15} {'Aktivitas'}")
    print("-" * 77)
    for baris in dua_puluh_terakhir:
        if len(baris) >= 4:
            tgl_tampil = datetime.strptime(baris, "%Y-%m-%d").strftime("%d-%m-%Y") if "-" in baris and len(baris) == 10 else baris
            print(f"{tgl_tampil:<12} {baris:<10} {baris:<15} {baris}")
    print("-" * 77)
while True: 
    while True:
        if login_sistem():
            break

    logout = False

    while True:

        if role_aktif.lower() == "admin":
            print("\n===== DASHBOARD UTAMA (ADMIN) =====")
            print("1. Kelola Pengguna (User Management)")
            print("2. Kelola Data Barang & Stok")
            print("3. Laporan & Riwayat Transaksi")
            print("4. Lihat Log Aktivitas (20 Terakhir)")
            print("5. Ganti Password Sendiri")
            print("0. Log Out")
            pilihan = input("Pilih menu (0-5): ").strip()

        elif role_aktif.lower() == "kasir":
            print("\n===== MENU UTAMA APLIKASI SMK MART (KASIR) =====")
            print("1. Tampilkan Daftar Barang")
            print("2. Pencarian Barang & Filter Kategori")
            print("3. Transaksi Penjualan")
            print("4. Ganti Password Sendiri")
            print("0. Log Out")
            pilihan = input("Pilih menu (0-3): ").strip()

        elif role_aktif.lower() == "gudang":
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

        role = role_aktif.lower()
        if role == "admin":
            if pilihan == "1":
                # SUBMENU USER MANAGEMENT
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
                # SUBMENU LAPORAN & KEUANGAN
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
                tampilkan_log_aktivitas()

            elif pilihan == "5":
                ganti_password_sendiri()

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


        elif role == "kasir":
            if pilihan == "1":
                urutkan_dan_tampilkan_barang()
            elif pilihan == "2":
                searching_data_barang()
            elif pilihan == "3":
                tambah_data_transaksi()
            elif pilihan == "4":
                ganti_password_sendiri()
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


    
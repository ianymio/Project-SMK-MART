
# fitur hapus pengguna maupun barang dan dapat dipulihkan (soft delete) | 50/50 (tinggal pulihkan)
# edit qty di keranjang belanjaan || FIX | x
# cari riwayat transaksi berdasarkan tanggal | x 
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
def tambah_data_transaksi():
    while True:
        print("\n=== MELAKUKAN TRANSAKSI ===")

        tanggal = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        id_kasir = user_aktif

        keranjang_belanja = []
        total_harga_transaksi = 0
        
        while True:
            print("\n=== Input Barang Belanjaan ===")
            print("Navigasi Cepat: [L]ihat Daftar | [E]dit Keranjang | [B]atal Transaksi")
            id_barang = input("Masukkan ID Barang atau Kode Navigasi: ").strip().upper()
            
            if id_barang == 'L':
                urutkan_dan_tampilkan_barang()
                continue

            if id_barang == 'E':
                if not keranjang_belanja:
                    print("⚠️ Keranjang belanja masih kosong!")
                    continue
                
                print("\n--- ISI KERANJANG BELANJA ---")
                for idx, item in enumerate(keranjang_belanja, start=1):
                    print(f"{idx}. {item['nama_barang']} ({item['id_barang']}) | {item['jumlah_beli']} pcs x Rp{item['harga_satuan']} = Rp{item['subtotal']}")
                print("0. Kembali")
                
                pilih_item = input_angka("Pilih nomor urut barang yang ingin diubah (0 untuk batal): ", minimum=0)
                if pilih_item == 0:
                    continue
                if pilih_item > len(keranjang_belanja):
                    print("❌ Nomor barang tidak valid!")
                    continue
                
                item_terpilih = keranjang_belanja[pilih_item - 1]
                stok_gudang = smk_mart_db["barang"][item_terpilih["id_barang"]]["Stok Sekarang"]
                
                print(f"Barang dipilih: {item_terpilih['nama_barang']} (Saat ini: {item_terpilih['jumlah_beli']} pcs | Stok tersedia: {stok_gudang} pcs)")
                qty_baru = input_angka("Masukkan jumlah beli baru (ketik 0 untuk menghapus item): ", minimum=0)
                
                if qty_baru == 0:
                    total_harga_transaksi -= item_terpilih["subtotal"]
                    keranjang_belanja.pop(pilih_item - 1)
                    print(f"🗑️ '{item_terpilih['nama_barang']}' berhasil dihapus dari keranjang.")
                elif qty_baru > stok_gudang:
                    print(f"❌ Gagal! Stok fisik hanya tersedia {stok_gudang} pcs.")
                else:
                    total_harga_transaksi -= item_terpilih["subtotal"]
                    item_terpilih["jumlah_beli"] = qty_baru
                    item_terpilih["subtotal"] = qty_baru * item_terpilih["harga_satuan"]
                    total_harga_transaksi += item_terpilih["subtotal"]
                    print(f"✅ Jumlah '{item_terpilih['nama_barang']}' diperbarui menjadi {qty_baru} pcs.")
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
            
            item_sudah_ada = False
            for item in keranjang_belanja:
                if item["id_barang"] == id_barang:
                    item["jumlah_beli"] += jumlah_beli
                    item["subtotal"] += subtotal
                    item_sudah_ada = True
                    break
            
            if not item_sudah_ada:
                keranjang_belanja.append({
                    "id_barang": id_barang,
                    "nama_barang": detail_barang["Nama Barang"],
                    "harga_beli": detail_barang.get("Harga Beli", 0),
                    "harga_satuan": detail_barang["Harga Jual"],
                    "jumlah_beli": jumlah_beli,
                    "subtotal": subtotal
                })
            # ------------------------------------------------------------------
            print(f"✅ {detail_barang['Nama Barang']} ({jumlah_beli} pcs) berhasil ditambahkan ke keranjang.")

            tanya_lagi = input("Apakah ingin menambahkan barang lain / edit keranjang? (y/n): ").lower()
            if tanya_lagi == 'n':
                break

        if not keranjang_belanja:
            print("❌ Keranjang belanja kosong! Transaksi dibatalkan.")
            return
        
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
            kembalian = jumlah_bayar - total_harga_transaksi
        else:
            metode = "QRIS"
            jumlah_bayar = total_harga_transaksi
            kembalian = 0

        for item in keranjang_belanja:
            smk_mart_db["barang"][item["id_barang"]]["Stok Sekarang"] -= item["jumlah_beli"]

        id_transaksi = "TX" + datetime.now().strftime("%Y%m%d%H%M%S")
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
        t_trx = input("\nTambah transaksi lagi? (y/n): ").lower()
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

def cari_riwayat_transaksi():
  print("\n=== CARI RIWAYAT TRANSAKSI ===")
  if not smk_mart_db["Transaksi"]:
    print("Belum ada riwayat transaksi penjualan.")
    return

  hari_ini = datetime.now().strftime("%d-%m-%Y")
  kemarin = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")

  print(f"[1] Hari Ini ({hari_ini})")
  print(f"[2] Kemarin  ({kemarin})")
  print("Atau ketik tanggal manual (Format: DD-MM-YYYY)")

  pilihan = input("Pilih opsi [1/2], ketik tanggal, atau [B]atal: ").strip().lower()

  if pilihan == "b":
    print("Pencarian riwayat dibatalkan! ❌")
    return

  if not pilihan:
    print("❌ Input tidak boleh kosong.")
    return

  if pilihan == "1":
    tanggal_tx = hari_ini
  elif pilihan == "2":
    tanggal_tx = kemarin
  else:
    tanggal_tx = pilihan

  ditemukan = False
  print("\n====================================================")
  for id_tx, data_tx in smk_mart_db["Transaksi"].items():
    if data_tx["tanggal"].startswith(tanggal_tx):
      ditemukan = True
      print(f"ID Transaksi / Nota : {id_tx}")
      print(f"Tanggal             : {data_tx['tanggal']}")
      print(f"ID Kasir            : {data_tx['id_kasir']}")
      print("Daftar Barang Belanjaan :")
      for item in data_tx["items"]:
        print(
            f" - {item['nama_barang']} ({item['jumlah_beli']} pcs) | Subtotal:"
            f" Rp{item['subtotal']:,}"
        )
      print(f"Total Bayar         : Rp{data_tx['total_harga']:,}")
      print(f"Metode Pembayaran   : {data_tx['metode_pembayaran']}")
      print("====================================================")

  if not ditemukan:
    print(f"❌ Tidak ditemukan transaksi pada tanggal '{tanggal_tx}'.")
    print("====================================================")
    return


# Data Laporan Penjualan
def laporan_penjualan():
    print("\n" + "=" * 45 + " LAPORAN TRANSAKSI PENJUALAN " + "=" * 46)
    print("=" * 120)
    if not smk_mart_db["Transaksi"]:
        print("Belum ada transaksi penjualan yang tercatat.")
        return

    total_uang_masuk = 0
    total_barang_terjual = 0
    total_keuntungan = 0

    print(f"{'Nota':<18} {'Tanggal':<21} {'Kasir':<12} {'Via':<8}{'Nama Barang':<22} {'Jumlah':<10}{'Jual':<14}{'Laba':<14}")
    print("-" * 120)

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

            harga_beli_pabrik = item.get(
                "harga_beli",
                smk_mart_db["barang"].get(id_barang, {}).get("Harga Beli", item["harga_satuan"])
            )

            laba_per_pcs = item["harga_satuan"] - harga_beli_pabrik
            keuntungan_item = laba_per_pcs * jumlah

            total_barang_terjual += jumlah
            total_keuntungan += keuntungan_item

            nama_barang_teks = f"{item['nama_barang']}"
            jumlah_beli_teks = f"{item['jumlah_beli']} pcs"
            jual = f"Rp{item['harga_satuan']:,}"
            laba = f"Rp{laba_per_pcs * jumlah :,}"
            print(f"{id_tx:<18} {data['tanggal']:<21} {data['id_kasir']:<12} {data['metode_pembayaran']:<8}{nama_barang_teks:<22} {jumlah_beli_teks:<10}{jual:<14}{laba:<14}")

        total_uang_masuk += data["total_harga"]
       
    print(f"\nTotal Uang Masuk     : Rp{total_uang_masuk :,}")
    print(f"Total Barang Terjual : {total_barang_terjual} pcs")
    print(f"Total Keuntungan     : Rp{total_keuntungan :,}")

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

        if id_barang not in smk_mart_db["barang"] or smk_mart_db["barang"][id_barang].get("Terhapus", False):
            print("❌ ID Barang tidak ditemukan atau sudah dihapus!")
            continue
        break

    tanggal_barang_masuk = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    jenis_aktivitas = input("Masukkan Jenis Aktivitas [M]asuk | [K]eluar: ").strip().lower()
    
    if jenis_aktivitas not in ("m", "k"):
        print("❌ Jenis aktivitas salah! Gunakan 'm' atau 'k'.")
        return

    # 2. Input jumlah barang setelah dipastikan jenis aktivitasnya valid
    jumlah_barang = input_angka("Masukkan Jumlah Barang: ", minimum=1)
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
            print("1. Tampilkan Semua Barang")
            print("2. Searching Data Barang")
            print("3. Tambah Transaksi Penjualan")
            print("0. Log Out")
            pilihan = input("Pilih menu (0-3): ").strip()

        elif role_aktif.lower() == "gudang":
            print("\n===== MENU UTAMA APLIKASI SMK MART (GUDANG) =====")
            print("1. Tambah Data Barang")
            print("2. Catat Aktivitas Gudang")
            print("3. Tampilkan Semua Barang")
            print("4. Searching Data Barang")
            print("5. Edit Data Barang")
            print("6. Hapus Data Barang")
            print("7. Pulihkan Data Barang")
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
            elif pilihan == "7": pulihkan_data_barang()
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


    
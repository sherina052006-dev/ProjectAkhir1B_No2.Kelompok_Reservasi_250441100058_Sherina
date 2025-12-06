# =============================================================
# Villa Reservation System - V4 (FULL VERSION – BEAUTIFIED UI)
# Extended with: delete review, double-book prevention, availability check, robust input handling.
# Hiasan input & tampilan ditambahkan (header, section, box, warna ANSI).
# Save as: villa_reservation_v4.py
# =============================================================

import json
import uuid
from datetime import datetime, timedelta
import math
import os
import getpass

# ---------------------------
# UI / Hiasan (Decoration) - combined utilities
# ---------------------------
def color(text, c="cyan"):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "end": "\033[0m"
    }
    return colors.get(c, "") + text + colors["end"]

def fancy_title(text):
    print("\n" + "=" * 60)
    print(color(text.center(60), "magenta"))
    print("=" * 60)

def fancy_section(text):
    print("\n" + "-" * 60)
    print(color(text.center(60), "cyan"))
    print("-" * 60)

def box(text):
    print("\n+" + "-" * 58 + "+")
    print("|" + text.center(58) + "|")
    print("+" + "-" * 58 + "+")

def pretty_input_label(text):
    """Return a decorated label for input prompts (keeps logic unchanged)."""
    return color(f"» {text}: ", "cyan")

def prompt(text):
    """Simple decorated prompt (returns full prompt string)."""
    return f"{color('»', 'green')} {text} "

# ---------------------------
# Persistence helpers
# ---------------------------
DATA_DIR = "data_villa_v4"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")
REVIEWS_FILE = os.path.join(DATA_DIR, "reviews.json")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path, default in [(USERS_FILE, {}), (BOOKINGS_FILE, {}), (REVIEWS_FILE, {})]:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

ensure_data_dir()
USERS = load_json(USERS_FILE)
BOOKINGS = load_json(BOOKINGS_FILE)
REVIEWS = load_json(REVIEWS_FILE)

# ---------------------------
# Utility
# ---------------------------
def generate_id(prefix="B"):
    return f"{prefix}{str(uuid.uuid4())[:8].upper()}"

def generate_barcode():
    return "BCODE-" + str(uuid.uuid4())[:10].upper()

def safe_input(prompt_text, validator=None, allow_empty=False):
    """
    Generic input helper that loops until value passes validator.
    validator: function(str) -> (ok:bool, parsed_value_or_msg)
      - if ok True: return parsed_value_or_msg
      - if ok False: print parsed_value_or_msg and repeat
    If validator is None, returns raw string (unless empty not allowed).
    """
    while True:
        try:
            s = input(pretty_input_label(prompt_text)).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n" + color("Input dibatalkan, kembali ke menu.", "yellow"))
            return None

        if not s and not allow_empty:
            print(color("Input tidak boleh kosong. Coba lagi.", "red"))
            continue

        if validator is None:
            return s

        ok, val = validator(s)
        if ok:
            return val
        else:
            print(color(val, "red"))

def parse_int_val(minv=None, maxv=None):
    def v(s):
        if not s:
            return False, "Tidak boleh kosong."
        if not s.lstrip("-").isdigit():
            return False, "Harus berupa angka bulat."
        iv = int(s)
        if minv is not None and iv < minv:
            return False, f"Nilai minimal: {minv}"
        if maxv is not None and iv > maxv:
            return False, f"Nilai maksimal: {maxv}"
        return True, iv
    return v

def parse_date_val(format="%d-%m-%Y"):
    def v(s):
        try:
            dt = datetime.strptime(s, format)
            return True, dt
        except ValueError:
            return False, f"Format salah, gunakan {format}."
    return v

def human_dt(dt):
    if isinstance(dt, str):
        return dt
    return dt.strftime("%d-%m-%Y %H:%M")

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ---------------------------
# STATIC DATA (Many Villas — extended)
# ---------------------------
VILLAS = [
    # Jakarta
    {"id":"JKT01","city":"Jakarta","name":"Villa Menteng Elite","price":1500000,"rating":4.9,"capacity":10,
     "facilities":["Kolam Renang","Karaoke","Dapur Lengkap","Parkir"],"desc":"Villa mewah Menteng.","coords":[-6.200,106.830],"type":"Luxury"},
    {"id":"JKT02","city":"Jakarta","name":"Villa Ancol View","price":650000,"rating":4.2,"capacity":3,
     "facilities":["AC","Wifi","Sarapan"],"desc":"Dekat Ancol.","coords":[-6.124,106.830],"type":"Standard"},
    {"id":"JKT03","city":"Jakarta","name":"Villa Budget Jakarta Barat","price":300000,"rating":3.4,"capacity":2,
     "facilities":["Wifi","Parkir"],"desc":"Murah & strategis.","coords":[-6.166,106.785],"type":"Budget"},
    {"id":"JKT04","city":"Jakarta","name":"Villa Kemang Cozy","price":550000,"rating":4.1,"capacity":4,
     "facilities":["AC","Dapur","Parking"],"desc":"Cocok untuk keluarga kecil.","coords":[-6.229,106.816],"type":"Standard"},
    # Bandung
    {"id":"BDG01","city":"Bandung","name":"Villa Dago Hills","price":600000,"rating":4.0,"capacity":4,
     "facilities":["Pemandangan","Wifi","Dapur"],"desc":"Dago sejuk.","coords":[-6.883,107.610],"type":"Standard"},
    {"id":"BDG02","city":"Bandung","name":"Villa Lembang Farm","price":900000,"rating":4.6,"capacity":8,
     "facilities":["Taman","Kolam Mini","Parkir"],"desc":"Cocok untuk gathering.","coords":[-6.780,107.610],"type":"Family"},
    {"id":"BDG03","city":"Bandung","name":"Villa Braga Heritage","price":700000,"rating":4.3,"capacity":5,
     "facilities":["Wifi","AC","SmartTV"],"desc":"Dekat pusat kota.","coords":[-6.917,107.619],"type":"Standard"},
    # Bali
    {"id":"BALI01","city":"Bali","name":"Villa Sunset","price":450000,"rating":4.1,"capacity":2,
     "facilities":["Pool","AC","Wifi"],"desc":"Romantis dekat pantai.","coords":[-8.670,115.212],"type":"Couple"},
    {"id":"BALI02","city":"Bali","name":"Villa Mandala","price":1200000,"rating":4.8,"capacity":6,
     "facilities":["Private Pool","BBQ"],"desc":"Private modern.","coords":[-8.789,115.174],"type":"Luxury"},
    {"id":"BALI03","city":"Bali","name":"Villa Seminyak Shore","price":850000,"rating":4.5,"capacity":4,
     "facilities":["Dekat Pantai","AC","Wifi"],"desc":"Trendy area Seminyak.","coords":[-8.690,115.168],"type":"Standard"},
    # Yogyakarta
    {"id":"YGY01","city":"Yogyakarta","name":"Villa Kaliurang","price":400000,"rating":4.0,"capacity":4,
     "facilities":["Pemandangan","Parkir","Dapur"],"desc":"Sejuk & dekat alam.","coords":[-7.755,110.446],"type":"Standard"},
    {"id":"YGY02","city":"Yogyakarta","name":"Villa Malioboro Stay","price":350000,"rating":3.9,"capacity":3,
     "facilities":["Wifi","AC"],"desc":"Dekat Malioboro.","coords":[-7.797,110.367],"type":"Budget"},
    # Surabaya
    {"id":"SBY01","city":"Surabaya","name":"Villa Kenjeran","price":500000,"rating":4.2,"capacity":5,
     "facilities":["Parkir","AC","Wifi"],"desc":"Dekat pantai Kenjeran.","coords":[-7.287,112.744],"type":"Standard"},
    # Lombok
    {"id":"LOM01","city":"Lombok","name":"Villa Gili Breeze","price":750000,"rating":4.7,"capacity":6,
     "facilities":["Private Pool","Boat Transfer"],"desc":"Akses ke Gili.","coords":[-8.350,116.045],"type":"Luxury"},
    # Malang
    {"id":"MLG01","city":"Malang","name":"Villa Batu Cool","price":420000,"rating":4.1,"capacity":4,
     "facilities":["Pemandangan","Dapur"],"desc":"Dekat Batu.","coords":[-7.877,112.519],"type":"Standard"},
    # Semarang
    {"id":"SMG01","city":"Semarang","name":"Villa Ungaran","price":380000,"rating":3.8,"capacity":3,
     "facilities":["Parkir","Wifi"],"desc":"Tenang & strategis.","coords":[-7.136,110.435],"type":"Budget"},
    # Additional options for variety
    {"id":"BDG04","city":"Bandung","name":"Villa Ciwidey Retreat","price":650000,"rating":4.4,"capacity":6,
     "facilities":["Pemandangan","HotSpring"],"desc":"Cocok untuk relaksasi.","coords":[-7.281,107.000],"type":"Family"},
    {"id":"JKT05","city":"Jakarta","name":"Villa Pulau Seribu","price":1100000,"rating":4.6,"capacity":8,
     "facilities":["Dekat Laut","BoatTransfer"],"desc":"Private island feel.","coords":[-5.783,106.750],"type":"Luxury"},
]

VILLAS_BY_CITY = {}
for v in VILLAS:
    VILLAS_BY_CITY.setdefault(v["city"], []).append(v)

DISCOUNT_WEEKDAY = {0: 10, 4: 15}
FULL_REFUND_HOURS = 72
PARTIAL_REFUND_HOURS = 24

# ---------------------------
# USER MANAGEMENT
# ---------------------------
def register():
    fancy_title("✨ REGISTER ✨")
    print(color("Masukkan data untuk membuat akun baru", "yellow"))
    while True:
        username = safe_input("Username", None, allow_empty=False)
        if username is None:
            return
        if username in USERS:
            print(color("⚠ Username sudah dipakai. Coba yang lain.", "red"))
            continue
        break

    password = safe_input("Password", None, allow_empty=False)
    if password is None:
        return
    name = safe_input("Nama lengkap", None, allow_empty=False)
    if name is None:
        return
    email = safe_input("Email", None, allow_empty=False)
    if email is None:
        return

    USERS[username] = {"password": password, "name": name, "email": email}
    save_json(USERS_FILE, USERS)
    print(color("✅ Registrasi berhasil.", "green"))

def login():
    fancy_title("🔐 LOGIN")
    username = safe_input("Username", None, allow_empty=False)
    if username is None:
        return None
    password = getpass.getpass(pretty_input_label("Password"))
    user = USERS.get(username)
    if not user or user["password"] != password:
        print(color("❌ Login gagal.", "red"))
        return None
    print(color(f"✅ Selamat datang, {user['name']}!", "green"))
    return username

def delete_account(username):
    fancy_section("HAPUS AKUN")
    konfirmasi = safe_input("Yakin hapus akun? Semua data booking & review akan hilang! (y/n)", None)
    if konfirmasi is None or konfirmasi.lower() != "y":
        print(color("Dibatalkan.", "yellow"))
        return

    # Hapus booking yang terkait user
    to_delete = []
    for bid, b in list(BOOKINGS.items()):
        if b.get("username") == username:
            to_delete.append(bid)
    for bid in to_delete:
        del BOOKINGS[bid]
    save_json(BOOKINGS_FILE, BOOKINGS)

    # Hapus review user
    for villa_id in list(REVIEWS.keys()):
        REVIEWS[villa_id] = [r for r in REVIEWS[villa_id] if r.get("username") != username]
        if not REVIEWS[villa_id]:
            del REVIEWS[villa_id]
    save_json(REVIEWS_FILE, REVIEWS)

    # Hapus akun
    if username in USERS:
        del USERS[username]
        save_json(USERS_FILE, USERS)

    print(color("Akun dan semua data berhasil dihapus!", "green"))
    return "LOGOUT"

def forgot_password():
    fancy_section("LUPA PASSWORD")
    username = safe_input("Masukkan username", None, allow_empty=False)
    if username is None:
        return

    if username not in USERS:
        print(color("Username tidak ditemukan.", "red"))
        return

    email = safe_input("Masukkan email terdaftar", None, allow_empty=False)
    if email is None:
        return
    if email != USERS[username].get("email"):
        print(color("Email tidak cocok!", "red"))
        return

    new_pass = safe_input("Masukkan password baru", None, allow_empty=False)
    if new_pass is None:
        return
    confirm = safe_input("Konfirmasi password baru", None, allow_empty=False)
    if confirm is None:
        return
    if new_pass != confirm:
        print(color("Password tidak cocok. Proses dibatalkan.", "red"))
        return

    USERS[username]["password"] = new_pass
    save_json(USERS_FILE, USERS)

    print(color("Password berhasil diperbarui!", "green"))

# ---------------------------
# SEARCH & SORT
# ---------------------------
def choose_city():
    fancy_section("PILIH KOTA")
    cities = sorted(VILLAS_BY_CITY.keys())
    for i, c in enumerate(cities, 1):
        print(f"{i}. {c}")
    idx = safe_input("Pilih kota (nomor)", parse_int_val(1, len(cities)))
    if idx is None:
        return None
    return cities[idx-1]

def filter_and_sort_villas(city):
    if city is None:
        return []
    fancy_section(f"Cari villa di {city}")
    try:
        min_rating = float(safe_input("Minimal rating (enter=0)", None, allow_empty=True) or "0")
    except:
        min_rating = 0

    min_capacity = safe_input("Minimal kapasitas", parse_int_val(1))
    if min_capacity is None:
        return []
    max_price_str = safe_input("Max harga (enter=semua)", None, allow_empty=True)
    max_price = float(max_price_str) if max_price_str else None

    candidates = [
        v for v in VILLAS_BY_CITY.get(city, [])
        if v["rating"] >= min_rating and v["capacity"] >= min_capacity
        and (max_price is None or v["price"] <= max_price)
    ]
    if not candidates:
        print(color("Tidak ada villa cocok.", "yellow"))
        return []

    print("-- Sorting (optional) --")
    print("1 = price, 2 = rating, 3 = capacity")
    sort_steps = []

    while True:
        key = safe_input("Tambah kriteria (enter = selesai)", None, allow_empty=True)
        if key is None:
            return candidates
        if not key:
            break
        if key not in {"1","2","3"}:
            print(color("Pilihan salah.", "red"))
            continue
        direction = safe_input("a=asc, d=desc", None, allow_empty=False)
        if direction is None:
            return candidates
        sort_steps.append((key, direction))

    for key, direction in reversed(sort_steps):
        if key == "1":
            candidates.sort(key=lambda x: x["price"], reverse=(direction=="d"))
        elif key == "2":
            candidates.sort(key=lambda x: x["rating"], reverse=(direction=="d"))
        elif key == "3":
            candidates.sort(key=lambda x: x["capacity"], reverse=(direction=="d"))

    if not sort_steps:
        candidates.sort(key=lambda x: (x["price"], -x["rating"]))
    return candidates

def display_villas_list(villas):
    box("DAFTAR VILLA")
    for i, v in enumerate(villas, 1):
        print(color(f"{i}. {v['name']}", "magenta"))
        print(f"   Rp{v['price']:,}/mlm | Rating {v['rating']} | Kapasitas {v['capacity']}")
        print("   Type:", v["type"])
        print("   Fasilitas:", ", ".join(v["facilities"]))
        print("   Deskripsi:", v["desc"])
        print("-" * 58)

# ---------------------------
# PRICE CALC
# ---------------------------
def calc_price(base_price, checkin_dt, nights):
    total = base_price * nights
    wd = checkin_dt.weekday()
    disc = DISCOUNT_WEEKDAY.get(wd, 0)
    final = total * (1 - disc/100)
    return total, disc, final

# ---------------------------
# BOOKING AVAILABILITY HELPERS
# ---------------------------
def intervals_overlap(a_start, a_end, b_start, b_end):
    """
    Returns True if [a_start, a_end) overlaps with [b_start, b_end)
    """
    return not (a_end <= b_start or b_end <= a_start)

def is_villa_unavailable(villa_id, new_checkin, new_checkout, ignore_booking_id=None):
    """
    Check if any existing booking (PENDING_PAYMENT or PAID) overlaps with given time range.
    """
    for b in BOOKINGS.values():
        if b.get("villa_id") != villa_id:
            continue
        if b.get("status") not in {"PENDING_PAYMENT", "PAID"}:
            continue
        if ignore_booking_id and b.get("booking_id") == ignore_booking_id:
            continue
        existing_checkin = datetime.fromisoformat(b["checkin"])
        existing_checkout = datetime.fromisoformat(b["checkout"])
        if intervals_overlap(existing_checkin, existing_checkout, new_checkin, new_checkout):
            return True, b  # unavailable and return conflicting booking
    return False, None

def is_double_booking_by_user(username, villa_id, new_checkin, new_checkout):
    """
    Prevent same user from making overlapping bookings for the same villa.
    """
    for b in BOOKINGS.values():
        if b.get("username") != username:
            continue
        if b.get("villa_id") != villa_id:
            continue
        if b.get("status") not in {"PENDING_PAYMENT", "PAID"}:
            continue
        existing_checkin = datetime.fromisoformat(b["checkin"])
        existing_checkout = datetime.fromisoformat(b["checkout"])
        if intervals_overlap(existing_checkin, existing_checkout, new_checkin, new_checkout):
            return True, b
    return False, None

# ---------------------------
# REVIEWS
# ---------------------------
def show_reviews(villa_id):
    revs = REVIEWS.get(villa_id, [])
    if not revs:
        print(color("   (Belum ada review)", "yellow"))
        return
    print("-- Review --")
    for r in revs:
        print(color(f"- {r['username']} | Rating {r['rating']}", "blue"))
        if r.get('comment'):
            print("  Komentar:", r['comment'])
        print("  Tanggal :", r['at'])

def view_reviews_flow():
    fancy_section("LIHAT REVIEW VILLA")
    print("1. Pilih kota lalu villa")
    print("2. Cari berdasarkan nama villa")
    choice = safe_input("Pilih metode (1/2)", None, allow_empty=False)
    if choice is None:
        return
    if choice == "1":
        city = choose_city()
        if city is None:
            return
        villas = VILLAS_BY_CITY.get(city, [])
        if not villas:
            print(color("Tidak ada villa di kota ini.", "yellow"))
            return
        display_villas_list(villas)
        idx = safe_input("Pilih villa untuk lihat review", parse_int_val(1, len(villas)))
        if idx is None:
            return
        villa = villas[idx-1]
        print(color(f"Review untuk {villa['name']}", "magenta"))
        show_reviews(villa['id'])
    elif choice == "2":
        q = safe_input("Masukkan nama (atau bagian nama)", None, allow_empty=False)
        if q is None:
            return
        found = [v for v in VILLAS if q.lower() in v['name'].lower()]
        if not found:
            print(color("Tidak ditemukan villa dengan nama tersebut.", "yellow"))
            return
        display_villas_list(found)
        idx = safe_input("Pilih villa untuk lihat review", parse_int_val(1, len(found)))
        if idx is None:
            return
        villa = found[idx-1]
        print(color(f"Review untuk {villa['name']}", "magenta"))
        show_reviews(villa['id'])
    else:
        print(color("Pilihan salah.", "red"))

def delete_review_flow(username):
    user_reviews = []
    for villa_id, rvlist in REVIEWS.items():
        for r in rvlist:
            if r.get("username") == username:
                user_reviews.append((villa_id, r))

    if not user_reviews:
        print(color("Kamu belum pernah buat review.", "yellow"))
        return

    fancy_section("Review milikmu")
    for i, (villa_id, r) in enumerate(user_reviews, 1):
        villa_name = next((v["name"] for v in VILLAS if v["id"] == villa_id), villa_id)
        print(f"{i}. {villa_name} | Rating {r['rating']} | {r.get('comment','')[:60]} | Tanggal: {r.get('at')} (BookingID:{r.get('booking_id')})")

    idx = safe_input("Pilih nomor review yang mau dihapus (enter = batal)", parse_int_val(1, len(user_reviews)), allow_empty=True)
    if idx is None:
        return
    if idx == "":
        print(color("Dibatalkan.", "yellow"))
        return
    idx = int(idx)
    villa_id, review_obj = user_reviews[idx-1]
    REVIEWS[villa_id] = [r for r in REVIEWS.get(villa_id, []) if r is not review_obj]
    if not REVIEWS[villa_id]:
        del REVIEWS[villa_id]
    save_json(REVIEWS_FILE, REVIEWS)
    print(color("Review berhasil dihapus!", "green"))

# ---------------------------
# BOOKING FLOW
# ---------------------------
def start_booking_flow(username):
    fancy_section("PESAN VILLA")
    city = choose_city()
    if city is None:
        return
    villas = filter_and_sort_villas(city)
    if not villas:
        return

    display_villas_list(villas)
    idx = safe_input("Pilih villa (nomor)", parse_int_val(1, len(villas)))
    if idx is None:
        return
    villa = villas[idx-1]

    box("DETAIL VILLA")
    print(color(villa["name"], "magenta"))
    print(f"Harga per malam : Rp{villa['price']:,}")
    print("Deskripsi       :", villa["desc"])
    show_reviews(villa["id"])

    # tanggal & jam & nights input with validation
    date = safe_input("Tanggal check-in (DD-MM-YYYY)", parse_date_val("%d-%m-%Y"))
    if date is None:
        return
    hour = safe_input("Jam check-in (0-23)", parse_int_val(0,23))
    if hour is None:
        return
    nights = safe_input("Durasi malam", parse_int_val(1))
    if nights is None:
        return
    guests = safe_input("Jumlah tamu", parse_int_val(1))
    if guests is None:
        return

    # build datetimes
    checkin_dt = datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=hour)
    checkout_dt = checkin_dt + timedelta(days=nights)

    if guests > villa["capacity"]:
        print(color("Melebihi kapasitas.", "red"))
        return

    # check double booking by the same user
    dbl, bconf = is_double_booking_by_user(username, villa["id"], checkin_dt, checkout_dt)
    if dbl:
        print(color("Kamu sudah punya booking yang tumpang tindih untuk villa ini:", "red"))
        print(f"- Booking {bconf['booking_id']} | {bconf['villa_name']} | {bconf['checkin']} - {bconf['checkout']} | Status {bconf['status']}")
        return

    # check availability (anyone)
    unavailable, conf = is_villa_unavailable(villa["id"], checkin_dt, checkout_dt)
    if unavailable:
        print(color("Maaf, villa ini sudah dibooking pada rentang waktu tersebut oleh:", "red"))
        print(f"- Booking {conf['booking_id']} | {conf['username']} | {conf['checkin']} - {conf['checkout']} | Status {conf['status']}")
        return

    total, disc, final = calc_price(villa["price"], checkin_dt, nights)

    print(color(f"Total sebelum diskon: Rp{int(total):,}", "yellow"))
    if disc > 0:
        print(color(f"Diskon {disc}% -> Rp{int(final):,}", "green"))
    else:
        print(color(f"Harga akhir: Rp{int(final):,}", "cyan"))

    confirm = safe_input("Konfirmasi booking (y/n)", None, allow_empty=False)
    if confirm is None or confirm.lower() != "y":
        print(color("Dibatalkan.", "yellow"))
        return

    booking_id = generate_id("B")
    barcode = generate_barcode()

    booking = {
        "booking_id": booking_id,
        "username": username,
        "villa_id": villa["id"],
        "villa_name": villa["name"],
        "city": villa["city"],
        "checkin": checkin_dt.isoformat(),
        "checkout": checkout_dt.isoformat(),
        "nights": nights,
        "guests": guests,
        "base_total": total,
        "discount_percent": disc,
        "final_total": final,
        "status": "PENDING_PAYMENT",
        "barcode": barcode,
        "paid_at": None,
        "cancelled_at": None,
        "refund_amount": 0,
        "created_at": datetime.now().isoformat(),
    }

    BOOKINGS[booking_id] = booking
    save_json(BOOKINGS_FILE, BOOKINGS)

    print(color("Booking berhasil!", "green"))
    print("ID:", booking_id)
    print("Barcode:", barcode)

# ---------------------------
# PAYMENT
# ---------------------------
def pay_booking_flow(username):
    fancy_section("PEMBAYARAN")
    pendings = [b for b in BOOKINGS.values()
                if b.get("username")==username and b.get("status")=="PENDING_PAYMENT"]
    if not pendings:
        print(color("Tidak ada booking menunggu pembayaran.", "yellow"))
        return

    for i,b in enumerate(pendings,1):
        print(f"{i}. {b['booking_id']} | {b['villa_name']} | Rp{int(b['final_total']):,} | {b['checkin']} - {b['checkout']}")

    idx = safe_input("Pilih (nomor)", parse_int_val(1, len(pendings)))
    if idx is None:
        return
    b = pendings[idx-1]

    print(color("--- Simulasi BANK ---", "cyan"))
    bank_user = safe_input("Bank Username", None, allow_empty=False)
    if bank_user is None:
        return
    bank_pin = getpass.getpass(pretty_input_label("PIN"))
    code = safe_input("Masukkan barcode", None, allow_empty=False)
    if code is None or code != b.get("barcode"):
        print(color("Barcode salah.", "red"))
        return

    confirm = safe_input(f"Bayar Rp{int(b['final_total']):,}? (y/n)", None, allow_empty=False)
    if confirm is None or confirm.lower() != "y":
        print(color("Dibatalkan.", "yellow"))
        return

    # Before marking paid, re-check availability because others might have paid in meantime
    checkin_dt = datetime.fromisoformat(b["checkin"])
    checkout_dt = datetime.fromisoformat(b["checkout"])
    unavailable, conf = is_villa_unavailable(b["villa_id"], checkin_dt, checkout_dt, ignore_booking_id=b["booking_id"])
    if unavailable:
        print(color("Maaf, saat hendak membayar ditemukan konflik booking lain yang sudah dibayar. Pembayaran dibatalkan.", "red"))
        print(f"Konflik: {conf['booking_id']} | {conf['username']} | {conf['checkin']} - {conf['checkout']}")
        return

    b["status"] = "PAID"
    b["paid_at"] = datetime.now().isoformat()
    save_json(BOOKINGS_FILE, BOOKINGS)

    print(color("Pembayaran sukses!", "green"))

# ---------------------------
# CANCELLATION
# ---------------------------
def cancel_booking_flow(username):
    fancy_section("BATALKAN BOOKING")
    eligible = [b for b in BOOKINGS.values()
                if b.get("username")==username and b.get("status") in {"PENDING_PAYMENT","PAID"}]
    if not eligible:
        print(color("Tidak ada booking yang bisa dibatalkan.", "yellow"))
        return

    for i,b in enumerate(eligible,1):
        print(f"{i}. {b['booking_id']} | {b['villa_name']} | Status: {b['status']} | {b['checkin']} - {b['checkout']}")

    idx = safe_input("Pilih (nomor)", parse_int_val(1, len(eligible)))
    if idx is None:
        return
    b = eligible[idx-1]

    checkin_dt = datetime.fromisoformat(b["checkin"])
    hours_left = (checkin_dt - datetime.now()).total_seconds()/3600

    if hours_left >= FULL_REFUND_HOURS:
        refund = b["final_total"]
    elif hours_left >= PARTIAL_REFUND_HOURS:
        refund = b["final_total"] * 0.5
    else:
        refund = 0

    b["status"] = "CANCELLED"
    b["cancelled_at"] = datetime.now().isoformat()
    b["refund_amount"] = refund
    save_json(BOOKINGS_FILE, BOOKINGS)

    print(color(f"Booking dibatalkan. Refund Rp{int(refund):,}", "green"))

# ---------------------------
# GIVE REVIEW
# ---------------------------
def give_review_flow(username):
    fancy_section("BERI REVIEW")
    now = datetime.now()
    eligible = []

    for b in BOOKINGS.values():
        if b.get("username") == username and b.get("status") == "PAID":
            checkout = datetime.fromisoformat(b["checkout"])
            if checkout <= now:
                villa_revs = REVIEWS.get(b["villa_id"], [])
                if not any(r.get("username")==username and r.get("booking_id")==b.get("booking_id") for r in villa_revs):
                    eligible.append(b)

    if not eligible:
        print(color("Tidak ada yang bisa direview.", "yellow"))
        return

    for i,b in enumerate(eligible,1):
        print(f"{i}. {b['villa_name']} (ID {b['villa_id']}) | {b['checkin']} - {b['checkout']}")

    idx = safe_input("Pilih (nomor)", parse_int_val(1, len(eligible)))
    if idx is None:
        return
    b = eligible[idx-1]

    rating = safe_input("Rating (1-5)", parse_int_val(1,5))
    if rating is None:
        return
    comment = safe_input("Komentar (opsional)", None, allow_empty=True)
    if comment is None:
        return

    rev = {
        "booking_id": b["booking_id"],
        "username": username,
        "rating": rating,
        "comment": comment,
        "at": datetime.now().strftime("%d-%m-%Y %H:%M")
    }

    REVIEWS.setdefault(b["villa_id"], []).append(rev)
    save_json(REVIEWS_FILE, REVIEWS)

    print(color("Review terkirim!", "green"))

# ---------------------------
# VIEW BOOKINGS
# ---------------------------
def view_my_bookings(username):
    fancy_section("RIWAYAT BOOKING")
    myb = [b for b in BOOKINGS.values() if b.get("username")==username]
    if not myb:
        print(color("Tidak ada booking.", "yellow"))
        return

    for b in myb:
        print(color(f"- {b['booking_id']} | {b['villa_name']}", "magenta"))
        print(f"  Status: {b['status']} | {b['checkin']} - {b['checkout']} | Total: Rp{int(b['final_total']):,}")
        print("-" * 58)

# ---------------------------
# USER MENU
# ---------------------------
def user_menu(username):
    while True:
        try:
            fancy_title(f"MENU USER - {username}")
            print("1. Cari & Booking Villa")
            print("2. Bayar Booking")
            print("3. Batalkan Booking")
            print("4. Berikan Review")
            print("5. Lihat Booking Saya")
            print("6. Lihat Review Villa")
            print("7. Hapus Akun")
            print("8. Logout")
            print("9. Hapus Review (milikmu)")

            c = safe_input("Pilih menu (nomor)", None, allow_empty=False)
            if c is None:
                continue

            if c == "1": start_booking_flow(username)
            elif c == "2": pay_booking_flow(username)
            elif c == "3": cancel_booking_flow(username)
            elif c == "4": give_review_flow(username)
            elif c == "5": view_my_bookings(username)
            elif c == "6": view_reviews_flow()
            elif c == "7":
                result = delete_account(username)
                if result == "LOGOUT":
                    break
            elif c == "8":
                print(color("Logout...", "yellow"))
                break
            elif c == "9":
                delete_review_flow(username)
            else:
                print(color("Pilihan salah.", "red"))
        except Exception as e:
            print(color("Terjadi error: " + str(e), "red"))
            print(color("Kembali ke menu user.", "yellow"))

# ---------------------------
# MAIN MENU
# ---------------------------
def main():
    while True:
        try:
            fancy_title("SISTEM BOOKING VILLA V4")
            print("1. Register")
            print("2. Login")
            print("3. Lupa Password")
            print("4. Lihat Review (Publik)")
            print("5. Keluar")

            c = safe_input("Pilih menu (nomor)", None, allow_empty=False)
            if c is None:
                continue

            if c == "1":
                register()
            elif c == "2":
                u = login()
                if u:
                    user_menu(u)
            elif c == "3":
                forgot_password()
            elif c == "4":
                view_reviews_flow()
            elif c == "5":
                print(color("Sampai jumpa!", "green"))
                break
            else:
                print(color("Pilihan salah.", "red"))
        except Exception as e:
            print(color("Terjadi error di main: " + str(e), "red"))
            print(color("Kembali ke menu utama.", "yellow"))

if __name__ == "__main__":
    main()
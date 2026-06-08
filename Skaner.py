import cv2
import os
import webbrowser
import threading
import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image
import numpy as np

# =========================================================
# BARCODE DETECTOR
# =========================================================
barcode_detector = cv2.barcode.BarcodeDetector()

# =========================================================
# GLOBAL
# =========================================================
processing = False
scanned_qr = set()
input_folder = "input_qr"

if not os.path.exists(input_folder):
    os.makedirs(input_folder)

# =========================================================
# DATABASE
# =========================================================
connection = sqlite3.connect("qr_database.db", check_same_thread=False)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS qr_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qr_text TEXT,
    scan_date TEXT,
    scan_time TEXT
)
""")
connection.commit()

# =========================================================
# HANDLE QR DATA (OPEN LINKS)
# =========================================================
def handle_qr_data(qr_text):
    qr_text = qr_text.strip()
    if qr_text == "":
        return

    open_link = None

    if "t.me/" in qr_text:
        open_link = "https://" + qr_text if not qr_text.startswith("http") else qr_text
    elif qr_text.startswith("tg://"):
        open_link = qr_text
    elif qr_text.startswith(("http://", "https://")):
        open_link = qr_text
    elif qr_text.startswith("www."):
        open_link = "https://" + qr_text

    if open_link:
        try:
            webbrowser.open(open_link)
        except Exception as e:
            print(f"[BROWSER ERROR] {e}")

# =========================================================
# SAVE SCAN
# =========================================================
def save_scan(unique_id, qr_text):
    if unique_id in scanned_qr:
        return
    scanned_qr.add(unique_id)

    current_datetime = datetime.now()
    scan_date = current_datetime.strftime("%Y-%m-%d")
    scan_time = current_datetime.strftime("%H:%M:%S")

    cursor.execute("INSERT INTO qr_codes (qr_text, scan_date, scan_time) VALUES (?, ?, ?)",
                   (qr_text, scan_date, scan_time))
    connection.commit()
    qr_id = cursor.lastrowid

    qr_table.insert("", 0, values=(qr_id, qr_text, scan_date, scan_time))
    handle_qr_data(qr_text)

# =========================================================
# LOAD IMAGE WITH GIF SUPPORT
# =========================================================
def load_image_as_cv2(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.gif':
        try:
            pil_img = Image.open(filepath)
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            img_np = np.array(pil_img)
            img_cv2 = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            return img_cv2
        except Exception as e:
            print(f"[GIF ERROR] {filepath}: {e}")
            return None
    else:
        return cv2.imread(filepath)

# =========================================================
# SCAN IMAGES IN FOLDER
# =========================================================
def scan_images_in_folder():
    global processing
    if processing:
        return

    processing = True
    status_label.config(text="STATUS: SCANNING...", fg="yellow")
    root.update()

    qr_detector = cv2.QRCodeDetector()
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')

    try:
        files = [f for f in os.listdir(input_folder) if f.lower().endswith(image_extensions)]
        if not files:
            messagebox.showinfo("Info", "Нет изображений в папке 'input_qr'")
            processing = False
            status_label.config(text="STATUS: READY", fg="white")
            return

        for filename in files:
            filepath = os.path.join(input_folder, filename)
            img = load_image_as_cv2(filepath)
            if img is None:
                continue

            # QR detection
            retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(img)
            if retval and points is not None:
                for i in range(len(decoded_info)):
                    qr_text = decoded_info[i].strip()
                    if qr_text:
                        unique_id = f"QR_{qr_text}"
                        save_scan(unique_id, qr_text)

            # Barcode detection
            try:
                ok, decoded_infos, decoded_types, _ = barcode_detector.detectAndDecode(img)
                if ok:
                    for i in range(len(decoded_infos)):
                        barcode_text = decoded_infos[i]
                        if barcode_text:
                            unique_id = f"{decoded_types[i]}_{barcode_text}"
                            save_scan(unique_id, f"[{decoded_types[i]}] {barcode_text}")
            except Exception as e:
                print(f"[BARCODE ERROR] {e}")

        messagebox.showinfo("Готово", f"Обработано файлов: {len(files)}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        processing = False
        status_label.config(text="STATUS: READY", fg="white")

# =========================================================
# GUI TABLE FUNCTIONS
# =========================================================
def add_qr_to_table(qr_id, qr_text, scan_date, scan_time):
    qr_table.insert("", 0, values=(qr_id, qr_text, scan_date, scan_time))

def load_all_qr():
    for item in qr_table.get_children():
        qr_table.delete(item)
    cursor.execute("SELECT * FROM qr_codes ORDER BY id DESC")
    for row in cursor.fetchall():
        add_qr_to_table(row[0], row[1], row[2], row[3])

def filter_qr(filter_type):
    for item in qr_table.get_children():
        qr_table.delete(item)

    if filter_type == "ALL":
        cursor.execute("SELECT * FROM qr_codes ORDER BY id DESC")
    elif filter_type == "TELEGRAM":
        cursor.execute("SELECT * FROM qr_codes WHERE qr_text LIKE '%t.me%' OR qr_text LIKE '%telegram%' OR qr_text LIKE '%tg://%' ORDER BY id DESC")
    elif filter_type == "URL":
        cursor.execute("SELECT * FROM qr_codes WHERE qr_text LIKE '%http%' OR qr_text LIKE '%www.%' ORDER BY id DESC")
    elif filter_type == "TEXT":
        cursor.execute("SELECT * FROM qr_codes WHERE qr_text NOT LIKE '%http%' AND qr_text NOT LIKE '%www.%' AND qr_text NOT LIKE '%t.me%' AND qr_text NOT LIKE '%tg://%' ORDER BY id DESC")
    else:
        return

    for row in cursor.fetchall():
        add_qr_to_table(row[0], row[1], row[2], row[3])

def search_qr():
    search_text = search_entry.get().strip()
    for item in qr_table.get_children():
        qr_table.delete(item)

    if search_text == "":
        cursor.execute("SELECT * FROM qr_codes ORDER BY id DESC")
    else:
        cursor.execute("SELECT * FROM qr_codes WHERE qr_text LIKE ? OR id LIKE ? OR scan_date LIKE ? OR scan_time LIKE ? ORDER BY id DESC",
                       (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
    for row in cursor.fetchall():
        add_qr_to_table(row[0], row[1], row[2], row[3])

def update_stats():
    cursor.execute("SELECT COUNT(*) FROM qr_codes")
    total_label.config(text=f"TOTAL\n{cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM qr_codes WHERE qr_text LIKE '%t.me%' OR qr_text LIKE '%telegram%' OR qr_text LIKE '%tg://%'")
    telegram_label.config(text=f"TELEGRAM\n{cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM qr_codes WHERE qr_text LIKE '%http%' OR qr_text LIKE '%www.%'")
    url_label.config(text=f"URL\n{cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM qr_codes WHERE qr_text NOT LIKE '%http%' AND qr_text NOT LIKE '%www.%' AND qr_text NOT LIKE '%t.me%' AND qr_text NOT LIKE '%tg://%'")
    text_label.config(text=f"TEXT\n{cursor.fetchone()[0]}")
    root.after(1000, update_stats)

def clear_history():
    cursor.execute("DELETE FROM qr_codes")
    connection.commit()
    scanned_qr.clear()
    load_all_qr()
    messagebox.showinfo("History", "История очищена")

def exit_program():
    connection.close()
    root.quit()
    root.destroy()
    os._exit(0)

# =========================================================
# GUI
# =========================================================
root = tk.Tk()
root.title("SMART QR SYSTEM (Folder Scanner)")
root.geometry("1320x760")
root.configure(bg="#1e1e1e")

title_label = tk.Label(root, text="SMART QR SYSTEM", font=("Arial", 26, "bold"), fg="cyan", bg="#1e1e1e")
title_label.pack(pady=15)

status_label = tk.Label(root, text="STATUS: READY", font=("Arial", 15), fg="white", bg="#1e1e1e")
status_label.pack(pady=5)

dashboard_frame = tk.Frame(root, bg="#1e1e1e")
dashboard_frame.pack(pady=15)

dashboard_style = {"font": ("Arial", 12, "bold"), "fg": "white", "width": 12, "height": 3}

total_label = tk.Label(dashboard_frame, text="TOTAL\n0", bg="#0078D7", **dashboard_style)
total_label.grid(row=0, column=0, padx=8)

telegram_label = tk.Label(dashboard_frame, text="TELEGRAM\n0", bg="#009688", **dashboard_style)
telegram_label.grid(row=0, column=1, padx=8)

url_label = tk.Label(dashboard_frame, text="URL\n0", bg="#FF9800", **dashboard_style)
url_label.grid(row=0, column=2, padx=8)

text_label = tk.Label(dashboard_frame, text="TEXT\n0", bg="#9C27B0", **dashboard_style)
text_label.grid(row=0, column=3, padx=8)

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

left_panel = tk.Frame(main_frame, bg="#1e1e1e")
left_panel.pack(side="left", fill="y", padx=(0, 20))

btn_style = {"font": ("Arial", 11, "bold"), "width": 20, "height": 1, "bg": "#333333", "fg": "white"}

tk.Button(left_panel, text="SCAN FOLDER", command=lambda: threading.Thread(target=scan_images_in_folder, daemon=True).start(), **btn_style).pack(pady=8)
tk.Button(left_panel, text="CLEAR HISTORY", command=clear_history, **btn_style).pack(pady=8)

exit_style = btn_style.copy()
exit_style["bg"] = "darkred"
tk.Button(left_panel, text="EXIT", command=exit_program, **exit_style).pack(pady=8)

right_panel = tk.Frame(main_frame, bg="#1e1e1e")
right_panel.pack(side="left", fill="both", expand=True)

search_frame = tk.Frame(right_panel, bg="#1e1e1e")
search_frame.pack(anchor="w", pady=5)

search_entry = tk.Entry(search_frame, font=("Arial", 13), width=40)
search_entry.pack(side="left", padx=(0, 10))

tk.Button(search_frame, text="SEARCH", command=search_qr, font=("Arial", 10, "bold"), bg="#444444", fg="white", width=12).pack(side="left")
search_entry.bind("<Return>", lambda e: search_qr())

filter_frame = tk.Frame(right_panel, bg="#1e1e1e")
filter_frame.pack(anchor="w", pady=10)

for text, value in [("ALL", "ALL"), ("TELEGRAM", "TELEGRAM"), ("URL", "URL"), ("TEXT", "TEXT")]:
    tk.Button(filter_frame, text=text, command=lambda v=value: filter_qr(v), font=("Arial", 10, "bold"), bg="#555555", fg="white", width=10).pack(side="left", padx=5)

table_frame = tk.Frame(right_panel)
table_frame.pack(fill="both", expand=True, pady=10)

scrollbar = tk.Scrollbar(table_frame)
scrollbar.pack(side="right", fill="y")

qr_table = ttk.Treeview(
    table_frame,
    columns=("ID", "QR_TEXT", "DATE", "TIME"),
    show="headings",
    height=20,
    yscrollcommand=scrollbar.set
)

qr_table.heading("ID", text="ID")
qr_table.heading("QR_TEXT", text="QR TEXT")
qr_table.heading("DATE", text="DATE")
qr_table.heading("TIME", text="TIME")

qr_table.column("ID", width=70)
qr_table.column("QR_TEXT", width=650)
qr_table.column("DATE", width=120)
qr_table.column("TIME", width=120)

qr_table.pack(fill="both", expand=True)
scrollbar.config(command=qr_table.yview)

load_all_qr()
update_stats()

root.mainloop()
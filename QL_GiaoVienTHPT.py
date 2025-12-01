import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime
import pyodbc
import pandas as pd  # Thêm thư viện để xuất Excel

# =============================================================================
# 1. KẾT NỐI VÀ CANH GIỮA
# =============================================================================
LUONG_CO_BAN = 1800000 

def ketnoi_database():
    conn_str = (
        r'DRIVER={SQL Server};'
        r'SERVER=ADMIN\SQLEXPRESS;'  
        r'DATABASE=QL_GiaoVien;'
        r'Trusted_Connection=yes;'
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi kết nối CSDL: {e}")
        return None

def center_window(win, w=1100, h=700):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

# =============================================================================
# 2. KHỞI TẠO GIAO DIỆN CHÍNH
# =============================================================================
root = tk.Tk()
root.title("HỆ THỐNG QUẢN LÝ GIÁO VIÊN THPT")
center_window(root, 1150, 720) 
root.resizable(False, False)
# Cấu hình style
style = ttk.Style()
style.theme_use('clam')  
style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[10, 5])
style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#d9edf7")
style.configure("Treeview", font=("Arial", 10), rowheight=25)

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Tạo 4 Tab
tab_trangchu = tk.Frame(notebook, bg="#f0f8ff")
tab_gv = tk.Frame(notebook)
tab_giangday = tk.Frame(notebook)
tab_luong = tk.Frame(notebook)

notebook.add(tab_trangchu, text="🏠 Trang chủ")
notebook.add(tab_gv, text="👨‍🏫 Quản lý Giáo viên")
notebook.add(tab_giangday, text="📚 Phân công Giảng dạy")
notebook.add(tab_luong, text="💰 Quản lý Lương")

# =============================================================================
# TAB 1: TRANG CHỦ 
# =============================================================================
lbl_header = tk.Label(tab_trangchu, text="HỆ THỐNG QUẢN LÝ\nGIÁO VIÊN THPT", 
                      font=("Arial", 40, "bold"), fg="#0056b3", bg="#f0f8ff")
lbl_header.place(relx=0.5, rely=0.4, anchor="center")

lbl_sv = tk.Label(tab_trangchu, text="Người thực hiện:\n1. Đỗ Thị Ánh Nhung - DPM245470\n2. Lê Nguyễn Quỳnh Phương - DPM245478", 
                  font=("Arial", 12, "italic"), bg="#f0f8ff", justify="left", fg="#555")
lbl_sv.place(relx=0.0, rely=1.0, x=20, y=-20, anchor="sw")

# =============================================================================
# TAB 2: THÔNG TIN GIÁO VIÊN 
# =============================================================================
def format_phone(sdt):
    sdt = str(sdt)
    if sdt and sdt != 'None':
        # Nếu là số và thiếu số 0 ở đầu (độ dài < 10 và không bắt đầu bằng 0)
        if sdt.isdigit() and len(sdt) < 10 and not sdt.startswith('0'):
            return '0' + sdt
    return sdt

def load_data_gv():
    for i in tree_gv.get_children(): tree_gv.delete(i)
    conn = ketnoi_database()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT MAGV, HoLot, Ten, NgaySinh, GioiTinh, DiaChi, SDT, Email, TrinhDo, ChucVu FROM GiaoVien")
            for r in cur.fetchall():
                row = list(r)
                # --- XỬ LÝ FORMAT NGÀY SINH ---
                if row[3]:
                    val = str(row[3]) # Ép dữ liệu về chuỗi '1990-02-15'
                    try:
                        d = datetime.strptime(val, '%Y-%m-%d')
                        row[3] = d.strftime('%d/%m/%Y')
                    except: pass
                # --------------------

                # Xử lý format Số điện thoại
                row[6] = format_phone(row[6])

                tree_gv.insert("", tk.END, values=row)
            load_combobox_gv_all() 
        finally:
            conn.close()
def get_gv_input():
    ma = entry_ma.get().strip()
    ho = entry_ho.get().strip()
    ten = entry_ten.get().strip()
    try: ns = date_ns.get_date().strftime('%Y-%m-%d')
    except: ns = None
    phai = var_phai.get()
    dc = entry_dc.get().strip()
    sdt = entry_sdt.get().strip()
    email = entry_email.get().strip()
    td = cbb_trinhdo.get()
    cv = cbb_chucvu.get()
    return (ma, ho, ten, ns, phai, dc, sdt, email, td, cv)

def them_gv():
    data = get_gv_input()
    if not data[0] or not data[2]:
        messagebox.showwarning("Cảnh báo", "Mã GV và Tên không được để trống!")
        return
    conn = ketnoi_database()
    if conn:
        try:
            conn.cursor().execute("INSERT INTO GiaoVien(MAGV, HoLot, Ten, NgaySinh, GioiTinh, DiaChi, SDT, Email, TrinhDo, ChucVu) VALUES (?,?,?,?,?,?,?,?,?,?)", data)
            conn.commit(); messagebox.showinfo("Thành công","Thêm giáo viên thành công!")
            load_data_gv(); clear_gv()
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

def sua_gv():
    data = get_gv_input()
    ma = entry_ma.get()
    if not ma: return
    conn = ketnoi_database()
    if conn:
        try:
            params = data[1:] + (ma,)
            sql = "UPDATE GiaoVien SET HoLot=?, Ten=?, NgaySinh=?, GioiTinh=?, DiaChi=?, SDT=?, Email=?, TrinhDo=?, ChucVu=? WHERE MAGV=?"
            conn.cursor().execute(sql, params)
            conn.commit(); messagebox.showinfo("Thành công","Cập nhật thông tin thành công!"); 
            load_data_gv(); clear_gv()
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

def xoa_gv():
    ma = entry_ma.get()
    if ma and messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa giáo viên này và toàn bộ dữ liệu liên quan?"):
        conn = ketnoi_database()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM GiangDay WHERE MAGV=?", (ma,))
                cur.execute("DELETE FROM Luong WHERE MAGV=?", (ma,))
                cur.execute("DELETE FROM GiaoVien WHERE MAGV=?", (ma,))
                conn.commit(); messagebox.showinfo("Thành công","Đã xóa!"); 
                load_data_gv(); clear_gv()
            except Exception as e: messagebox.showerror("Lỗi", str(e))
            finally: conn.close()

def clear_gv():
    entry_ma.config(state="normal")
    entry_ma.delete(0, tk.END)
    entry_ho.delete(0, tk.END) 
    entry_ten.delete(0, tk.END)
    entry_dc.delete(0, tk.END)
    entry_sdt.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    date_ns.set_date(datetime.today())
    var_phai.set("Nam")
    cbb_trinhdo.current(0)
    cbb_chucvu.current(0)

    entry_search.delete(0, tk.END)
    load_data_gv()
    
    entry_ma.focus()

def chon_dong_gv(event):
    selected = tree_gv.selection()
    if selected:
        row = tree_gv.item(selected)['values']
        
        entry_ma.config(state="normal")
        entry_ma.delete(0, tk.END)
        entry_ho.delete(0, tk.END)
        entry_ten.delete(0, tk.END)
        entry_dc.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        
        entry_ma.insert(0, row[0])
        entry_ma.config(state="readonly") 
        
        entry_ho.insert(0, row[1])
        entry_ten.insert(0, row[2])
        
        # --- XỬ LÝ NGÀY SINH ---
        ngay_sinh_str = str(row[3]).strip() # Lấy chuỗi ngày, cắt khoảng trắng thừa
        if ngay_sinh_str and ngay_sinh_str != 'None':
            # Trường hợp 1: Định dạng DD/MM/YYYY (Ví dụ: 30/05/2000)
            try:
                d = datetime.strptime(ngay_sinh_str, '%d/%m/%Y')
                date_ns.set_date(d)
            except ValueError:
                # Trường hợp 2: Định dạng YYYY-MM-DD (Ví dụ: 2000-05-30 - Lỗi do SQL chưa format)
                try:
                    d = datetime.strptime(ngay_sinh_str, '%Y-%m-%d')
                    date_ns.set_date(d)
                except ValueError:
                    pass 
        
        var_phai.set(row[4])
        entry_dc.insert(0, row[5])
        
        # Xử lý SĐT
        sdt_str = format_phone(row[6])
        entry_sdt.insert(0, sdt_str)
        
        entry_email.insert(0, row[7])
        cbb_trinhdo.set(row[8])
        cbb_chucvu.set(row[9])

def tim_gv():
    ten = entry_search.get().strip()
    if not ten:
        load_data_gv()
        return

    # Xóa dữ liệu cũ trên cây
    for row in tree_gv.get_children():
        tree_gv.delete(row)

    conn = ketnoi_database()
    if conn:
        try:
            cur = conn.cursor()
            # Tìm kiếm gần đúng theo Tên
            query = "SELECT MAGV, HoLot, Ten, NgaySinh, GioiTinh, DiaChi, SDT, Email, TrinhDo, ChucVu FROM GiaoVien WHERE Ten LIKE ?"
            cur.execute(query, ('%' + ten + '%',))

            for r in cur.fetchall():
                row = list(r)
                if row[3]:
                    try: row[3] = row[3].strftime('%d/%m/%Y')
                    except: pass
                
                row[6] = format_phone(row[6])
                
                tree_gv.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            conn.close()

def xuat_excel_gv():
    conn = ketnoi_database()
    if conn:
        try:
            query = "SELECT MAGV, HoLot, Ten, NgaySinh, GioiTinh, DiaChi, SDT, Email, TrinhDo, ChucVu FROM GiaoVien"
            df = pd.read_sql(query, conn)
            # (ép về chuỗi để giữ số 0)
            df['SDT'] = df['SDT'].apply(lambda x: format_phone(x))
            
            path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if path:
                df.to_excel(path, index=False)
                messagebox.showinfo("Xuất Excel", f"Đã xuất file thành công tại:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi Xuất File", str(e))
        finally:
            conn.close()

def thoat_chuong_trinh():
    if messagebox.askokcancel("Thoát", "Bạn có muốn thoát chương trình?"):
        root.destroy()

# --- GUI Tab GV ---
fr_info = tk.LabelFrame(tab_gv, text="Thông tin chi tiết", font=("Arial", 10, "bold"), fg="#2E86C1", padx=10, pady=10)
fr_info.pack(fill="x", padx=15, pady=10)

tk.Label(fr_info, text="Mã GV:").grid(row=0, column=0, sticky="e", pady=5)
entry_ma = tk.Entry(fr_info, width=15)
entry_ma.grid(row=0, column=1, sticky="w", padx=5)

tk.Label(fr_info, text="Họ lót:").grid(row=0, column=2, sticky="e", pady=5)
entry_ho = tk.Entry(fr_info, width=20)
entry_ho.grid(row=0, column=3, sticky="w", padx=5)

tk.Label(fr_info, text="Tên:").grid(row=0, column=4, sticky="e", pady=5)
entry_ten = tk.Entry(fr_info, width=15)
entry_ten.grid(row=0, column=5, sticky="w", padx=5)

tk.Label(fr_info, text="Giới tính:").grid(row=0, column=6, sticky="e", pady=5)
fr_phai = tk.Frame(fr_info)
fr_phai.grid(row=0, column=7, sticky="w", padx=5)
var_phai = tk.StringVar(value="Nam")
tk.Radiobutton(fr_phai, text="Nam", variable=var_phai, value="Nam").pack(side="left")
tk.Radiobutton(fr_phai, text="Nữ", variable=var_phai, value="Nữ").pack(side="left")

tk.Label(fr_info, text="Ngày sinh:").grid(row=1, column=0, sticky="e", pady=5)
date_ns = DateEntry(fr_info, width=12, background='darkblue',
                    foreground='white', borderwidth=2, 
                    date_pattern='dd/mm/yyyy') 
date_ns.grid(row=1, column=1, sticky="w", padx=5)

tk.Label(fr_info, text="SĐT:").grid(row=1, column=2, sticky="e", pady=5)
entry_sdt = tk.Entry(fr_info, width=20)
entry_sdt.grid(row=1, column=3, sticky="w", padx=5)

tk.Label(fr_info, text="Email:").grid(row=1, column=4, sticky="e", pady=5)
entry_email = tk.Entry(fr_info, width=25)
entry_email.grid(row=1, column=5, columnspan=3, sticky="w", padx=5)

tk.Label(fr_info, text="Trình độ:").grid(row=2, column=0, sticky="e", pady=5)
cbb_trinhdo = ttk.Combobox(fr_info, width=12, state="readonly", values=["Cử nhân", "Thạc sĩ", "Tiến sĩ"])
cbb_trinhdo.current(0)
cbb_trinhdo.grid(row=2, column=1, sticky="w", padx=5)

tk.Label(fr_info, text="Chức vụ:").grid(row=2, column=2, sticky="e", pady=5)
cbb_chucvu = ttk.Combobox(fr_info, width=17, state="readonly", values=["Giáo viên", "Tổ trưởng", "Hiệu phó", "Hiệu trưởng", "Nhân viên"])
cbb_chucvu.current(0)
cbb_chucvu.grid(row=2, column=3, sticky="w", padx=5)

tk.Label(fr_info, text="Địa chỉ:").grid(row=2, column=4, sticky="e", pady=5)
entry_dc = tk.Entry(fr_info, width=40)
entry_dc.grid(row=2, column=5, columnspan=3, sticky="w", padx=5)

# Frame Button
fr_btn = tk.Frame(tab_gv)
fr_btn.pack(pady=10)

btn_them_gv = tk.Button(fr_btn, text="Thêm", command=them_gv, bg="#28a745", 
                        fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_them_gv.pack(side="left", padx=5)

btn_luu_gv = tk.Button(fr_btn, text="Lưu/Sửa", command=sua_gv,bg="#ffc107", 
                       fg="white",font=("Arial", 10, "bold"),width=12, relief="raised", bd=3)
btn_luu_gv.pack(side="left", padx=5)

btn_xoa_gv = tk.Button(fr_btn, text="Xóa", command=xoa_gv,bg="#dc3545", 
                    fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_xoa_gv.pack(side="left", padx=5)

btn_clear_gv = tk.Button(fr_btn, text="Làm mới", command=clear_gv, bg="#17a2b8", 
                      fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_clear_gv.pack(side="left", padx=5)

btn_excel_gv = tk.Button(fr_btn, text="Xuất Excel", command=xuat_excel_gv, bg="#207245", 
                      fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)  
btn_excel_gv.pack(side="left", padx=20)

btn_thoat = tk.Button(fr_btn, text="Thoát", command=thoat_chuong_trinh, bg="#6c757d", 
                      fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_thoat.pack(side="left", padx=5)

# ==== KHUNG TÌM KIẾM ====
fr_search = tk.Frame(tab_gv)
fr_search.pack(fill="x", padx=10, pady=5)

tk.Label(fr_search, text="Tìm theo tên:").pack(side="left", padx=5)
entry_search = tk.Entry(fr_search, width=30)
entry_search.pack(side="left", padx=5)

tk.Button(fr_search, text="Tìm", bg="#17a2b8", fg="white",
          font=("Arial", 10, "bold"), command=tim_gv).pack(side="left", padx=5)


# Treeview
cols_gv = ("MAGV", "HoLot", "Ten", "NgaySinh", "GioiTinh", "DiaChi", "SDT", "Email", "TrinhDo", "ChucVu")
tree_gv = ttk.Treeview(tab_gv, columns=cols_gv, show="headings", height=12)

# 1. Đặt tên tiêu đề 
header_name = ["Mã GV", "Họ Lót", "Tên", "Ngày Sinh", "Giới Tính", "Địa Chỉ", "SĐT", "Email", "Trình Độ", "Chức Vụ"]
for i, c in enumerate(cols_gv):
    tree_gv.heading(c, text=header_name[i])

# 2. Cấu hình chi tiết từng cột
tree_gv.column("MAGV",     width=60,  anchor="center") 
tree_gv.column("HoLot",    width=130, anchor="w")     
tree_gv.column("Ten",      width=70,  anchor="w")     
tree_gv.column("NgaySinh", width=90,  anchor="center") 
tree_gv.column("GioiTinh", width=60,  anchor="center")
tree_gv.column("DiaChi",   width=200, anchor="w")      
tree_gv.column("SDT",      width=100, anchor="center")
tree_gv.column("Email",    width=150, anchor="w")
tree_gv.column("TrinhDo",  width=90,  anchor="center")
tree_gv.column("ChucVu",   width=100, anchor="center")

scrol_y = ttk.Scrollbar(tab_gv, orient="vertical", command=tree_gv.yview)
tree_gv.configure(yscroll=scrol_y.set)
scrol_y.pack(side="right", fill="y", pady=5)
tree_gv.pack(fill="both", expand=True, padx=15, pady=5)
tree_gv.bind("<<TreeviewSelect>>", chon_dong_gv) 

# =============================================================================
# TAB 3: GIẢNG DẠY 
# =============================================================================
list_gv_combo = []

def load_combobox_gv_all():
    conn = ketnoi_database()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT MAGV, HoLot, Ten FROM GiaoVien")
            list_gv_combo.clear()
            data = []
            for r in cur.fetchall():
                val = f"{r[0]} - {r[1]} {r[2]}"
                list_gv_combo.append(val)
                data.append(val)
            cbb_gd_magv['values'] = data
            cbb_luong_magv['values'] = data
        except: pass
        finally: conn.close()

def load_data_gd():
    for i in tree_gd.get_children(): tree_gd.delete(i)
    conn = ketnoi_database()
    if conn:
        try:
            cur = conn.cursor()
            sql = """SELECT GD.ID, GV.HoLot+' '+GV.Ten, GD.MonHoc, GD.LopPhuTrach, GD.ToCongTac, GD.SoTietTuan 
                     FROM GiangDay GD JOIN GiaoVien GV ON GD.MAGV=GV.MAGV"""
            cur.execute(sql)
            for row in cur.fetchall(): tree_gd.insert("", tk.END, values=list(row))
        except: pass
        finally: conn.close()

def them_gd():
    gv_str = cbb_gd_magv.get()
    if not gv_str: return
    magv = gv_str.split(' - ')[0]
    data = (magv, cbb_gd_mon.get(), entry_gd_lop.get(), cbb_gd_to.get(), entry_gd_tiet.get())
    conn = ketnoi_database()
    if conn:
        try:
            conn.cursor().execute("INSERT INTO GiangDay VALUES (?,?,?,?,?)", data)
            conn.commit(); messagebox.showinfo("OK", "Thêm thành công!"); 
            load_data_gd(); clear_gd()
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

def sua_gd():
    sel = tree_gd.selection()
    if not sel: return
    id_row = tree_gd.item(sel)['values'][0]
    gv_str = cbb_gd_magv.get()
    magv = gv_str.split(' - ')[0] if gv_str else None
    conn = ketnoi_database()
    if conn:
        try:
            sql = "UPDATE GiangDay SET MAGV=?, MonHoc=?, LopPhuTrach=?, ToCongTac=?, SoTietTuan=? WHERE ID=?"
            conn.cursor().execute(sql, (magv, cbb_gd_mon.get(), entry_gd_lop.get(), cbb_gd_to.get(), entry_gd_tiet.get(), id_row))
            conn.commit(); messagebox.showinfo("OK", "Cập nhật xong!"); 
            load_data_gd(); clear_gd()
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

def xoa_gd():
    sel = tree_gd.selection()
    if sel and messagebox.askyesno("Xóa", "Xóa thông tin này?"):
        id_row = tree_gd.item(sel)['values'][0]
        conn = ketnoi_database()
        if conn:
            conn.cursor().execute("DELETE FROM GiangDay WHERE ID=?", (id_row,))
            conn.commit(); conn.close(); 
            load_data_gd(); clear_gd()

def clear_gd():
    cbb_gd_magv.set(''); cbb_gd_mon.delete(0, tk.END); entry_gd_lop.delete(0, tk.END)
    cbb_gd_to.delete(0, tk.END); entry_gd_tiet.delete(0, tk.END)
    load_data_gd()

def chon_dong_gd(e):
    sel = tree_gd.selection()
    if sel:
        r = tree_gd.item(sel)['values']
        ten_gv = str(r[1])
        for item in list_gv_combo:
            if ten_gv in item: cbb_gd_magv.set(item); break
        cbb_gd_mon.delete(0, tk.END)
        cbb_gd_mon.set(r[2])
        entry_gd_lop.delete(0, tk.END)
        entry_gd_lop.insert(0, r[3])
        cbb_gd_to.delete(0, tk.END)
        cbb_gd_to.set(r[4])
        entry_gd_tiet.delete(0, tk.END)
        entry_gd_tiet.insert(0, r[5])

# GUI TAB 2
fr_gd_info = tk.LabelFrame(tab_giangday, text="Thông tin Phân công", font=("Arial", 10, "bold"), fg="#D35400", padx=10, pady=10)
fr_gd_info.pack(fill="x", padx=15, pady=10)

tk.Label(fr_gd_info, text="Giáo viên:").grid(row=0, column=0, sticky="e", pady=5)
cbb_gd_magv = ttk.Combobox(fr_gd_info, width=30, state="readonly")
cbb_gd_magv.grid(row=0, column=1, columnspan=2, sticky="w", padx=5)

tk.Label(fr_gd_info, text="Môn dạy:").grid(row=0, column=3, sticky="e", pady=5)
cbb_gd_mon = ttk.Combobox(fr_gd_info, width=17, state="readonly", values=[
    "Toán", "Vật lí", "Hóa học", "Sinh học", "Tin học", 
    "Ngữ văn", "Lịch sử", "Địa lí", "Tiếng Anh", 
    "GDCD", "GDTC (Thể dục)", "GDQP-AN", "Công nghệ", 
])
cbb_gd_mon.grid(row=0, column=4, sticky="w", padx=5)

tk.Label(fr_gd_info, text="Lớp phụ trách:").grid(row=1, column=0, sticky="e", pady=5)
entry_gd_lop = tk.Entry(fr_gd_info, width=15)
entry_gd_lop.grid(row=1, column=1, sticky="w", padx=5)

tk.Label(fr_gd_info, text="Tổ bộ môn:").grid(row=1, column=2, sticky="e", pady=5)
cbb_gd_to = ttk.Combobox(fr_gd_info, width=17, state="readonly", values= ["Toán - Tin", "Lý - CN", "Xã hội", "Ngữ văn", "Ngoại ngữ", "TD - QP", "Hóa - Sinh"])
cbb_gd_to.grid(row=1, column=3, sticky="w", padx=5) 

tk.Label(fr_gd_info, text="Số tiết/tuần:").grid(row=1, column=4, sticky="e", pady=5)
entry_gd_tiet = tk.Entry(fr_gd_info, width=10)
entry_gd_tiet.grid(row=1, column=5, sticky="w", padx=5)

fr_btn2 = tk.Frame(tab_giangday)
fr_btn2.pack(pady=5)
btn_them_gd = tk.Button(fr_btn2, text="Thêm", command=them_gd, bg="#28a745",
                        fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_them_gd.pack(side="left", padx=5)

btn_luu_gd = tk.Button(fr_btn2, text="Lưu", command=sua_gd, bg="#ffc107", 
                       fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_luu_gd.pack(side="left", padx=5)

btn_xoa_gd = tk.Button(fr_btn2, text="Xóa", command=xoa_gd, bg="#dc3545", 
                       fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_xoa_gd.pack(side="left", padx=5)

btn_moi_gd = tk.Button(fr_btn2, text="Mới", command=clear_gd, bg="#17a2b8", 
                       fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_moi_gd.pack(side="left", padx=5)

# --- Treeview ---
cols_gd = ("ID", "GV", "MON", "LOP", "TO", "TIET")
tree_gd = ttk.Treeview(tab_giangday, columns=cols_gd, show="headings", height=12)

# 1. Đặt tên tiêu đề
h2 = ["ID", "Giáo viên", "Môn dạy", "Lớp phụ trách", "Tổ bộ môn", "Số tiết"]
for i, c in enumerate(cols_gd): 
    tree_gd.heading(c, text=h2[i])

# 2. Cấu hình chi tiết từng cột
tree_gd.column("ID",   width=40,  anchor="center")
tree_gd.column("GV",   width=180, anchor="w")     
tree_gd.column("MON",  width=100, anchor="center") 
tree_gd.column("LOP",  width=80,  anchor="center") 
tree_gd.column("TO",   width=120, anchor="center") 
tree_gd.column("TIET", width=80,  anchor="center") 

tree_gd.pack(fill="both", expand=True, padx=15, pady=5)
tree_gd.bind("<<TreeviewSelect>>", chon_dong_gd)

# =============================================================================
# TAB 4: LƯƠNG 
# =============================================================================
def load_data_luong():
    for i in tree_luong.get_children(): tree_luong.delete(i)
    conn = ketnoi_database()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT L.ID, GV.HoLot+' '+GV.Ten, L.HeSoLuong, L.BacLuong, L.PhuCap, L.Thuong FROM Luong L JOIN GiaoVien GV ON L.MAGV=GV.MAGV")
            for row in cur.fetchall():
                r = list(row)
                thuc_lanh = (r[2] * LUONG_CO_BAN) + r[4] + r[5]
                r.append("{:,.0f} VNĐ".format(thuc_lanh))
                tree_luong.insert("", tk.END, values=r)
        except: pass
        finally: conn.close()

def luu_luong():
    gv_str = cbb_luong_magv.get()
    if not gv_str: messagebox.showwarning("Lỗi", "Chưa chọn giáo viên!"); return
    magv = gv_str.split(' - ')[0]
    data = (magv, entry_heso.get(), entry_bac.get(), entry_phucap.get(), entry_thuong.get())
    
    conn = ketnoi_database()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT ID FROM Luong WHERE MAGV=?", (magv,))
            if cur.fetchone(): 
                sql = "UPDATE Luong SET HeSoLuong=?, BacLuong=?, PhuCap=?, Thuong=? WHERE MAGV=?"
                cur.execute(sql, (data[1], data[2], data[3], data[4], magv))
            else:
                sql = "INSERT INTO Luong (MAGV, HeSoLuong, BacLuong, PhuCap, Thuong) VALUES (?,?,?,?,?)"
                cur.execute(sql, data)
            conn.commit(); messagebox.showinfo("OK", "Đã tính lương xong!"); 
            load_data_luong(); clear_luong()
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

def xoa_luong():
    sel = tree_luong.selection()
    if sel and messagebox.askyesno("Xóa", "Xóa bảng lương này?"):
        id_row = tree_luong.item(sel)['values'][0]
        conn = ketnoi_database()
        if conn:
            conn.cursor().execute("DELETE FROM Luong WHERE ID=?", (id_row,))
            conn.commit(); conn.close(); load_data_luong(); clear_luong()

def clear_luong():
    cbb_luong_magv.set('')
    entry_heso.delete(0, tk.END)
    entry_bac.delete(0, tk.END)
    entry_phucap.delete(0, tk.END)
    entry_thuong.delete(0, tk.END)
    load_data_luong()

# --- HÀM XUẤT EXCEL LƯƠNG ---
def xuat_excel_luong():
    conn = ketnoi_database()
    if conn:
        try:
            sql = """
            SELECT GV.MAGV, GV.HoLot + ' ' + GV.Ten AS HoTen, 
                   L.HeSoLuong, L.BacLuong, L.PhuCap, L.Thuong
            FROM Luong L 
            JOIN GiaoVien GV ON L.MAGV = GV.MAGV
            """
            df = pd.read_sql(sql, conn)
            # Tính lại cột Thực Lãnh để ghi vào Excel
            df['ThucLanh'] = (df['HeSoLuong'] * LUONG_CO_BAN) + df['PhuCap'] + df['Thuong']
            df.columns = ['Mã GV', 'Họ Tên', 'Hệ Số', 'Bậc', 'Phụ Cấp', 'Thưởng', 'Thực Lãnh']
            
            path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Xuất Bảng Lương")
            if path:
                df.to_excel(path, index=False)
                messagebox.showinfo("Thành công", f"Đã xuất file tại: {path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

def chon_dong_luong(e):
    sel = tree_luong.selection()
    if sel:
        r = tree_luong.item(sel)['values']
        ten_gv = str(r[1])
        for item in list_gv_combo:
            if ten_gv in item: cbb_luong_magv.set(item); break
        entry_heso.delete(0, tk.END)
        entry_heso.insert(0, r[2])
        entry_bac.delete(0, tk.END)
        entry_bac.insert(0, r[3])
        entry_phucap.delete(0, tk.END)
        entry_phucap.insert(0, str(r[4]).replace('.0',''))
        entry_thuong.delete(0, tk.END)
        entry_thuong.insert(0, str(r[5]).replace('.0',''))

# GUI TAB 3 
fr_luong_info = tk.LabelFrame(tab_luong, text="Tính Lương Chi Tiết", font=("Arial", 10, "bold"), fg="#27AE60", padx=10, pady=10)
fr_luong_info.pack(fill="x", padx=15, pady=10)

tk.Label(fr_luong_info, text="Giáo viên:").grid(row=0, column=0, sticky="e", pady=5)
cbb_luong_magv = ttk.Combobox(fr_luong_info, width=30, state="readonly")
cbb_luong_magv.grid(row=0, column=1, columnspan=2, sticky="w", padx=5)

tk.Label(fr_luong_info, text="Hệ số:").grid(row=1, column=0, sticky="e", pady=5)
entry_heso = tk.Entry(fr_luong_info, width=10)
entry_heso.grid(row=1, column=1, sticky="w", padx=5)

tk.Label(fr_luong_info, text="Bậc lương:").grid(row=1, column=2, sticky="e", pady=5)
entry_bac = tk.Entry(fr_luong_info, width=10)
entry_bac.grid(row=1, column=3, sticky="w", padx=5)

tk.Label(fr_luong_info, text="Phụ cấp:").grid(row=2, column=0, sticky="e", pady=5)
entry_phucap = tk.Entry(fr_luong_info, width=15)
entry_phucap.grid(row=2, column=1, sticky="w", padx=5)

tk.Label(fr_luong_info, text="Thưởng:").grid(row=2, column=2, sticky="e", pady=5)
entry_thuong = tk.Entry(fr_luong_info, width=15)
entry_thuong.grid(row=2, column=3, sticky="w", padx=5)

fr_btn3 = tk.Frame(tab_luong)
fr_btn3.pack(pady=5)
btn_tinhluu = tk.Button(fr_btn3, text="Tính & Lưu", command=luu_luong, bg="#27AE60", 
                        fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_tinhluu.pack(side="left", padx=5)

btn_xoa_luong = tk.Button(fr_btn3, text="Xóa", command=xoa_luong, bg="#dc3545", 
                          fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_xoa_luong.pack(side="left", padx=5)

btn_lammo_luong = tk.Button(fr_btn3, text="Làm mới", command=clear_luong, bg="#17a2b8", 
                            fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_lammo_luong.pack(side="left", padx=5)

btn_excel_luong = tk.Button(fr_btn3, text="Xuất Excel", command=xuat_excel_luong, bg="#207245", 
                            fg="white", font=("Arial", 10, "bold"), width=12, relief="raised", bd=3)
btn_excel_luong.pack(side="left", padx=20)

# --- Treeview---
cols_l = ("ID", "GV", "HESO", "BAC", "PHUCAP", "THUONG", "THUC")
tree_luong = ttk.Treeview(tab_luong, columns=cols_l, show="headings", height=12)

# 1. Đặt tên tiêu đề
h3 = ["ID", "Giáo viên", "Hệ số", "Bậc", "Phụ cấp", "Thưởng", "THỰC LÃNH"]
for i, c in enumerate(cols_l): 
    tree_luong.heading(c, text=h3[i])

# 2. Cấu hình chi tiết từng cột
tree_luong.column("ID",     width=40,  anchor="center")
tree_luong.column("GV",     width=180, anchor="w")     
tree_luong.column("HESO",   width=60,  anchor="center") 
tree_luong.column("BAC",    width=50,  anchor="center")
tree_luong.column("PHUCAP", width=100, anchor="e")    
tree_luong.column("THUONG", width=100, anchor="e")     
tree_luong.column("THUC",   width=140, anchor="e")   
tree_luong.pack(fill="both", expand=True, padx=15, pady=5)
tree_luong.bind("<<TreeviewSelect>>", chon_dong_luong)

# =============================================================================
# MAIN LOOP
# =============================================================================
if __name__ == "__main__":
    load_data_gv()
    load_data_gd()
    load_data_luong()
    load_combobox_gv_all()
    root.mainloop()
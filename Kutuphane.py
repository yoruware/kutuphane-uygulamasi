from tkinter import *
from PIL import Image, ImageTk
import sqlite3
from tkinter import ttk
from tkinter import messagebox
import pyodbc
import tkinter.font as tkFont


conn = pyodbc.connect(
    'DRIVER={SQL Server};'                    # MSSQL icin Driver ismi genellikle SQL Server'dir, diğer serverlara göre değişkenlik gösterebilir.
    'SERVER=DESKTOP-73TL06M\SQLEXPRESS;'      # SQL Serverinizin adı veya IP adresi (kendinize göre değiştirmelisiniz)
    'DATABASE=Kutuphane;'                     # Veritabanınızın adı
    'Trusted_Connection=yes;'
)

#Pencere Oluşturma
pencere = Tk()
pencere.title("KUTUPHANE")
pencere.geometry("1215x650")
pencere.configure(bg="lightblue")


#İmleçle yapılacak işlemler için kod??
cursor = conn.cursor()
cursor.execute("SELECT * FROM KitapListesi") 
rows = cursor.fetchall()


#TkFont ile yazı tipi ayarlanması
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family="Helvetica", size=12)





label = Label(pencere, text="HOŞ GELDİNİZ", font=("Verdana", 20), bg="lightblue", fg="white", justify="center") 
#label statik metin veya resimler için kullanılır.
label.pack(side="top") 


# Treeview modülünü kullanarak tablo oluşturuyoruz
sutunlar = [isimbul[0] for isimbul in cursor.description]  
# pyodbc ile bir SQL sorgusu (SELECT ...) çalıştığında, cursor.description bize sorgudan dönen sütunların bilgilerini verir.
# Bu description listesi, her sütun için bir tuple tutar. O tuple’ın ilk elemanı sütunun adı olur.
# isimbul[0] → her sütun bilgisinin ilk elemanı, yani sütun adı

frame = Frame(pencere)
frame.pack(fill="x", pady=10)
frame.configure(bg="lightblue")


tree = ttk.Treeview(frame, columns=sutunlar, show="headings")

scroll=Scrollbar(frame, command=tree.yview)
scroll.pack(side="right", fill=Y)
tree.config(yscrollcommand=scroll.set)

# Sütun başlıklarını databaseden cekme
for col in sutunlar:
    tree.heading(col, text=col)
    tree.column(col, width=140)
tree.pack(side="left", expand=True)

def hepsi():
    # Önce Treeview içini temizleriz.
    for i in tree.get_children():
        tree.delete(i)

    cursor.execute('SELECT * FROM KitapListesi')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])   
        #Tabloya yazılacak değerleri databaseden alıyoruz. values kısmı none değerlerinde treeview yapısının hata vermemesi için.


def kitapEkle():
    yenipen = Toplevel(pencere)
    yenipen.title("Yeni Kitap Ekle")
    yenipen.geometry("220x300")

    entries = {}
    for i, col in enumerate(sutunlar):
        Label(yenipen, text=col).grid(row=i, column=0, sticky='w', padx=5, pady=2)
        entry = Entry(yenipen)
        entry.grid(row=i, column=1, padx=5, pady=2)
        entries[col] = entry


    def ekle():
        values = []
        for col in sutunlar:
            val = entries[col].get()
            if val == "":
                messagebox.showerror("Hata", f"{col} boş bırakılamaz!")
                return
            values.append(val)

        kolonlar = ', '.join(sutunlar)
        placeholders = ', '.join('?' for _ in sutunlar)
        sql = f"INSERT INTO KitapListesi ({kolonlar}) VALUES ({placeholders})"

        try:
            cursor.execute(sql, values)
            conn.commit()
            messagebox.showinfo("Başarılı", "Kitap eklendi!")
            hepsi()
            yenipen.destroy()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    btn = Button(yenipen, text="Ekle", command=ekle)
    btn.grid(row=len(sutunlar), column=0, columnspan=2, pady=10)

def kitapSil():
    secim = tree.selection()
    if not secim:
        messagebox.showwarning("Uyarı", "Lütfen silmek için bir kitap seçin!")
        return

    # Seçilen ilk item id'sini al
    item = secim[0]
    values = tree.item(item, 'values')
    
    # Birincil anahtar sütununu bul (örneğin ilk sütun KitapID)
    kitap_id = values[0]  

    cevap = messagebox.askyesno("Onay", f"KitapID {kitap_id} olan kitabı silmek istediğine emin misin?")
    if not cevap:
        return

    try:
        cursor.execute("DELETE FROM KitapListesi WHERE ID = ?", (kitap_id,))
        conn.commit()
        messagebox.showinfo("Başarılı", "Kitap silindi!")
        hepsi()
    except Exception as e:
        messagebox.showerror("Hata", str(e))


def enIyiler():
    cursor.execute('select top 10 * from KitapListesi where Puan>=7')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])



# Arama fonksiyonu
def kitap_ara():
    kelime = entry_ara.get()
    for i in tree.get_children():
        tree.delete(i)
    
    sql = "SELECT * FROM KitapListesi WHERE KitapAdi LIKE ? or Yazar like ? or Tur like ?"
    girdi = '%' + kelime + '%'
    girdiler = (girdi, girdi, girdi)  # Aynı girdiyi üç defa kullanabilmek için
    cursor.execute(sql, girdiler)
    rows = cursor.fetchall()

    for row in rows:
        tree.insert('', 'end', values=[str(v) if v is not None else '' for v in row])



def alfabetik():
    for i in tree.get_children():
        tree.delete(i)

    cursor.execute('select * from KitapListesi order by KitapAdi')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])

def yazardan():
    for i in tree.get_children():
        tree.delete(i)
            
    cursor.execute('select * from KitapListesi order by Yazar')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])

def turden():
    for i in tree.get_children():
        tree.delete(i)
          
    cursor.execute('select * from KitapListesi order by Tur')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])

def puandan():
    for i in tree.get_children():
        tree.delete(i)

    cursor.execute('select * from KitapListesi order by Puan desc')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])

def yilasec():
    for i in tree.get_children():
        tree.delete(i)

    cursor.execute('select * from KitapListesi order by BasimYili')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])

def yildesc():
    for i in tree.get_children():
        tree.delete(i)

    cursor.execute('select * from KitapListesi order by BasimYili desc')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])



def yil():
    global tiklama_sayisi
    tiklama_sayisi += 1
    if tiklama_sayisi % 2 == 1:  # Tek basış
        yilasec()
    else:  # Çift basış
        yildesc()





def cikis():
    pencere.destroy()



btn_frame = Frame(pencere)
btn_frame.configure(background='lightblue')
btn_frame.pack(side="left", fill="x", pady=10)

btn_frame_right = Frame(pencere)
btn_frame_right.configure(background='lightblue')
btn_frame_right.pack(side="right", fill="x", pady=10)



btn = Button(btn_frame, text="Tüm Kitapları Görüntüle", command=hepsi)
btn.pack(side="top", fill='x', padx=10, pady=10)

btn = Button(btn_frame, text="Kitap Ekle", command=kitapEkle)
btn.pack(side="top", fill='x', padx=10,pady=10)

btn = Button(btn_frame, text="Kitap Sil", command=kitapSil)
btn.pack(side="top", fill='x', padx=10, pady=10)

btn = Button(btn_frame, text="En Çok Beğenilenler", command=enIyiler)
btn.pack(side="top", fill='x', padx=10, pady=10)


btn = Button(btn_frame_right, text="A'dan Z'ye Sırala", command=alfabetik)
btn.pack(side="top", fill='x', padx=10, pady=10)

btn = Button(btn_frame_right, text="Yazara Göre Sırala", command=yazardan)
btn.pack(side="top", fill='x', padx=10,pady=10)

btn = Button(btn_frame_right, text="Türe Göre Sırala", command=turden)
btn.pack(side="top", fill='x', padx=10, pady=10)

btn = Button(btn_frame_right, text="Puana Göre Sırala", command=puandan)
btn.pack(side="top", fill='x', padx=10, pady=10)

tiklama_sayisi = 0
btn = Button(btn_frame_right, text="Yıla Göre Sırala", command=yil)
btn.pack(side="top", fill='x', padx=10, pady=10)


# Arama çubuğu ve buton
frame_ara = Frame(pencere)
frame_ara.pack(pady=10)

Label(frame_ara, text="Kitap Ara:").pack(side=LEFT)
entry_ara = Entry(frame_ara)
entry_ara.pack(side=LEFT, padx=5)

btn_ara = Button(frame_ara, text="Ara", command=kitap_ara)
btn_ara.pack(side=LEFT)




btn = Button(bg='red', fg='white', text="ÇIKIŞ", command=cikis, width=12, height=3)
btn.pack(padx=7, pady=10)


pencere.mainloop()
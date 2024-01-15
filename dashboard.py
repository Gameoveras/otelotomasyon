from flask import Flask, render_template, request, url_for, flash, redirect,session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import hashlib
import os
import datetime 


app = Flask(__name__)
app.secret_key = 'sdfkwprı3*034ıaw*0dı-32ğ1pk1ğ34k1'

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

baglanti = sqlite3.connect("deneme2.db", check_same_thread=False)


# Kullanıcı girişini kontrol etme
def get_user_id():
    if 'user' in session:
        return session['user'][0]
    else:
        return None

# Ana sayfa
@app.route("/")
@app.route("/")
def anasayfa():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ilan')
    oteller = cursor.fetchall()
   
  

    conn.close()
    
    otela = [
        {"otel_adi": "Otel 1", "lat": 41.0082, "lng": 28.9784, "fiyat": 150, "aciklama": "Güzel bir otel"},
    ]
    
    user_id = get_user_id() 
    
    ## Google Maps API Key
    api_key = "AIzaSyBlrIbMz_0LyXMU0b923onTM--kqTsuULw" 

    if 'user' in session:
        return render_template('anasayfa_girisli.html', oteller=oteller,api_key=api_key , yer=otela, user_id=user_id)
    else:
        return render_template('anasayfass.html', oteller=oteller,api_key=api_key , yer=otela) 


# Kullanıcı kaydı
@app.route("/kaydol/", methods=['POST', 'GET'])
def kaydol():
    if request.method == 'POST':
        adsoyad = request.form['name'] + " " + request.form['surname']
        eposta = request.form['email']
        sifre = request.form['password']
        telefon = request.form['phone_number']
        tc_kimlik = request.form['tc_kimlik']

        hashed_sifre = hashlib.sha256(sifre.encode('utf-8')).hexdigest()
        baglanti.execute("INSERT INTO kullanici (adsoyad, eposta, sifre, telefon, tc_kimlik) VALUES (?, ?, ?, ?, ?)",
                         (adsoyad, eposta, hashed_sifre, telefon, tc_kimlik))
        baglanti.commit()

        return redirect(url_for('anasayfa'))

    return render_template('kaydol.html')

# Kullanıcı girişi
@app.route("/girisyap", methods=['POST', 'GET'])
def login():
    cursor = baglanti.cursor()
    if request.method == 'POST':
        email_or_phone_number = request.form['email_or_phone_number']
        password = request.form['password']

        if '@' in email_or_phone_number:
            cursor.execute('SELECT * FROM kullanici WHERE eposta=? AND sifre=?', (email_or_phone_number, hashlib.sha256(password.encode('utf-8')).hexdigest()))
        else:
            cursor.execute('SELECT * FROM kullanici WHERE telefon=? AND sifre=?', (email_or_phone_number, hashlib.sha256(password.encode('utf-8')).hexdigest()))

        user = cursor.fetchone()

        if user:
            session['user'] = user
            flash('Giriş başarılı.', 'success')
            return redirect(url_for('anasayfa'))
        else:
            flash('Geçersiz e-posta veya şifre.', 'error')

    return render_template('girisyap.html')

# Yönetici girişi
@app.route("/yoneticigiris", methods=['POST', 'GET'])
def yonetici_girisi():
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')

        conn = create_connection()
        cursor = conn.cursor()

        # Kullanıcı adını kullanarak veritabanından yönetici bilgilerini al
        cursor.execute('SELECT * FROM yonetici WHERE username = ?', (kullanici_adi,))
        yonetici = cursor.fetchone()

        if yonetici and check_password_hash(yonetici[2], sifre):
            # Şifre doğruysa yönetici giriş yapabilir
            return render_template('/admin/dashboard.html')
        else:
            return "Yanlış kullanıcı adı veya şifre!"

    return render_template('yoneticigiris.html')


# Yönetici kaydı
@app.route("/yoneticikayit", methods=['POST', 'GET'])
def yonetici_kaydi():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']

        conn = create_connection()
        cursor = conn.cursor()

        # Aynı kullanıcı adına sahip bir yönetici var mı kontrol et
        cursor.execute('SELECT * FROM yonetici WHERE username = ?', (kullanici_adi,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Bu kullanıcı adı zaten kullanımda. Lütfen farklı bir kullanıcı adı seçin."
        else:
            # Yeni yöneticiyi veritabanına ekle
            hashed_password = generate_password_hash(sifre, method='sha256')
            cursor.execute('INSERT INTO yonetici (username, password) VALUES (?, ?)', (kullanici_adi, hashed_password))
            conn.commit()
            conn.close()

            return "Yönetici kaydı başarıyla oluşturuldu!"

    return render_template('yoneticikayit.html')

# Yönetici çıkışı
@app.route("/admin")
def admin_panel():
    return render_template('/admin/dashboard.html')  

# Veritabanı bağlantısı oluşturma
def create_connection():
    conn = sqlite3.connect('deneme2.db')
    return conn

# Veritabanı sorgusu çalıştırma
def execute_query(query, args=()):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    conn.close()

# Yönetici otel ekleme
@app.route("/admin/otelekle", methods=['POST', 'GET'])
def urun_ekle():
    if request.method == 'POST':
        otel_adi = request.form['otelAdi']
        parola = request.form['parola']
        hashed_parola = generate_password_hash(parola, method='sha256')  # Şifreyi güvenli bir şekilde hash'le

        adres = request.form['adres']
        telefon = request.form['telefon']
        email = request.form['email']
        oda_sayisi = request.form['odaSayisi']
        aciklama = request.form['aciklama']
        enlem = request.form['enlem']
        boylam = request.form['boylam']
        vergi_numarasi = request.form['vergiNumarasi']

        try:
            query = "INSERT INTO hotel (name, parola, address, phone, email, rooms, description, location_lat, location_lng, tax_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            data = (otel_adi, hashed_parola, adres, telefon, email, oda_sayisi, aciklama, enlem, boylam, vergi_numarasi)
            execute_query(query, data)
            print("Data inserted successfully.")

            return redirect(url_for('admin_panel'))
        except Exception as e:
            print("Error inserting data into the database:", str(e))
            return "Error: " + str(e)  # Hata mesajını geri döndür
    return render_template('admin/otelekle.html')




@app.route("/admin/indirim", methods=['GET'])
def indirim():
    return render_template('/admin/indirim.html')


# Otel Getir Fonksiyonu
def get_hotels():
    conn = create_connection()  # Veritabanı adınızı buraya ekleyin
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hotel")
    hotels = cursor.fetchall()

    conn.close()

    return hotels

# Kullanıcı Getir Fonksiyonu
def get_users():
    conn = create_connection()
    cursor = conn.cursor()

    # Kullanıcıları çek
    cursor.execute("SELECT * FROM kullanici")
    users = cursor.fetchall()

    conn.close()

    return users

# Şikayet Getir Fonksiyonu
def get_sikayet():
    conn = create_connection()
    cursor = conn.cursor()

    # Kullanıcıları çek
    cursor.execute("SELECT * FROM sikayet")
    users = cursor.fetchall()

    conn.close()

    return users
# Rezervasyon Getir Fonksiyonu
def get_rezervasyon():
    conn = create_connection()
    cursor = conn.cursor()

    # Kullanıcıları çek
    cursor.execute("SELECT * FROM rezervasyon")
    users = cursor.fetchall()

    conn.close()

    return users
# Yorum Getir Fonksiyonu
def get_yorum():
    conn = create_connection()
    cursor = conn.cursor()

    # Kullanıcıları çek
    cursor.execute("SELECT * FROM OtelYorumlari")
    users = cursor.fetchall()

    conn.close()

    return users

# Yönetici paneli faaliyetler
@app.route("/admin/faaliyet", methods=['GET'])
def faaliyet():
    rezervasyonlar = get_rezervasyon()  
    yorumlar = get_yorum()
    return render_template('/admin/faaliyet.html' , rezervasyonlar=rezervasyonlar,yorumlar=yorumlar)

# Yönetici kullanıcılar
@app.route("/admin/uyeler", methods=['GET'])
def uyeler():
    users = get_users() 
    return render_template('/admin/uyeler.html', users=users)




# Yönetici oteller
@app.route("/admin/oteller", methods=['GET'])
def hotels():
    otels = get_hotels()  # get_users fonksiyonunu implemente ettiğinizi varsayalım
    return render_template('/admin/oteller.html', hotels=otels)


# Yönetici şikayetler
@app.route("/admin/sikayetler", methods=['GET'])
def sikayet():
    sikayetler = get_sikayet() 
    return render_template('/admin/sikayetler.html', sikayetler=sikayetler)

# İlgilenildi fonksiyonu
@app.route("/admin/sikayet_ilgilenildi/<int:sikayet_id>", methods=['POST'])
def sikayet_ilgilenildi(sikayet_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE sikayet SET durum = 'İlgilenildi' WHERE id=?", (sikayet_id,))
    conn.commit()
    conn.close()

    return "Success" 

# İlgiilenilmedi fonksiyonu
@app.route("/admin/sikayet_ilgilenilmedi/<int:sikayet_id>", methods=['POST'])
def sikayet_ilgilenilmedi(sikayet_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE sikayet SET durum = 'İlgilenilmedi' WHERE id=?", (sikayet_id,))
    conn.commit()
    conn.close()

    return "Success"  




# Yönetici arama
@app.route("/admin/arama", methods=['GET'])
def arama():
    return render_template('/admin/arama.html')


@app.route('/admin/delete_member/<int:user_id>')
def delete_member(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Perform delete operation
    cursor.execute("DELETE FROM kullanici WHERE id = ?", (user_id,))
    conn.commit()

    conn.close()

    return redirect('/admin/uyeler')

@app.route('/admin/edit_member/<int:user_id>')
def edit_member(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM kullanici WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    conn.close()

    return render_template('edit_member.html', user=user)



# Yönetici ilanları
@app.route("/admin/ilanlar", methods=['GET'])
def yonetici_ilanlar():
    conn = create_connection()
    cursor = conn.cursor()

    # İlanları çek
    cursor.execute("SELECT * FROM ilan")
    ilanlar = cursor.fetchall()

    conn.close()

    # Yönetici ilanları template'e gönder
    return render_template('/admin/ilanlar.html', ilanlar=ilanlar)


# Yönetici ilan düzenleme sayfası
@app.route("/admin/ilanlar/duzenle/<int:ilan_id>", methods=['GET', 'POST'])
def yot_ilan_duzenle(ilan_id):
    conn = create_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        # İlanı getir
        cursor.execute('SELECT * FROM ilan WHERE id = ?', (ilan_id,))
        ilan = cursor.fetchone()
        conn.close()

        return render_template('/admin/iladuzenle.html', ilan=ilan)
    elif request.method == 'POST':
        # Düzenleme formu gönderildiğinde
        yeni_bilgiler = {
            'otel_adi': request.form['otel_adi'],
            'slogan': request.form['slogan'],
            'facebook': request.form['facebook'],
            'instagram': request.form['instagram'],
            'yildiz_sayisi': request.form['yildiz_sayisi'],
            'sehir': request.form['sehir'],
            'ilce': request.form['ilce'],
            'otel_onresim': request.form['otel_onresim'],
            'otel_resimler': request.form['otel_resimler'],
            'herSeyDahil': request.form['herSeyDahil'],
            'eposta': request.form['eposta'],
            'telefon': request.form['telefon'],
            'rezervasyonBaslangic': request.form['rezervasyonBaslangic'],
            'rezervasyonBitis': request.form['rezervasyonBitis'],
            'maxRezervasyonSayisi': request.form['maxRezervasyonSayisi'],
            'denizeUzaklik': request.form['denizeUzaklik'],
            'gunlukFiyat': request.form['gunlukFiyat'],
            'enlem': request.form['enlem'],
            'denizeSifir': request.form['denizeSifir'],
            'havuzVar': request.form['havuzVar'],
            'taksitliOdeme': request.form['taksitliOdeme'],
            'otelAciklama': request.form['otelAciklama']
        }

        # İlanı güncelle
        cursor.execute("""
            UPDATE ilan
            SET otel_adi = ?, slogan = ?, facebook = ?, instagram = ?, yildiz_sayisi = ?,
                sehir = ?, ilce = ?, otel_onresim = ?, otel_resimler = ?, herSeyDahil = ?,
                eposta = ?, telefon = ?, rezervasyonBaslangic = ?, rezervasyonBitis = ?,
                maxRezervasyonSayisi = ?, denizeUzaklik = ?, gunlukFiyat = ?, enlem = ?,
                denizeSifir = ?, havuzVar = ?, taksitliOdeme = ?, otelAciklama = ?
            WHERE id = ?
        """, (yeni_bilgiler['otel_adi'], yeni_bilgiler['slogan'], yeni_bilgiler['facebook'],
              yeni_bilgiler['instagram'], yeni_bilgiler['yildiz_sayisi'], yeni_bilgiler['sehir'],
              yeni_bilgiler['ilce'], yeni_bilgiler['otel_onresim'], yeni_bilgiler['otel_resimler'],
              yeni_bilgiler['herSeyDahil'], yeni_bilgiler['eposta'], yeni_bilgiler['telefon'],
              yeni_bilgiler['rezervasyonBaslangic'], yeni_bilgiler['rezervasyonBitis'],
              yeni_bilgiler['maxRezervasyonSayisi'], yeni_bilgiler['denizeUzaklik'],
              yeni_bilgiler['gunlukFiyat'], yeni_bilgiler['enlem'], yeni_bilgiler['denizeSifir'],
              yeni_bilgiler['havuzVar'], yeni_bilgiler['taksitliOdeme'],
              yeni_bilgiler['otelAciklama'], ilan_id))

        conn.commit()
        conn.close()

        # Profil sayfasına yönlendir
        return redirect(url_for('dashboard'))
   

# Kullanıcı favorileri
@app.route("/kullanici/<int:kullanici_id>")
def favorilerim(kullanici_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    print(kullanici_id)

    cursor.execute("""
        SELECT O.id, O.otel_adi, O.sehir, O.ilce, O.gunlukFiyat
        FROM ilan AS O
        JOIN Favoriler AS F ON O.id = F.otel_id
        WHERE F.kullanici_id = ?
    """, (kullanici_id,))

    favori_oteller = cursor.fetchall()
    
    

    conn.close()
    
    user_id = get_user_id() 

    return render_template('/kullanici/favorilerim.html', favori_oteller=favori_oteller,user_id=user_id)


# Kullanıcı bilgilerini getirme fonksiyonu
def get_kullanici_bilgileri():
    kullanici_id = get_user_id()

    if kullanici_id is not None:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kullanici WHERE id=?", (kullanici_id,))
        kullanici = cursor.fetchone()
        cursor.close()
        return kullanici
    else:
        return None


# Kullanıcı bilgilerini güncelleme fonksiyonu
def update_kullanici_bilgileri(yeni_bilgiler):
    kullanici_id = get_user_id()

    if kullanici_id is not None:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE kullanici SET adsoyad=?, telefon=?, email=?, sifre=? WHERE id=?",
                       (yeni_bilgiler['adsoyad'], yeni_bilgiler['telefon'], yeni_bilgiler['email'], yeni_bilgiler['sifre'], kullanici_id))
        
        conn.commit()
        cursor.close()


# Kullanıcı profil sayfası
@app.route("/kullanici/profilim", methods=['GET', 'POST'])
def profilim():
    if get_user_id() is None:
        return redirect(url_for('login'))

    kullanici = get_kullanici_bilgileri()
    
    user_id = get_user_id() 


    if request.method == 'POST':
        yeni_bilgiler = {
            'adsoyad': request.form.get('adsoyad'),
            'email': request.form.get('email'),
            'telefon': request.form.get('telefon')
        }
        update_kullanici_bilgileri(yeni_bilgiler)

    return render_template('/kullanici/profilim.html', kullanici=kullanici,user_id=user_id)

# Kullanıcı rezervasyonları
@app.route("/kullanici/rezervasyonlarim", methods=['GET'])
def rezer():
    kullanici_id = get_user_id()

    conn = sqlite3.connect("deneme2.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT R.*, O.otel_adi
        FROM rezervasyon R
        JOIN ilan O ON R.otel_id = O.id
        WHERE R.kullanici_id = ?
        ORDER BY R.rezervasyon_id DESC
    """, (kullanici_id,))

    rezervasyonlar = cursor.fetchall()


    conn.close()
    
    user_id = get_user_id() 

    return render_template("/kullanici/rezervasyonlarim.html", rezervasyonlar=rezervasyonlar, user_id=user_id)

# Son görüntülenen otelleri getirme fonksiyonu
@app.route("/kullanici/songoruntulenen", methods=['GET'])
def son_goruntulenen():
    if 'user' in session:
        kullanici_id = session['user'][0]  # Giriş yapmış kullanıcının ID'sini al

        conn = create_connection()
        cursor = conn.cursor()

        # Kullanıcının son görüntülenen otellerini al
        cursor.execute('SELECT otel_id, tarih FROM SonGoruntulenenOteller WHERE kullanici_id=? ORDER BY tarih DESC', (kullanici_id,))
        son_goruntulenen_oteller = cursor.fetchall()

        # Oteller tablosundan detaylı bilgileri al
        oteller = []
        for otel_id, tarih in son_goruntulenen_oteller:
            cursor.execute('SELECT * FROM ilan WHERE id=?', (otel_id,))
            otel_bilgisi = cursor.fetchone()
            oteller.append({'otel_id': otel_id, 'otel_bilgisi': otel_bilgisi, 'tarih': tarih})

        conn.close()
        
        user_id = get_user_id() 

        return render_template('/kullanici/songoruntulenen.html', oteller=oteller, user_id=user_id)
    else:
        return redirect(url_for('login'))

# Otel ilanları    
@app.route("/otel/ilanolustur", methods=['GET', 'POST'])
def otel():
    if request.method == 'POST':
        otel_id = request.form.get('otel_id')
        otel_adi = request.form['otel-adi']
        slogan = request.form['slogan']
        facebook = request.form['facebook']
        instagram = request.form['instagram']
        yildiz_sayisi = request.form['yildiz']
        her_sey_dahil = request.form['her-sey-dahil']
        sehir = request.form['il']
        ilce = request.form['ilce']
        eposta = request.form['eposta']
        telefon = request.form['tel']
        rezervasyon_baslangic = request.form['reservation-start']
        rezervasyon_bitis = request.form['reservation-end']
        max_rezervasyon_sayisi = request.form['max-occupancy']
        denize_uzaklik = request.form['denize-uzaklik']
        gunluk_fiyat = request.form['gunluk-fiyat']
        tam_konum = request.form['tam-konum']
        denize_sifir = request.form.get('denize-sifir')
        havuz_var = request.form.get('havuzu-var')
        taksitli_odeme = request.form.get('taksitli-odeme')
        otel_aciklama = request.form['otel-aciklama']
        boylam = request.form['boylam']

        
        onresim = request.files['otel-onresim']
        resimler = request.files.getlist('otel-resimler[]')

 
        onresim.save(os.path.join(app.config['UPLOAD_FOLDER'], onresim.filename))
        for resim in resimler:
            resim.save(os.path.join(app.config['UPLOAD_FOLDER'], resim.filename))

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO ilan (otel_adi, slogan, facebook, instagram, yildiz_sayisi, sehir, ilce, eposta, telefon, 
            rezervasyonBaslangic, rezervasyonBitis, maxRezervasyonSayisi, denizeUzaklik, gunlukFiyat, tamKonum, 
            denizeSifir, havuzVar, taksitliOdeme, otelAciklama, herSeyDahil, otel_onresim, otel_resimler,boylam,hotel_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)
        ''', (otel_adi, slogan, facebook, instagram, yildiz_sayisi, sehir, ilce, eposta, telefon,
              rezervasyon_baslangic, rezervasyon_bitis, max_rezervasyon_sayisi, denize_uzaklik, gunluk_fiyat,
              tam_konum, denize_sifir, havuz_var, taksitli_odeme, otel_aciklama, her_sey_dahil, onresim.filename,
              ",".join([resim.filename for resim in resimler],boylam,otel_id)))
        
        
        
        if request.form.get('farkli-oda-ekle') == 'hayir':
            conn.commit()
            conn.close()
            return "İlan başarıyla kaydedildi!"

        otel_id = cursor.lastrowid
        
        if request.form.get('farkli-oda-ekle') == 'evet':
            oda_sayisi = int(request.form.get('oda-sayisi'))

            for i in range(1, oda_sayisi + 1):
                oda_adi = request.form.get(f'oda-adi-{i}')
                max_kisi_sayisi = request.form.get(f'max-kisi-sayisi-{i}')
                cift_fiyat = request.form.get(f'cift-fiyat-{i}')
                gunluk_aciklama = request.form.get(f'gunluk-aciklama-{i}')

        # Oda resimlerini kontrol et ve kaydet
                oda_resimler = request.files.getlist(f'oda-resim-{i}[]')
                for oda_resim in oda_resimler:
                    if oda_resim.filename != '':
                        oda_resim.save(os.path.join(app.root_path, "static", "images", oda_resim.filename))
                
                        cursor.execute('''
                            INSERT INTO oda (otel_id, oda_adi, max_kisi_sayisi, cift_fiyat, gunluk_aciklama, oda_resmi)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ''', (otel_id, oda_adi, max_kisi_sayisi, cift_fiyat, gunluk_aciklama, oda_resim.filename))
                    else:
                        cursor.execute('''
                            INSERT INTO oda (otel_id, oda_adi, max_kisi_sayisi, cift_fiyat, gunluk_aciklama)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (otel_id, oda_adi, max_kisi_sayisi, cift_fiyat, gunluk_aciklama))


        conn.commit()
        conn.close()

        return "İlan başarıyla kaydedildi!"

    return render_template('/otel/ilanolustur.html')


# Otel ilanlarını getirme fonksiyonu
def get_hotel_ilanlari(hotel_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ilan WHERE hotel_id = ?', (hotel_id,))
    ilanlar = cursor.fetchall()

    conn.close()

    return ilanlar


# Otel profil sayfası
@app.route("/otel")
def otel_profil():
    if 'otel' not in session:
        return redirect(url_for('otel_giris'))

    hotel_id = session['otel'][0]
    
    conn = create_connection()
    cursor = conn.cursor()

    # Otel bilgilerini getir
    cursor.execute('SELECT * FROM hotel WHERE hotel_id = ?', (hotel_id,))
    oteller = cursor.fetchone()

    conn.close()

    # Otel ilanlarını getir
    ilanlar = get_hotel_ilanlari(hotel_id)

    return render_template("otel/profilim.html", oteller=oteller, ilanlar=ilanlar)

# İlan düzenleme sayfası
@app.route("/otel/profilim/duzenle/<int:ilan_id>", methods=['GET', 'POST'])
def ilan_duzenle(ilan_id):
    conn = create_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        # İlanı getir
        cursor.execute('SELECT * FROM ilan WHERE id = ?', (ilan_id,))
        ilan = cursor.fetchone()
        conn.close()

        return render_template('/otel/duzenle.html', ilan=ilan)
    elif request.method == 'POST':
        # Düzenleme formu gönderildiğinde
        yeni_bilgiler = {
            'otel_adi': request.form['otel_adi'],
            'slogan': request.form['slogan'],
            'facebook': request.form['facebook'],
            'instagram': request.form['instagram'],
            'yildiz_sayisi': request.form['yildiz_sayisi'],
            'sehir': request.form['sehir'],
            'ilce': request.form['ilce'],
            'otel_onresim': request.form['otel_onresim'],
            'otel_resimler': request.form['otel_resimler'],
            'herSeyDahil': request.form['herSeyDahil'],
            'eposta': request.form['eposta'],
            'telefon': request.form['telefon'],
            'rezervasyonBaslangic': request.form['rezervasyonBaslangic'],
            'rezervasyonBitis': request.form['rezervasyonBitis'],
            'maxRezervasyonSayisi': request.form['maxRezervasyonSayisi'],
            'denizeUzaklik': request.form['denizeUzaklik'],
            'gunlukFiyat': request.form['gunlukFiyat'],
            'enlem': request.form['enlem'],
            'denizeSifir': request.form['denizeSifir'],
            'havuzVar': request.form['havuzVar'],
            'taksitliOdeme': request.form['taksitliOdeme'],
            'otelAciklama': request.form['otelAciklama']
        }

        # İlanı güncelle
        cursor.execute("""
            UPDATE ilan
            SET otel_adi = ?, slogan = ?, facebook = ?, instagram = ?, yildiz_sayisi = ?,
                sehir = ?, ilce = ?, otel_onresim = ?, otel_resimler = ?, herSeyDahil = ?,
                eposta = ?, telefon = ?, rezervasyonBaslangic = ?, rezervasyonBitis = ?,
                maxRezervasyonSayisi = ?, denizeUzaklik = ?, gunlukFiyat = ?, enlem = ?,
                denizeSifir = ?, havuzVar = ?, taksitliOdeme = ?, otelAciklama = ?
            WHERE id = ?
        """, (yeni_bilgiler['otel_adi'], yeni_bilgiler['slogan'], yeni_bilgiler['facebook'],
              yeni_bilgiler['instagram'], yeni_bilgiler['yildiz_sayisi'], yeni_bilgiler['sehir'],
              yeni_bilgiler['ilce'], yeni_bilgiler['otel_onresim'], yeni_bilgiler['otel_resimler'],
              yeni_bilgiler['herSeyDahil'], yeni_bilgiler['eposta'], yeni_bilgiler['telefon'],
              yeni_bilgiler['rezervasyonBaslangic'], yeni_bilgiler['rezervasyonBitis'],
              yeni_bilgiler['maxRezervasyonSayisi'], yeni_bilgiler['denizeUzaklik'],
              yeni_bilgiler['gunlukFiyat'], yeni_bilgiler['enlem'], yeni_bilgiler['denizeSifir'],
              yeni_bilgiler['havuzVar'], yeni_bilgiler['taksitliOdeme'],
              yeni_bilgiler['otelAciklama'], ilan_id))

        conn.commit()
        conn.close()

        # Profil sayfasına yönlendir
        return redirect(url_for('otelprofil'))
    
# İlan silme fonksiyonu
@app.route("/otel/profilim/sil/<int:ilan_id>", methods=['POST'])
def ilan_sil(ilan_id):
    conn = create_connection()
    cursor = conn.cursor()

    # İlanı sil
    cursor.execute('DELETE FROM ilan WHERE id = ?', (ilan_id,))
    conn.commit()
    conn.close()

    # Profil sayfasına yönlendir
    return redirect(url_for('otelprofil'))

# Otel giriş işlevi
@app.route("/otelgiris", methods=['POST', 'GET'])
def otel_giris():
    if request.method == 'POST':
        otel_adi = request.form.get('otelAdi')
        parola = request.form.get('parola')


        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM hotel WHERE name=?', (otel_adi,))
            otel = cursor.fetchone()

            if otel and check_password_hash(otel[13], parola):
                session['otel'] = otel
                return redirect(url_for('otel'))
            else:
                return render_template('otelgiris.html', error='Otel adı veya parola hatalı.')
        except Exception as e:
            print("Error during query execution:", str(e))
            return render_template('otelgiris.html', error='Bir hata oluştu.')

    return render_template('otelgiris.html')

# Otel çıkış işlevi
def sil_yorum(yorum_id):
    conn = sqlite3.connect("your_database.db")  # Veritabanı adını güncelleyin
    cursor = conn.cursor()

    cursor.execute("DELETE FROM OtelYorumlari WHERE id=?", (yorum_id,))

    conn.commit()
    conn.close()

# Otele ait yorumları görüntüleme işlevi
@app.route("/otel/yorumlar", methods=['GET', 'POST'])
def otel_yorumlar():
    if 'otel' not in session:
        return redirect(url_for('otel_giris'))

    otel_id = session['otel'][0]

    conn = create_connection()
    cursor = conn.cursor()

    # Otele ait yorumları al
    cursor.execute('SELECT * FROM OtelYorumlari WHERE otel_id = ?', (otel_id,))
    yorumlar = cursor.fetchall()

    if request.method == 'POST':
        # Yorumu silme işlemi
        yorum_id = request.form.get('yorum_id')
        if yorum_id:
            sil_yorum(yorum_id, cursor, conn)  # Pass cursor and connection to the function

    conn.close()

    return render_template('/otel/yorumlar.html', yorumlar=yorumlar)

def sil_yorum(yorum_id, cursor, conn):
    cursor.execute('DELETE FROM OtelYorumlari WHERE id = ?', (yorum_id,))
    conn.commit()

# Talep onaylama işlevi
@app.route("/otel/talepler", methods=['GET'])
def talep():
    if 'otel' not in session:
        return redirect(url_for('otel_giris'))

    otel_id = session['otel'][0]  

    conn = create_connection()
    cursor = conn.cursor()

    # Otele ait rezervasyon taleplerini al
    cursor.execute('''
        SELECT r.*, i.otel_adi AS ilan_adi, i.sehir AS ilan_aciklamasi
        FROM rezervasyon r
        JOIN ilan i ON r.otel_id = i.id
        WHERE r.otel_id = ?''', (otel_id,))    
    talepler = cursor.fetchall()

    conn.close()

    return render_template('/otel/talepler.html', talepler=talepler)


# Talep onaylama işlevi
@app.route("/oteller/<int:otel_id>", methods=['GET'])
def adres(otel_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ilan WHERE id=?', (otel_id,))
    otel_bilgileri = cursor.fetchone()

    cursor.execute('SELECT * FROM OtelYorumlari WHERE otel_id=?', (otel_id,))
    otel_yorumlari = cursor.fetchall()
    
    
    cursor.execute('SELECT * FROM ilan')
    oteller = cursor.fetchall()


    cursor.execute('SELECT * FROM oda WHERE otel_id=?', (otel_id,))
    odalar = cursor.fetchall()

    conn.close()

    return render_template('otel.html', oteller=oteller, otels=otel_bilgileri, otel_yorumlari=otel_yorumlari,odalar=odalar)

# Yorum ekleme işlevi
@app.route("/oteller/<int:otel_id>/yorum-ekle", methods=['POST'])
def yorum_ekle(otel_id):
    if request.method == 'POST':
        ad = request.form['yorum-yapan']
        puan = request.form['yorum-puan']
        icerik = request.form['yorum-icerik']

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute('INSERT INTO OtelYorumlari (otel_id, yorum_yapan, yorum_puan, yorum_icerik) VALUES (?, ?, ?, ?)',
                           (otel_id, ad, puan, icerik))

            conn.commit()
            print("Yorum eklendi.")
        except Exception as e:
            print(f"Error: {str(e)}")
            conn.rollback()
        finally:
            if conn:
                conn.close()

        return redirect(url_for('adres', otel_id=otel_id))

# Favoriye ekleme işlevi
@app.route("/favori-ekle/<int:otel_id>", methods=['POST'])
def favori_ekle(otel_id):
    if 'user' in session:
        kullanici_id = session['user'][0]  # Giriş yapmış kullanıcının ID'sini al

        conn = create_connection()
        cursor = conn.cursor()

        # Kullanıcının daha önce bu oteli favorilere ekleyip eklememiğini kontrol et
        cursor.execute("SELECT * FROM Favoriler WHERE kullanici_id=? AND otel_id=?", (kullanici_id, otel_id))
        result = cursor.fetchone()

        if not result:
            # Kullanıcı daha önce bu oteli favorilere eklemediyse ekleyin
            cursor.execute("INSERT INTO Favoriler (kullanici_id, otel_id) VALUES (?, ?)", (kullanici_id, otel_id))
            conn.commit()

        conn.close()

        return redirect(url_for('adres', otel_id=otel_id))
    else:
        return redirect(url_for('login'))


#Son görüntülenen otelleri veritabanına ekleyen işlev
@app.route("/songorulenen-ekle/<int:otel_id>", methods=['POST'])
def songorulenen_ekle(otel_id):
    if 'user' in session:
        kullanici_id = session['user'][0]  # Giriş yapmış kullanıcının ID'sini al

        conn = create_connection()
        cursor = conn.cursor()

        # Kullanıcının daha önce bu oteli görüntüleyip görüntülemediğini kontrol et
        cursor.execute("SELECT * FROM SonGoruntulenenOteller WHERE kullanici_id=? AND otel_id=?", (kullanici_id, otel_id))
        result = cursor.fetchone()

        if not result:
            # Kullanıcı daha önce bu oteli görüntülemediyse ekleyin
            cursor.execute("INSERT INTO SonGoruntulenenOteller (kullanici_id, otel_id) VALUES (?, ?)", (kullanici_id, otel_id))
            conn.commit()

        conn.close()

        return redirect(url_for('adres', otel_id=otel_id))
    else:
        return redirect(url_for('login'))


#Otel silme işlevi
@app.route("/admin/otel/delete/<int:hotel_id>", methods=['POST'])
def delete_hotel(hotel_id):
    conn = create_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute("DELETE FROM hotel WHERE hotel_id=?", (hotel_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('hotels'))
    else:
        return redirect(url_for('hotels'))
    
    
 



# Rezervation sayfası
@app.route("/rezervasyon-yap/<int:otel_id>", methods=["POST"])
def rezervasyon_yap(otel_id):
    if request.method == "POST":
        # Rezervasyon bilgilerini formdan al
        giris_tarihi = request.form.get("giris_tarihi")
        cikis_tarihi = request.form.get("cikis_tarihi")
        yetiskin_sayisi = request.form.get("yetisin_sayisi")
        oda_tipi = request.form.get("oda_tipi")
        toplam_fiyat = request.form.get("toplam_fiyat")

        # Kullanıcı bilgileri (örneğin, oturum açmış bir kullanıcının ID'si) alınabilir
        # Şu anlık örnek olarak bir kullanıcı ID'si veriyorum:
        kullanici_id = get_user_id()

        # Veritabanına rezervasyon bilgilerini ekleyin
        conn = sqlite3.connect("deneme2.db")
        cursor = conn.cursor()

        # Örnek bir SQL sorgusu (tablolar ve alan adları gerçek veritabanı şemanıyla uyuşmalı)
        cursor.execute(
            "INSERT INTO rezervasyon (otel_id, kullanici_id, giris_tarihi, cikis_tarihi, yetiskin_sayisi, oda_tipi, toplam_fiyat) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (otel_id, kullanici_id, giris_tarihi, cikis_tarihi, yetiskin_sayisi, oda_tipi, toplam_fiyat)
        )

        conn.commit()
        conn.close()

        # Başarılı bir şekilde rezervasyon yapıldığında kullanıcıyı başka bir sayfaya yönlendirin
        return redirect(url_for("odeme"))

    # Eğer kullanıcı doğrudan bu sayfaya gelirse başka bir sayfaya yönlendirin (isteğe bağlı)
    return redirect(url_for("anasayfa"))

# Odeme sayfası
@app.route("/odeme", methods=['GET'])
def odeme():
    kullanici_id = get_user_id()

    conn = sqlite3.connect("deneme2.db")
    cursor = conn.cursor()

    # Kullanıcının son rezervasyon bilgilerini ve otel adını al
    cursor.execute("""
        SELECT R.*, O.otel_adi
        FROM rezervasyon R
        JOIN ilan O ON R.otel_id = O.id
        WHERE R.kullanici_id = ?
        ORDER BY R.rezervasyon_id DESC
        LIMIT 1
    """, (kullanici_id,))

    rezervasyon_bilgisi = cursor.fetchone()

    conn.close()

    # rezervasyon_bilgisi[10] ifadesi ile otel adına ulaşabilirsiniz
    return render_template("odeme.html", rezervasyon=rezervasyon_bilgisi)


# Kullanıcı şikayetini veritabanına ekleyen işlev
def save_sikayet(kullanici_id, otel_id, konu, mesaj):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO sikayet (kullanici_id, otel_id, konu, mesaj) VALUES (?, ?, ?, ?)",
                   (kullanici_id, otel_id, konu, mesaj))

    conn.commit()
    conn.close()

# Şikayet formunu işleyen fonksiyon
@app.route("/sikayet", methods=['GET', 'POST'])
def sikayets():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT otel_adi FROM ilan")

    otel_adi_list = cursor.fetchall()
    otel_adi_options = [otel[0] for otel in otel_adi_list]

    conn.commit()
    conn.close()

    if request.method == 'POST':
        kullanici_id = get_user_id()  # Kullanıcı kimliğini almak için kendi işlevinizi kullanın
        otel_adi = request.form.get('otel_adi')
        konu = request.form.get('konu')
        mesaj = request.form.get('mesaj')

        save_sikayet(kullanici_id, otel_adi, konu, mesaj)

        return "Şikayetiniz başarıyla kaydedildi!"

    return render_template('/sikayet.html', otel_adi_options=otel_adi_options)

if __name__ == "__main__":
    app.run(debug=True)

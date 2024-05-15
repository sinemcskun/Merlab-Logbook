from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)
connectionStr = "D:/Sunular-Ödevler/Codeworks/flask-py/MerlabLogbook/logbook.db" #Change the path here to the path where the database is located on the installed computer

def add_panel_data(user_id, user_type_id, credential_id, faculty_id, lab_id, machine_id, parametre_id, deney_id, baslangic_zamani, bitis_zamani):
    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO panel (
                kullanici_id, kullanici_cesit_id, credential_id, fakulte_id, lab_id, makine_id, parametre_id, deney_id, baslangic_zamani, bitis_zamani
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, user_type_id, credential_id, faculty_id, lab_id, machine_id, parametre_id, deney_id, baslangic_zamani, bitis_zamani))
        con.commit()

def get_last_panel_id():
    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        cur.execute("SELECT MAX(id) FROM panel")
        result = cur.fetchone()
        return result[0] if result else None

@app.route('/', methods=['GET', 'POST'])
def mainPage():
    return render_template("index.html")

@app.route('/misafir', methods=['GET', 'POST'])
def guestP():
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    add_panel_data(user_id = 0, user_type_id=0, credential_id =0, faculty_id=0, lab_id=0, machine_id=0, parametre_id=0, deney_id=0, baslangic_zamani=current_datetime, bitis_zamani=0)
    user_id =3
    return render_template('guest.html', user_id = 3)

def newGuest():
    guestName = request.form.get('guestName')
    guestSurname = request.form.get('guestSurname')
    name = f"{guestName} {guestSurname}"
    barcode = request.form.get('barcode')
    user_id = 3

    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, kullanici_cesit_id) VALUES (?,?)", (name,user_id))
        con.commit()
        lastU = get_last_user_id()
        cur.execute("INSERT INTO user_credential (kullanicilar_id, kimlik) VALUES (?, ?)", (lastU, barcode))
        con.commit()
        cur.execute("SELECT MAX(id) FROM user_credential")
        credential_id = cur.fetchone()[0]
    lastPID = get_last_panel_id()
    update_panel_data_guest(lastPID,lastU,user_id,credential_id)

    return user_id

def get_last_user_id():
    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        cur.execute("SELECT MAX(id) FROM users")
        result = cur.fetchone()
        return result[0] if result else None

def update_panel_data_guest(panel_id, lastU, user_id, credential_id):
    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        cur.execute("""UPDATE panel
                    SET kullanici_id = ?, kullanici_cesit_id = ?, credential_id = ?
                    WHERE id = ?
                    """, (lastU, user_id, credential_id, panel_id)) 

def update_panel_data_parameter(panel_id, parameter_id_dict, deney_id, bitis_zamani):
    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        for param_name,param_id in parameter_id_dict.items():
            cur.execute("""
                UPDATE panel
                SET parametre_id = ?, deney_id = ?, bitis_zamani = ?
                WHERE id = ?
            """, (param_id, deney_id, bitis_zamani,panel_id))
    con.commit()

@app.route('/personel', methods=['GET', 'POST'])
def staffP():
    user_id = 2
    return render_template('staff.html', user_id=2)

def newStaff():
    staff_name = request.form.get('staffName')
    staff_surname = request.form.get('staffSurname')
    name= f"{staff_name} {staff_surname}"
    id_num = request.form.get('idNum')
    user_id = 2

    with sqlite3.connect(connectionStr) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, kullanici_cesit_id) VALUES (?,?)", (name,user_id))
            con.commit()
            lastU = get_last_user_id()
            cur.execute("INSERT INTO user_credential (kullanicilar_id, kimlik) VALUES (?, ?)", (lastU, id_num))
            con.commit()
            cur.execute("SELECT MAX(id) FROM user_credential")
            credential_id = cur.fetchone()[0]
    lastPID = get_last_panel_id()
    update_panel_data_staff(lastPID,lastU,user_id,credential_id)
    return user_id

def update_panel_data_staff(panel_id, lastU, user_id, credential_id):
    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        cur.execute("""UPDATE panel
                    SET kullanici_id = ?, kullanici_cesit_id = ?, credential_id =?
                    WHERE id = ?
                    """,(lastU,user_id,credential_id,panel_id))

@app.route('/yonetici', methods=['GET', 'POST'])
def adminP():
    return render_template("admin.html")  

@app.route('/panel', methods=['GET', 'POST'])
def adminPanel():
    if request.method == 'POST':
        entered_password = request.form.get('password')
        sql_query = """SELECT
    panel.id AS panel_id,
    users.username,
    user_type.kullanici_cesidi,
    user_credential.kimlik,
    faculty.fakulteler,
    laboratories.laboratuvarlar,
    machines.makine_isim,
    panel.baslangic_zamani,
    panel.bitis_zamani
FROM
    panel
INNER JOIN users ON panel.kullanici_id = users.id
INNER JOIN user_type ON panel.kullanici_cesit_id = user_type.id
INNER JOIN user_credential ON panel.credential_id = user_credential.id
INNER JOIN faculty ON panel.fakulte_id = faculty.id
INNER JOIN laboratories ON panel.lab_id = laboratories.id
INNER JOIN machines ON panel.makine_id = machines.id;
"""
        with sqlite3.connect(connectionStr) as con:
            cur = con.cursor()
            cur.execute("SELECT kimlik FROM user_credential ORDER BY id LIMIT 1")
            first_password = cur.fetchone()

            # Compare with the password entered by the user trying to log in
            if first_password and entered_password == first_password[0]:
                # Password correct, pass
                cur.execute(sql_query)
                result = cur.fetchall()
                return render_template("panel.html", result=result)
            else:
                # Password wrong,login failed
                return render_template("admin.html")

@app.route('/menu/<int:user_id>', methods=['GET', 'POST'])
def menu(user_id):
    if user_id == 2:
        user_id = newStaff()
    elif user_id == 3:
        user_id = newGuest()
    selectedTemplate = None
    if request.method == 'POST':
        sci_field = request.form.get('sciField')
        lab_selection = request.form.get('labSelection')
        machine_selection = request.form.get('machineSelection')

        selectedTemplate = machine_selection

    return render_template("menu.html", selectedTemplate = selectedTemplate, sci_field = sci_field, lab_selection = lab_selection)

@app.route('/machine', methods=['GET', 'POST'])
def machine_params():
    templateN = None  
    if request.method == 'POST':
        template = request.form.get('machineSelection')

        con = sqlite3.connect(connectionStr)
        cur = con.cursor()

        sci_field = request.form.get('sciField')
        lab_selection = request.form.get('labSelection')
        machine_selection = request.form.get('machineSelection')
        
        cur.execute("SELECT * FROM faculty WHERE fakulteler = ?", (sci_field,))
        faculty_result = cur.fetchone()
        faculty_id = faculty_result[0] if faculty_result else None
        cur.execute("SELECT * FROM laboratories WHERE laboratuvarlar = ?", (lab_selection,))
        laboratory_result = cur.fetchone()

        laboratory_id = laboratory_result[0] if laboratory_result else None
        cur.execute("SELECT * FROM machines WHERE makine_isim = ?", (machine_selection,))
        machine_result = cur.fetchone()

        machine_id = machine_result[0] if machine_result else None
        cur.execute("INSERT INTO menu_inputs (fakulte_id, laboratuvar_id, makine_id) VALUES (?, ?, ?)",(faculty_id, laboratory_id, machine_id))
        con.commit()

        updated_data = {
    'fakulte_id': faculty_id,
    'lab_id': laboratory_id,
    'machine_id': machine_id
}
        lastPID = get_last_panel_id()
        if lastPID:
            update_panel_data_menu(lastPID, updated_data)

        cur.execute("SELECT * FROM machines WHERE makine_isim = ?", (template,))
        machine_result = cur.fetchone()
        if machine_result:
            machine_id = machine_result[0]
            return redirect(url_for('machine_details', machine_id=machine_id))

    return redirect(url_for('mainPage')) 

def update_panel_data_menu(panel_id, updated_data):
    with sqlite3.connect(connectionStr) as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE panel
            SET fakulte_id = ?, lab_id = ?, makine_id = ?
            WHERE id = ?
        """, (updated_data['fakulte_id'], updated_data['lab_id'], updated_data['machine_id'], panel_id))
        con.commit()

@app.route('/<int:machine_id>', methods=['GET', 'POST'])
def machine_details(machine_id):
    if request.method == 'POST':
        if machine_id == 1:
            numune_sayisi = request.form['input1']
            eds = request.form['input2']
            edsd = request.form['input3']
            stem = request.form['input4']
            kaplama = request.form['input5']

            parametre_isimleri = ['Numune Sayısı', 'EDS', 'EBSD', 'STEM', 'Kaplama']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    # If the parameter is not found, you can throw an appropriate error or assign a default value.
                    parametre_idleri[parametre_isim] = None        

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'],1, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['EDS'], 1, eds))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['EBSD'], 1, edsd))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['STEM'], 1, stem))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Kaplama'], 1, kaplama))

            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)

            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id,current_datetime)
            return redirect(url_for('mainPage'))
        elif machine_id == 2:
            numune_sayisi = request.form['input1']
            numune_kalinligi = request.form['input2']
            ust_plaka_sicakligi = request.form['input3']
            alt_plaka_sicakligi = request.form['input4']
            ortalama_sicaklik = request.form['input5']

            parametre_isimleri = ['Numune Sayısı', 'Numune Kalınlığı', 'Üst Plaka Sıcaklığı', 'Alt Plaka Sıcaklığı', 'Ortalama Sıcaklık']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    # If the parameter is not found, you can throw an appropriate error or assign a default value.
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'],2, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Kalınlığı'], 2, numune_kalinligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Üst Plaka Sıcaklığı'], 2, ust_plaka_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Alt Plaka Sıcaklığı'], 2, alt_plaka_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Ortalama Sıcaklık'], 2, ortalama_sicaklik))

            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 3:
            numune_sayisi = request.form['input1']
            numune_kalinligi = request.form['input2']
            baslangic_sicakligi = request.form['input3']
            bitis_sicakligi = request.form['input4']
            olcum_nokta_sayisi = request.form['input5']
            atmosfer_ortami = request.form['input6']
            numune_boyutu = request.form['input7']    

            parametre_isimleri = ['Numune Sayısı', 'Numune Kalınlığı', 'Başlangıç Sıcaklığı', 'Bitiş Sıcaklığı', 'Ölçüm Nokta Sayısı','Atmosfer Ortamı','Numune Boyutu']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 3, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Kalınlığı'], 3, numune_kalinligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Başlangıç Sıcaklığı'],3, baslangic_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Bitiş Sıcaklığı'], 3, bitis_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Ölçüm Nokta Sayısı'], 3, olcum_nokta_sayisi)) 
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Atmosfer Ortamı'], 3, atmosfer_ortami))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Boyutu'], 3, numune_boyutu))         

            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)

            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)         

            return redirect(url_for('mainPage'))
        elif machine_id == 4:
            numune_sayisi = request.form['input1']
            numune_boyutlari = request.form['input2']
            baslangic_sicakligi = request.form['input3']
            bitis_sicakligi = request.form['input4']
            olcum_nokta_sayisi = request.form['input5']
            delta_t = request.form['input6']   

            parametre_isimleri = ['Numune Sayısı', 'Numune Boyutları', 'Başlangıç Sıcaklığı', 'Bitiş Sıcaklığı', 'Ölçüm Nokta Sayısı','Delta T']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 4, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Boyutları'], 4, numune_boyutlari))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Başlangıç Sıcaklığı'], 4, baslangic_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Bitiş Sıcaklığı'],4, bitis_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Ölçüm Nokta Sayısı'], 4, olcum_nokta_sayisi)) 
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Delta T'], 4, delta_t))  

            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)

            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 5:
            numune_sayisi = request.form['input1']
            lazer_secimi = request.form['input2']   

            parametre_isimleri = ['Numune Sayısı', 'Lazer Çeşidi']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 5, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Lazer Çeşidi'], 5, lazer_secimi))

            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 6:
            reaksiyon_sayisi = request.form['input1']
            numune_tipi = request.form['input2']
            rt_pcr_tespit_yontemi = request.form['input3']
            tespit_edilen_boya = request.form['input4']

            parametre_isimleri = ['Reaksiyon Sayısı', 'Numune Tipi', 'RT-PCR Tespit Yöntemi', 'Tespit Edilen Boya/Boyalar']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Reaksiyon Sayısı'], 6, reaksiyon_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Tipi'], 6, numune_tipi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['RT-PCR Tespit Yöntemi'], 6, rt_pcr_tespit_yontemi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Tespit Edilen Boya/Boyalar'], 6, tespit_edilen_boya))

            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 7:
            reaksiyon_sayisi = request.form['input1']
            numune_tipi = request.form['input2']
            rt_pcr_tespit_yontemi = request.form['input3']
            tespit_edilen_boya = request.form['input4']  

            parametre_isimleri = ['Reaksiyon Sayısı', 'Numune Tipi', 'RT-PCR Tespit Yöntemi', 'Tespit Edilen Boya/Boyalar']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Reaksiyon Sayısı'], 7, reaksiyon_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Tipi'], 7, numune_tipi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['RT-PCR Tespit Yöntemi'], 7, rt_pcr_tespit_yontemi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Tespit Edilen Boya/Boyalar'], 7, tespit_edilen_boya))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 8:
            numune_sayisi = request.form['input1']
            numune_tipi = request.form['input2']
            kullanilan_filtreler = request.form['input3']

            parametre_isimleri = ['Numune Sayısı', 'Numune Tipi', 'Kullanılan Filtre']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 8, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Tipi'], 8, numune_tipi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Kullanılan Filtre'], 8, kullanilan_filtreler))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 9:
            numune_sayisi = request.form['input1']
            numune_tipi = request.form['input2']
            kullanilan_filtreler = request.form['input3']

            parametre_isimleri = ['Numune Sayısı', 'Numune Tipi', 'Kullanılan Filtre']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 9, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Tipi'], 9, numune_tipi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Kullanılan Filtre'], 9, kullanilan_filtreler))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 10:
            numune_sayisi = request.form['input1']
            analiz_edilen_numune = request.form['input2']
            kullanilan_kolon = request.form['input3']  

            parametre_isimleri = ['Numune Sayısı', 'Analiz Edilen Numune', 'Kullanılan Kolon']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 10, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Analiz Edilen Numune'], 10, analiz_edilen_numune))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Kullanılan Kolon'],10, kullanilan_kolon))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 11:
            numune_sayisi = request.form['input1']
            numune_kaynagi = request.form['input2']
            dizileme_tipi = request.form['input3']
            kullanilan_cip = request.form['input4']

            parametre_isimleri = ['Numune Sayısı','Numune Kaynağı', 'Dizileme Tipi', 'Kullanılan Çip']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 11, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Kaynağı'], 11, numune_kaynagi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Dizileme Tipi'], 11, dizileme_tipi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Kullanılan Çip'], 11, kullanilan_cip))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 12:
            numune_sayisi = request.form['input1']
            analiz_edilen_numune = request.form['input2']
            kullanilan_kolon = request.form['input3']    

            parametre_isimleri = ['Numune Sayısı', 'Analiz Edilen Numune', 'Kullanılan Kolon']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 12, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Analiz Edilen Numune'], 12, analiz_edilen_numune))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Kullanılan Kolon'], 12, kullanilan_kolon))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 13:
            numune_sayisi = request.form['input1']
            analiz_edilen_numune = request.form['input2']
            kullanilan_kolon = request.form['input3']   

            parametre_isimleri = ['Numune Sayısı', 'Analiz Edilen Numune', 'Kullanılan Kolon']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 13, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Analiz Edilen Numune'], 13, analiz_edilen_numune))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Kullanılan Kolon'], 13, kullanilan_kolon))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 14:
            numune_sayisi = request.form['input1']
            numune_tipi = request.form['input2']  

            parametre_isimleri = ['Numune Sayısı', 'Numune Tipi']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Sayısı'], 14, numune_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Numune Tipi'],14, numune_tipi))
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
        elif machine_id == 15:
            baslangic_sicakligi = request.form['input1']
            bitis_sicakligi = request.form['input2']
            isitma_hizi = request.form['input3']
            atmosfer_ortami = request.form['input4']
            dongu_sayisi = request.form['input5']
            gaz_debisi = request.form['input6']    

            parametre_isimleri = ['Başlangıç Sıcaklığı', 'Bitiş Sıcaklığı', 'Isıtma Hızı', 'Atmosfer Ortamı', 'Döngü Sayısı','Gaz Debisi']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Başlangıç Sıcaklığı'], 15, baslangic_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Bitiş Sıcaklığı'], 15, bitis_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Isıtma Hızı'], 15, isitma_hizi))       
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Atmosfer Ortamı'], 15, atmosfer_ortami))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Döngü Sayısı'], 15, dongu_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Gaz Debisi'], 15, gaz_debisi))                 
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))

        elif machine_id == 16:
            baslangic_sicakligi = request.form['input1']
            bitis_sicakligi = request.form['input2']
            isitma_hizi = request.form['input3']
            atmosfer_ortami = request.form['input4']
            dongu_sayisi = request.form['input5']
            gaz_debisi = request.form['input6'] 

            parametre_isimleri = ['Başlangıç Sıcaklığı', 'Bitiş Sıcaklığı', 'Isıtma Hızı', 'Atmosfer Ortamı', 'Döngü Sayısı','Gaz Debisi']
            parametre_idleri = {}
            con = sqlite3.connect(connectionStr)
            cur = con.cursor()

            for parametre_isim in parametre_isimleri:
                cur.execute("SELECT id FROM parameters WHERE parametre_isim = ?", (parametre_isim,))
                result = cur.fetchone()
                if result:
                    parametre_idleri[parametre_isim] = result[0]
                else:
                    parametre_idleri[parametre_isim] = None 

            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Başlangıç Sıcaklığı'], 16, baslangic_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Bitiş Sıcaklığı'], 16, bitis_sicakligi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Isıtma Hızı'], 16, isitma_hizi))       
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Atmosfer Ortamı'],16, atmosfer_ortami))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Döngü Sayısı'], 16, dongu_sayisi))
            cur.execute("INSERT INTO experiment (parametre_id, makine_id, parametre_deger) VALUES (?, ?, ?)", (parametre_idleri['Gaz Debisi'], 16, gaz_debisi))                      
            con.commit()
            cur.execute("SELECT id FROM experiment WHERE makine_id = ? ORDER BY id DESC LIMIT 1", (1,))
            deney_id_result = cur.fetchone()
            deney_id = deney_id_result[0] if deney_id_result else None

            param_value_dict = {}
            for param_name in parametre_idleri.keys():
                param_value_dict[param_name] = request.form.get(param_name, None)
            lastPID = get_last_panel_id()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_panel_data_parameter(lastPID, parametre_idleri, deney_id, current_datetime)                
            return redirect(url_for('mainPage'))
    return render_template(f"{machine_id}.html")

if __name__ == '__main__':

    app.run(debug=True)

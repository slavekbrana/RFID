from flask import Flask, render_template, request, redirect
from datetime import datetime
import csv
import os

app = Flask(__name__)
DATA_FILE = 'dochazka.csv'
USERS_FILE = 'uzivatele.csv'



def nacti_uzivatele():
    uzivatele = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='r', encoding='utf-8') as f:
            radky = csv.reader(f)
            for radek in radky:
                if len(radek) >= 2:
                    uzivatele[radek[0]] = radek[1]
    return uzivatele


def zapis_do_csv(cip, jmeno, akce):
    cas = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([cas, cip, jmeno, akce])


@app.route('/')
def index():
    zaznamy = []
    pritomni = {}
    uzivatele = nacti_uzivatele()

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            radky = list(csv.reader(f))
            zaznamy = radky[-50:]

            for radek in radky:
                if len(radek) >= 4:
                    jmeno = radek[2]
                    stav = radek[3]
                    if stav == "PŘÍCHOD":
                        pritomni[jmeno] = True
                    else:
                        pritomni.pop(jmeno, None)

    return render_template('index.html', zaznamy=zaznamy, pritomni=pritomni.keys(), seznam_lidi=uzivatele)


@app.route('/pipnuti', methods=['POST'])
def pipnuti():
    kod_cipu = request.form.get('cip_id').strip()
    uzivatele = nacti_uzivatele()

    if not kod_cipu or kod_cipu not in uzivatele:
        return redirect('/')

    jmeno = uzivatele[kod_cipu]
    stav = "PŘÍCHOD"

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            radky = list(csv.reader(f))
            for radek in reversed(radky):
                if len(radek) >= 4 and radek[1] == kod_cipu:
                    stav = "ODCHOD" if radek[3] == "PŘÍCHOD" else "PŘÍCHOD"
                    break

    zapis_do_csv(kod_cipu, jmeno, stav)
    return redirect('/')


@app.route('/pridat_uzivatele', methods=['POST'])
def pridat_uzivatele():
    jmeno = request.form.get('jmeno').strip()
    cip = request.form.get('novy_cip').strip()

    if jmeno and cip:
        with open(USERS_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([cip, jmeno])

    return redirect('/')


@app.route('/smazat_uzivatele', methods=['POST'])
def smazat_uzivatele():
    cip_k_vymazani = request.form.get('cip_smazat')
    uzivatele = nacti_uzivatele()

    if cip_k_vymazani in uzivatele:

        del uzivatele[cip_k_vymazani]
        with open(USERS_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for cip, jmeno in uzivatele.items():
                writer.writerow([cip, jmeno])

        if os.path.exists(DATA_FILE):
            zbyle_zaznamy = []
            with open(DATA_FILE, mode='r', encoding='utf-8') as f:
                radky = list(csv.reader(f))
                for radek in radky:
                    if len(radek) >= 4 and radek[1] != cip_k_vymazani:
                        zbyle_zaznamy.append(radek)

            with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for radek in zbyle_zaznamy:
                    writer.writerow(radek)

    return redirect('/')


# ----------------------------------------

@app.route('/smazat', methods=['POST'])
def smazat():
    if os.path.exists(DATA_FILE):
        pritomni_zaznamy = []
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            radky = list(csv.reader(f))
            stav_lidi = {}
            for radek in radky:
                if len(radek) >= 4:
                    stav_lidi[radek[1]] = radek
            for cip, posledni_radek in stav_lidi.items():
                if posledni_radek[3] == "PŘÍCHOD":
                    pritomni_zaznamy.append(posledni_radek)

        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for radek in pritomni_zaznamy:
                writer.writerow(radek)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
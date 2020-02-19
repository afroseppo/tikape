import sqlite3
from datetime import datetime


# luodaan sqlite3 tietokantayhteys
db = sqlite3.connect('testi.db')
db.isolation_level = None

c = db.cursor()

# komentorivisovelluksen käyttöliittymä


def UI():
    print('''Tervetuloa pakettiseurantatietokantaan. Alla komennot:
    1. Luo tietokanta
    2. Lisää uusi paikka tietokantaan
    3. Lisää uusi asiakas
    4. Lisää uusi paketti
    5. Lisää uusi tapahtuma
    6. Hae paketin tapahtumat
    7. Hae asiakkaan paketit
    8. Hae tapahtumat päivämäärällä
    9. Suorita tehokkuustesti
    x. Poistu tietokannasta
    ''')

    while True:
        komento = input("Syötä komento (1-9 tai X poistuaksesi): ")

        if komento == 'X':
            db.close()
            break

        if komento not in '123456789':
            print('Komentoa ei löydy')
        else:
            switcher = {
                '1': luo_tietokanta,
                '2': lisaa_paikka,
                '3': lisaa_asiakas,
                '4': lisaa_paketti,
                '5': lisaa_tapahtuma,
                '6': hae_paketin_tapahtumat,
                '7': hae_asiakkaan_paketit,
                '8': hae_tapahtumat_pvm,
                '9': suorita_tehokkuustesti
            }

            func = switcher.get(komento, lambda: 'Komentoa ei löydy')
            func()


def luo_tietokanta():
    try:
        c.execute("CREATE TABLE Paikka (id INTEGER PRIMARY KEY, nimi TEXT UNIQUE)")
        c.execute("CREATE TABLE Asiakas (id INTEGER PRIMARY KEY, nimi TEXT UNIQUE)")
        c.execute("CREATE TABLE Tapahtuma (id INTEGER PRIMARY KEY, paketti_id INTEGER REFERENCES Paketti, paikka_id INTEGER REFERENCES Paikka, kuvaus TEXT, aika DATETIME, aikastr TEXT)")
        c.execute(
            "CREATE TABLE Paketti (id INTEGER PRIMARY KEY, asiakas_id INTEGER REFERENCES Asiakas, seurantakoodi TEXT UNIQUE)")

        print('Tietokantaan on luotu seuraavat taulut: Paikka, Asiakas, Tapahtuma sekä Paketti')

    except:
        print("Suorituksessa tapahtui virhe.")


def lisaa_paikka():
    paikka = input("Anna paikan nimi: ")

    try:
        c.execute("INSERT INTO Paikka(nimi) VALUES (?)", [paikka])
        print(f'Paikka {paikka} lisätty id:llä {c.lastrowid}')
    except:
        print('Tällä nimellä on jo olemassa paikka.')


def lisaa_asiakas():
    asiakas = input("Anna asiakkaan nimi: ")

    try:
        c.execute("INSERT INTO Asiakas(nimi) VALUES (?)", [asiakas])
        print(f'Asiakas {asiakas} lisätty id:llä {c.lastrowid}')
    except:
        print('Tällä nimellä on jo asiakas.')


def lisaa_paketti():
    seurantakoodi = input("Anna paketin seurantakoodi: ")
    asiakas = input("Anna asiakkaan nimi: ")

    c.execute("SELECT id FROM Asiakas where nimi=?", [asiakas])
    asiakasid = c.fetchone()

    if asiakasid == None:
        print(f"VIRHE: Asiakasta nimellä {asiakas} ei ole olemassa.")
    else:
        try:
            c.execute("INSERT INTO Paketti(seurantakoodi, asiakas_id) VALUES (?,?)", [
                      seurantakoodi, asiakasid[0]])
            print(
                f"Paketti seurantakoodilla {seurantakoodi} asiakkaalle {asiakas} lisätty.")
        except:
            print("Virhe suorituksessa")


def lisaa_tapahtuma():
    seurantakoodi = input("Anna paketin seurantakoodi: ")

    c.execute("SELECT id FROM Paketti WHERE seurantakoodi=?", [seurantakoodi])
    paketti_id = c.fetchone()

    if paketti_id == None:
        print("VIRHE: Seurantakoodia ei löydy!")
    else:
        paikka = input("Anna paikka: ")
        c.execute("SELECT id FROM Paikka where nimi=?", [paikka])
        paikka_id = c.fetchone()

        if paikka_id == None:
            print("VIRHE: Paikkaa ei löydy!")
        else:
            kuvaus = input("Anna kuvaus: ")

            if kuvaus != '':
                c.execute("INSERT INTO Tapahtuma(paketti_id, paikka_id, aika, kuvaus) VALUES (?, ?, DateTime('now'), ?)", [
                          paketti_id[0], paikka_id[0], kuvaus])

                print(
                    f"Tapahtuma {kuvaus} on lisätty paketille seurantakoodilla {seurantakoodi} paikassa {paikka}")
            else:
                print("Ei kuvausta annettu, kuvaus ei voi olla tyhjä!")


def hae_paketin_tapahtumat():
    seurantakoodi = input("Anna paketin seurantakoodi: ")

    try:
        c.execute("SELECT strftime('%d.%m.%Y, %H:%M', aika), p.nimi, kuvaus FROM Tapahtuma t LEFT JOIN Paikka p on t.paikka_id = p.id LEFT JOIN Paketti pk on t.paketti_id = pk.id WHERE seurantakoodi=?", [
                  seurantakoodi])
        rows = c.fetchall()

        if not rows:
            print("Seurantakoodia ei ole!")
        else:
            for row in rows:
                print(f"{row[0]}, {row[1]}, {row[2]}")
    except:
        print("Virheellinen haku!")


def hae_asiakkaan_paketit():
    asiakas = input("Anna asiakkaan nimi: ")

    try:
        c.execute(
            "SELECT seurantakoodi, count(t.id) FROM Paketti p LEFT JOIN Tapahtuma t on p.id = t.paketti_id LEFT JOIN Asiakas a on p.asiakas_id = a.id WHERE a.nimi=?", [asiakas])

        rows = c.fetchall()

        if not rows:
            print("Asiakkaalla ei ole yhtään pakettia.")
        else:
            for row in rows:
                print(f"{row[0]}: {row[1]} tapahtumaa")

    except:
        print("Virhe!")


def hae_tapahtumat_pvm():
    paikka = input("Anna paikka: ")

    try:
        c.execute("SELECT id FROM Paikka WHERE nimi=?", [paikka])
        paikkaid = c.fetchone()

        if not paikkaid:
            print("Paikkaa ei ole olemassa.")
        else:
            pvm = input("Anna päivämäärä: ")

            c.execute("SELECT count(id) FROM Tapahtuma WHERE strftime('%d.%m.%Y', aika)=? and paikka_id=?", (pvm, paikkaid[0]))

            rows = c.fetchall()

            for row in rows:
                print(f'Tapahtumien määrä: {row[0]}')
    except:
        print("VIRHE!")

def suorita_tehokkuustesti():
    pass


UI()

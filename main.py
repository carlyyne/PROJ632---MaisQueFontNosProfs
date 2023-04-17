from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3 as sql
import ModuleResponsable as mR
import Archives  as A

def creationDatabase():
    curs.execute("""CREATE TABLE IF NOT EXISTS Professeur (
                    idProfesseur INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nom VARCHAR,
                    Prenom VARCHAR
                )""")
    curs.execute("""CREATE TABLE IF NOT EXISTS Module (
                    idModule INTEGER PRIMARY KEY AUTOINCREMENT, 
                    Code VARCHAR, 
                    Intitule VARCHAR
                )""")
    curs.execute("""CREATE TABLE IF NOT EXISTS ProfModule (
                    idProf INTEGER REFERENCES Professeur (idProfesseur),
                    idMod INTEGER REFERENCES Module (idModule)
                )""")
    curs.execute("""CREATE TABLE IF NOT EXISTS Archive (
                    idArchive INTEGER PRIMARY KEY AUTOINCREMENT,
                    URLArchive TEXT,
                    TitreArchive TEXT,
                    idProf INTEGER REFERENCES Professeur (idProfesseur)
                )""")
    
def afficherProfsBDD(curs):
    curs.execute("SELECT Nom, Prenom FROM Professeur")
    rows = curs.fetchall()
    
    for row in rows:
        nomPrenoms = row[0]+" "+row[1]
        print(nomPrenoms)

def afficherModulesBDD(curs):
    curs.execute("SELECT Code, Intitule FROM Module")
    rows = curs.fetchall()
    for row in rows:
        if row[0] == "":
            module = row[1]
        else:
            module = row[0]+" "+row[1]
        print(module)
    
def menu(curs,conn):
    res = True
    while(res):
        print("\nVeuillez choisir une option:")
        print("1 - Rechercher les modules et leurs responsables")
        print("2 - Récupérer les articles associés aux professeurs (avoir fait l'option 1 avant)")
        print("3 - Afficher le graphique montrant le nombre de modules dont chaque professeur est responsable (avoir fait l'option 1 avant)")
        print("4 - Afficher les professeurs de la base de données (avoir fait l'option 1 avant)")
        print("5 - Afficher les modules de la base de données (avoir fait l'option 1 avant)")
        print("6 - Quitter le menu")
        reponse = input("\nVotre choix (1,2,3,4,5,6):")

        if reponse == "1":
            ########## OPTION 1 - n RECUPERATION DE DONNEES dans l'intranet de Polytech #########
            driver.get("https://www.polytech.univ-smb.fr/intranet/scolarite/programmes-ingenieur.html")
            mR.RecuperationModuleResponsable(driver,curs,conn)
        if reponse == "2":
            ########## OPTION 2 - RECUPERATION DES ARTICLES ASSOCIES dans hal  #########
            driver.get("https://hal.archives-ouvertes.fr/") 
            A.recuperationArticle(driver,curs,conn)
        if reponse == "3":
            mR.compteNbModuleParProf(curs)
        if reponse == "4":
            afficherProfsBDD(curs)
        if reponse == "5":
            afficherModulesBDD(curs)
        if reponse == "6":
            res = False
        else:
            print("Veuillez choisir un numéro entre 1, 2, 3, 4, 5 et 6")


if __name__ == "__main__":

    ########## Masquage du webScraping ##########
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'

    # configuration des options de Chrome
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')

    # création de l'objet de service Chrome
    chrome_service = webdriver.chrome.service.Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=options)

    ########## INITIALISATION ET CREATION DATABASE #########
    conn = sql.connect("database.db")
    curs = conn.cursor()
    creationDatabase()

    ########## Affichage du menu ##########
    menu(curs,conn)
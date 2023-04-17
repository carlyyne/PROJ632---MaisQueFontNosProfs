from selenium.webdriver.common.by import By
import time
import unicodedata
import matplotlib.pyplot as plt
import mplcursors
import getpass


def IdentificationIntranet(driver):

    #validation cookies
    res=False
    while res==False:
        try:
            driver.find_element(By.XPATH,"/html/body/div[4]/div[3]/button[1]").click()
            res=True
        except:
            time.sleep(1)
    
    """ Entrer dans le terminal l'identifiant et le mot de passe"""
    #identifiant
    driver.find_element(By.XPATH,"/html/body/section[3]/div/div/div/div/div/form/fieldset/input[1]").send_keys(input('Identifiant:'))
    #mot de passe
    driver.find_element(By.XPATH,"/html/body/section[3]/div/div/div/div/div/form/fieldset/input[2]").send_keys(getpass.getpass('Mot de passe:')) 

    """ Recherche dans fichier id.txt le terminal l'identifiant et le mot de passe"""
    """
    f = open("/Users/carlynebarrachin/Documents/Polytech/FI3/S6/PROJ632-SCRAPING/Profs/id.txt", "r")
    lines = f.read().splitlines() #affichier le contenu dans une liste, par ligne, sans \n
    driver.find_element(By.XPATH,"/html/body/section[3]/div/div/div/div/div/form/fieldset/input[1]").send_keys(lines[0])
    driver.find_element(By.XPATH,"/html/body/section[3]/div/div/div/div/div/form/fieldset/input[2]").send_keys(lines[1]) 
    """
    #cliquer sur le bouton identification
    driver.find_element(By.XPATH,"/html/body/section[3]/div/div/div/div/div/form/fieldset/input[3]").click()

def AccesRubriqueProgrammes(driver):
    #cliquer sur la rubrique PROGRAMMES
    res=False
    while res==False:
        try:
            driver.find_element(By.XPATH,"/html/body/div[1]/div[5]/a").click()
            res=True
        except:
            time.sleep(0.1)
    
    #cliquer sur la loupe afin d'avoir tous les modules quelque soit la spécialité, le semestre...
    res=False
    while res==False:
        try:
            driver.find_element(By.XPATH,"//*[@id='c3506']/div/div/form/div[2]/button[1]").click()
            res=True
        except:
            time.sleep(0.1) 

def RecuperationLiensModules(driver):
    liens = []
    elements = driver.find_elements(By.CSS_SELECTOR,'.intitule a')
    for element in elements:
        lien = element.get_attribute('href')
        if lien:
            liens.append(lien)
    return liens


def ajoutInformations(driver,curs,conn):
    lienModules = RecuperationLiensModules(driver)
    idMod = None
    for lien in lienModules:
        driver.get(lien)
        infosModule = driver.find_element(By.CLASS_NAME,'titleLabel').text
        infosProf = driver.find_element(By.XPATH,'//*[@id="c853"]/div/div[2]/div[2]/div[3]/div[2]/div[2]').text #oblige de faire par XPATH car il existe plusieurs elements ayant un nom de classe similaire

        idMod = récupérationInfosModule (curs,conn,infosModule)
        
        if infosProf != "":
            if infosProf.__contains__(';'):
                listeProfs = infosProf.split(';')
            else:
                listeProfs = [infosProf]
            for prof in listeProfs:
                infoProf = prof.split('@')[0]
                if infoProf.__contains__('.'):
                    nomPrenom = infoProf.split(".")
                    Prenom = nomPrenom[0].strip().lower().title()
                    Nom = nomPrenom[1].strip().upper()
                else:
                    nomPrenom = driver.find_element(By.XPATH,'//*[@id="c853"]/div/div[2]/div[2]/div[3]/div[1]/div[2]').text.split(" ")
                    Prenom = unicodedata.normalize('NFKD',nomPrenom[0].strip().lower().title())
                    Nom = unicodedata.normalize('NFKD',nomPrenom[1].strip().upper())
                if Nom[-1] == ",": #enleve les cas ou il y a une virgule à la fin
                    Nom = Nom[:-1]
                idProf = ajoutProfBaseDonnee(curs,conn,Nom,Prenom)

                ajoutRelationProfModuleBaseDonnee(curs,conn,idMod,idProf)


def récupérationInfosModule (curs,conn,infosModule):

    idMod = None
        
    #Verifie qu'il y a bien un module pour récupérer les informations
    #Suppression des espaces avant et apres le code et l'intitule
    if infosModule != ": -" :
        infosModule = infosModule.split(':')
        Code = infosModule[0].strip()
        Intitule = infosModule[1].strip()
        if Intitule[-1] == "-": #enleve les cas ou il y a un tiret seul a la fin
            Intitule = Intitule[:-1]            
        if Intitule != " Au choix ": #enleve les cas ou l'intitulé est "Au choix": ce n'est pas une matiere
            idMod = ajoutModuleBaseDonnee(Code,Intitule,curs,conn)
    return idMod

def ajoutRelationProfModuleBaseDonnee(curs,conn,idMod,idProf):
    """Insertion dans ProfModule la relation n'existe pas déjà"""
    if idMod != None:
            cProfMod=curs.execute(f"SELECT idProf, idMod FROM ProfModule WHERE idProf LIKE '{idProf}' AND idMod LIKE '{idMod}'")
            tabProfMod = cProfMod.fetchall()
            if (len(tabProfMod) == 0):
                curs.execute(f"INSERT INTO ProfModule (idProf,idMod) VALUES('{idProf}','{idMod}')")
                conn.commit()    

def ajoutModuleBaseDonnee(code,intitule,curs,conn):
    """ Recherche et ajout du module dans la base de donnée (s'il n'y est pas deja) """

    cMod=curs.execute("SELECT idModule FROM Module WHERE Code LIKE ? AND Intitule LIKE ?", (code, intitule))

    tabMod = cMod.fetchall()
    if (len(tabMod)==0):
        curs.execute("INSERT INTO Module(Code,Intitule) VALUES(?, ?)", (code, intitule))
        idMod=curs.lastrowid
        conn.commit()
    else:
        idMod=tabMod[0][0]
    return idMod

def ajoutProfBaseDonnee(curs,conn,nom,prenom):
    """ Recherche et ajout du nomPrénom dans la base de donnée (s'il n'y est pas deja) """

    cPers=curs.execute(f"SELECT idProfesseur FROM Professeur WHERE Nom LIKE '{nom}' AND Prenom LIKE '{prenom}'")

    #Cas où le prenom n'est pas dans la base de donnée et qu'il y en a bien un dans la case 'Responsable' associe au module
    idProf=0
    tabPers = cPers.fetchall()
    if nom!="" and prenom!="":
        if len(tabPers) == 0:
            curs.execute(f"INSERT INTO Professeur (Nom,Prenom) VALUES('{nom}','{prenom}')")
            idProf=curs.lastrowid
            conn.commit()
        else:
            for row in tabPers:
                idProf = row[0]
    return idProf

def compteNbModuleParProf(curs):

    #compte le nombre de modules dont chaque prof est responsable
    curs.execute("SELECT idProf, count(idProf) AS nb FROM ProfModule GROUP BY idProf ORDER BY nb DESC")
    rows = curs.fetchall()
    
    # Création des listes de données (Nom Prenom du professeur et le nombre de modules)
    noms = []
    valeurs = []
    for row in rows:
        curs.execute(f"SELECT Nom, Prenom FROM Professeur WHERE idProfesseur='{row[0]}'")
        rows = curs.fetchone()
        noms.append(rows[0]+" "+rows[1])
        valeurs.append(row[1])

    # Création du graphique
    fig, ax = plt.subplots()
    bars = ax.bar(noms, valeurs,width=0.7)
    plt.style.use('fivethirtyeight')
    ax.set(xlabel='Professeur', ylabel='Nombre total de modules',title='Responsables de modules')
    plt.xticks(rotation=90)
    plt.yticks(valeurs)

    # Ajustement des marges
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.3)

    # Ajout de la fonctionnalité de survol
    cursor = mplcursors.cursor(bars, hover=True)
    def on_hover(sel):

        # Récupérer la position x du curseur
        x_pos = sel.target[0]
        sup = x_pos + 0.5

        # Récupérer le nom et le prenom correspondant au placement du curseur
        if  int(x_pos) == int(sup):
            nom_prof = noms[int(x_pos)]
        else:
            nom_prof = noms[int(sup)]

        # Récupérer l'id du professeur
        curs.execute(f"SELECT idProfesseur FROM Professeur WHERE Nom = '{nom_prof.split()[0]}' AND Prenom = '{nom_prof.split()[1]}'")
        id_prof = curs.fetchone()[0]

        # Rechercher les modules dont le professeur est responsable
        curs.execute(f"SELECT m.Code FROM Module as m JOIN ProfModule as pm ON m.idModule = pm.idMod WHERE pm.idProf = {id_prof}")
        modules = curs.fetchall()
        txtModule = "\n".join([module[0] for module in modules])
        sel.annotation.set_text(txtModule)
        sel.annotation.set_backgroundcolor('pink')

    cursor.connect("add", on_hover)
    plt.show()
    

def RecuperationModuleResponsable(driver,curs,conn):
    IdentificationIntranet(driver)
    AccesRubriqueProgrammes(driver)
    ajoutInformations(driver,curs,conn)
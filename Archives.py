from selenium.webdriver.common.by import By
from ModuleResponsable import *
import re

def rechercheProfsBDD(curs):
    """ Recherche d'un professeur dans la base de donnees"""
    c=curs.execute(f"SELECT Nom, Prenom FROM Professeur")
    listeNomsPrenoms = c.fetchall()
    return listeNomsPrenoms

def recherchePremierProfBarreRecherche(driver,listeNomsPrenoms):
    #ajout de "" autour du nom prenom pour avoir accès seulement aux articles de la personne et pas à ceux ayant le même nom ou le même prenom
    nomPrenom = f"'{listeNomsPrenoms[0][0]} {listeNomsPrenoms[0][1]}'"
    #Ecrire le premier prenom dans le moteur de recherche
    driver.find_element(By.XPATH,"//*[@id='searchNG']/div/div/div/input").send_keys(nomPrenom)
    #cliquer sur le bouton Recherche
    driver.find_element(By.XPATH,"//*[@id='searchNG']/div/div/div/button").click()

def rechercheProfs(i,driver,listePrenoms):
    if i < len(listePrenoms)-1:
        #Ecrire tous les autres prenoms dans le moteur de recherche en supprimant celui déjà present dans la barre de recherche
        Nom = listePrenoms[i+1][0]
        Prenom = listePrenoms[i+1][1]
        NomPrenom = f"'{Nom} {Prenom}'"
        driver.find_element(By.XPATH,"//*[@id='littleSearchBar']").clear()
        driver.find_element(By.XPATH,"//*[@id='littleSearchBar']").send_keys(NomPrenom)

        #cliquer sur le bouton Recherche
        driver.find_element(By.XPATH,"//*[@id='searchHeaderNG']/button").click()

def recuperationArticle(driver,curs,conn):

    listePrenoms = rechercheProfsBDD(curs)
    recherchePremierProfBarreRecherche(driver,listePrenoms)

    for i in range (0,len(listePrenoms)):

        #recherche l'id du Professeur associé au nom et au prenom
        cProf=curs.execute(f"SELECT idProfesseur FROM Professeur WHERE Nom LIKE '{listePrenoms[i][0]}' AND Prenom LIKE '{listePrenoms[i][1]}'")
        tabProf = cProf.fetchall()
        idProf=tabProf[0][0]

        #recuperation des URL du premier article et de son titre
        try:
            Resultats = driver.find_element(By.XPATH,f"/html/body/main/section/section[2]/div[1]/div[1]/span").text
            nbResultats = int(re.findall('\d+', Resultats)[0])
        except:
            nbResultats=0

        if nbResultats > 0: #verifie qu'il y a au moins 1 résultat: 1 article correspondant
            for j in range(1,2): # for j in range (1,nbResultats+1) pour tous les articles
                titre = driver.find_element(By.XPATH,f"/html/body/main/section/section[2]/table/tbody/tr[{j}]/td[3]/a/h3").text
                URL = driver.find_element(By.XPATH,f"/html/body/main/section/section[2]/table/tbody/tr[{j}]/td[3]/a").get_attribute("href")
            
                #les ' posent des problèmes dans INSERT car on ecrit '{URL}'
                titre = re.sub(r"'","",titre) 
                URL = re.sub(r"'","", URL)

                #Creation de l'archive si elle n'existe pas dans la base
                cArch=curs.execute(f"SELECT idArchive FROM Archive WHERE URLArchive LIKE '{URL}'")
                tabArch = cArch.fetchall()

                if (len(tabArch)==0):
                    curs.execute(f"INSERT INTO Archive(URLArchive, TitreArchive, idProf) VALUES ('{URL}', '{titre}', '{idProf}')")
                    conn.commit()

        else:
            print(f"Aucun article associé au professeur {idProf}!")
        
        rechercheProfs(i,driver,listePrenoms)
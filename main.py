#
#	SCRAPING JOBUP
#
#	Ce fichier contient le coeur du programme
#	et sert à piloter les différentes parties
#	de celui-ci
import os
from EDatabase import EDatabase
from EJob import EJob
from EScraper import EScraper
from EAddress import EAddress
from EHelper import EHelper
from ECompany import ECompany
from time import sleep
from os import remove
from EScraper import HTTP_CODES
from math import floor
import json
#Temps d'attente avant de scraper chaque page
SLEEP_TIME_BETWEEN_PAGES = 2
#Temps d'attente entre le scraping de chaque job
SLEEP_TIME_BETWEEN_JOBS = 0.2
DEBUG = 0
if DEBUG == 1:
    try:
        remove('jobup.db')
    except:
        pass

if(EDatabase.countJobs() == 0):
    #Si il y a 0 jobs en DB, c'est le premier lancement et il
    #faut scraper les 2000 derniers postes
    #Les pages sont scrapés séquentiellement (du poste le plus récent au plus ancien)
    searchPages = EScraper.getAllAvailableJobIDsFromJobup()
    #On veut cependant stocker les postes du plus ancien au plus récent (le poste avec l'id la plus élevée devrait être le plus récent)
    #Pour ce faire, on va inverser la liste de pages, puis la liste d'id dans chaque page
    searchPages.reverse()
    [page.reverse() for page in searchPages]
    #Nombre de jobs total = nb pages * nb résultat par page
    nbJobs = len(searchPages) * len(searchPages[0])
    currScraped = 0

    for page in searchPages:
        for jobID in page:
            job = EScraper.getJobFromID(jobID)
            currScraped += 1
            if type(job) is HTTP_CODES:
                print('')
                EHelper.printError(f"Erreur lors du scraping du poste à l'ID {jobID}", job.name)
                continue
            
            progressStr = f"{currScraped}/{nbJobs}"
            EHelper.printInfo("Job scrapé, insertion dans la DB", progressStr)
            EDatabase.insertJob(job)
            EHelper.printInfo(f"Job inséré, pause de {SLEEP_TIME_BETWEEN_JOBS}s", progressStr)
            sleep(SLEEP_TIME_BETWEEN_JOBS)

        print('')
        progressStr = f"{int(currScraped / nbJobs * 100)}%"
        EHelper.printInfo(f"Page scrapée, sauvegarde des données...", progressStr)
        EDatabase.saveChanges()
        if currScraped < nbJobs:
            EHelper.printInfo(f"Pause de {SLEEP_TIME_BETWEEN_PAGES}s", progressStr)
            sleep(SLEEP_TIME_BETWEEN_PAGES)
            print('')
else:
    
    lastJob:EJob = EScraper.getLastPostedJob()
    #Si le dernier job posté existe déjà en DB, il n'y a rien à scraper
    #et le script peut terminer son exécution
    if EDatabase.jobExists(lastJob.job_id):
        exit()
    
    print("Recherche des nouveaux postes depuis " + str(lastJob.job_id))
    newJobs = EScraper.getAllNewJobs(lastJob.job_id)
    print(f"{len(newJobs)} nouveaux postes trouvés, insertion dans la DB")
    #On inverse la liste de jobs, car ceux-ci sont scrapés séquentiellement, du plus récent au plus ancien
    newJobs.reverse()
    for job in newJobs:
        EDatabase.insertJob(job)
    print("Tous les postes ont été insérés")
    EDatabase.saveChanges()        
    print("Modifications enregistrées")

#@TODO SELECT company_id from jobs WHERE company_id NOT IN (SELECT company_id FROM companies)
# On SELECT l'ID de toutes les entreprises qui ne sont pas encore en db
# On les scrape, puis on les ajoute
missingCompanies = EDatabase.getAllMissingCompaniesID()
nbMissing = len(missingCompanies)
hiddenCompanies:list = []
if type(missingCompanies) is list and nbMissing > 0:
    print(f"\r\n{nbMissing} entreprises à scraper")
    companies:list = []
    i = 0
    for compID in missingCompanies:
        i += 1
        EHelper.printInfo(f'Scraping entreprise {compID[0]}', f"{i}/{nbMissing}")
        tmp  = EScraper.getCompanyFromID(compID[0])
        if type(tmp) is HTTP_CODES:
            EHelper.printError(f"L'entreprise {compID} est cachée", tmp.name)
            hiddenCompanies.append(compID)
            print('')
            continue
        EDatabase.insertCompany(tmp)
    
    print("\r\nToutes les entreprises ont été ajoutées à la DB")
    print(f"Suppression des {len(hiddenCompanies)} entreprises cachées")
    for companyID in hiddenCompanies:
        EDatabase.updateJobCompanyID(companyID[0], '')
    print("Suppression terminée")
    EDatabase.saveChanges()
        
print("Scraping complété, fin de l'éxécution")


def insertCompanyIfNotExists(id:str) -> bool:
    """Ajoute l'entreprise avec l'ID spécifiée en base de données si celle-ci n'y est pas

    Args:
        id (str): l'ID de l'entreprise à ajouter
    Returns:
        bool: Est-ce que l'entreprise a été ajoutée
    """
    if EDatabase.companyExists(id) is not True:
        comp:ECompany = EScraper.getCompanyFromID(id)
        if(comp is not None):
            EDatabase.insertCompany(comp)
            return True
    return False
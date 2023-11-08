#
#   SCRAPING JOBUP
#
#   Ce fichier contient tout ce qui touche au scraping
#   Utilisation: from EScraper import EScraper

import json
import requests
from time import sleep
from pprint import pprint
from EJob import EJob
from ECompany import ECompany
from EHelper import EHelper
from enum import Enum
from typing import Union

class API(Enum):
    BASE = "https://www.jobup.ch/api/v1/public"
    SEARCH = BASE + '/search'
    JOB = SEARCH + '/job/'
    COMPANY = BASE + '/company/'
    IT_CATEGORIES = 'category-ids%5B0%5D=702&category-ids%5B1%5D=703&category-ids%5B2%5D=704&category-ids%5B3%5D=705&category-ids%5B4%5D=706&category-ids%5B5%5D=707&category-ids%5B6%5D=708&category-ids%5B7%5D=709&category-ids%5B8%5D=710&category-ids%5B9%5D=711&category-ids%5B10%5D=712&category-ids%5B11%5D=713&category-ids%5B12%5D=714&category-ids%5B13%5D=715'
    SEARCH_IT = f"{SEARCH}?{IT_CATEGORIES}"

class HTTP_CODES(Enum):
    """ Le premier chiffre des codes de statut HTML représentent le type de status
        2XX -> Pas d'erreur
        3XX -> Redirect
        4XX -> Client error
        5XX -> Server Error

        Additionnellement, jobup utilise le code 422 si la limite de recherche (2000) est atteinte
    """
    OK = '2'
    REDIRECT = '3'
    ERR_CLIENT = '4'
    ERR_PAGE_NOT_FOUND = '404'
    ERR_JOBUP_SEARCH_LIMIT = '422'
    ERR_SERVER = '5'
    ERR_GATEWAY = '502'
    #UNDEFINED est utilisé pour les valeurs inconnues
    #Comme celui-ci a une longueur de 0, il sera le dernier de la liste
    #et sera ainsi la valeur par défaut
    UNDEFINED = ''


class private:
    """ Contient les méthodes privées.
        Toutes les méthodes qui exécutent des requêtes sont privées,
        afin de forcer l'utilisation d'EJob comme format de données
    """

    @staticmethod
    def getQueryStatusFromString(code:str) -> HTTP_CODES:
        """Retourne un HTTP_CODE précisant le statut d'une requête à partir d'un code de statut

        Args:
            code (str): Le code, au format texte

        Returns:
            HTTP_CODES: Le HTTP_CODE correspondant
        """
        if type(code) is not str:
            code = str(code)

        listCodes = list(map(lambda enum: enum.value, list(HTTP_CODES)))
        #Les codes sont triés par longueur descendante
        #Plus une valeur dans HTTP_CODES est longue (522 > 5), plus celle-ci sera précise
        #Ainsi, en triant la liste on commence par les codes les plus descriptifs

        #key définit la valeur à utiliser pour le tri
        #ici, len sera appelé avec chaque valeur de notre liste, et la longueur sera utilisée
        #reverse=True veut dire que la liste sera triée par ordre descendant
        listCodes.sort(key=len, reverse=True)

        for statusCode in listCodes:
            if code.startswith(statusCode):
                return HTTP_CODES(statusCode)

        #Si le code n'est pas trouvé, on retourne UNDEFINED
        return HTTP_CODES.UNDEFINED


    @staticmethod
    def queryResultOrError(url:str) -> Union[requests.Response, HTTP_CODES]:
        """Query l'url et retourne la réponse, ou False si une erreur est survenue (code html autre que 2XX)

        Args:
            url (str): L'URL à query

        Returns:
            Union[requests.Response, HTTP_CODES]: La réponse, ou le type d'erreur
        """
        result = requests.get(url)
        code = private.getQueryStatusFromString(str(result.status_code))

        if code is HTTP_CODES.OK:
            return result
        else:
            return code


    @staticmethod
    def getJob(jobID: str) -> Union[object, HTTP_CODES]:
        """ Retourne les informations d'un poste
        Args:
                jobID (str): L'ID du job à rechercher
        Returns:
                Union[object, HTTP_CODES]: Les données du job
        """
        result = private.queryResultOrError(f"{API.JOB.value}{jobID}")
        if type(result) is requests.Response:
            return result.json()
        else:
            #@TODO Décider quoi faire lorsque le scraping d'un poste échoue
            EHelper.printError(f"Erreur lors de la récupération du job : {jobID}", str(result))
            return result

    @staticmethod
    def getLastJob() -> Union[object, HTTP_CODES]:
        """Retourne les informations du dernier job posté sur jobup, via la page de recherche

        Returns:
            Union[object, HTTP_CODES]: Les données du dernier job
        """
        idQuery = private.queryResultOrError(API.SEARCH_IT.value)
        if type(idQuery) is requests.Response:
            id = idQuery.json()['documents'][0]['job_id']
            #Pas besoin de faire d'error checking sur la valeur de retour de getJob, car getJob le fait déjà
            return private.getJob(id)

        EHelper.printError("Erreur lors de la récupération de l'ID du dernier poste via la recherche", str(idQuery))
        return idQuery
        

    @staticmethod
    def getCompany(companyID: str) -> Union[object, HTTP_CODES]:
        """Retourne les informations d'une entreprise sur jobup, via son ID

        Args:
            companyID (str): L'ID de l'entreprise

        Returns:
            Union[object, HTTP_CODES]: Les informations de l'entreprise
        """
        company = private.queryResultOrError(f"{API.COMPANY.value}{companyID}")
        if type(company) is requests.Response:
            return company.json()

        #@TODO Décider quoi faire si company n'est pas trouvé
        EHelper.printError(f"Erreur lors de la récupération de l'entreprise {companyID}", str(company))
        return company

    @staticmethod
    def getSearchPage(page:int, query = '', rows:int = 20) -> Union[object, HTTP_CODES]:
        """Retourne une page de la recherche

        Args:
            page (int): le numéro de page (commence à 1)
            query (str, optional): Le texte à rechercher. Defaults to ''.
            rows (int, optional): Le nombre de résultats à retourner par page. Defaults to 100.

        Returns:
            object: Le résultat de la recherche
        """
        queryString:str = f"{API.SEARCH_IT.value}&page={page}&rows={rows}"
        if(len(query) > 0):
            queryString += '&' + query

        result = private.queryResultOrError(queryString)
        if type(result) is requests.Response:
            return result.json()
            
        EHelper.printError(f"Erreur lors de la récupération de la page {page}", str(result))
        return result

    

class EScraper:
    """ Contient différentes méthodes publiques permettant de récupérer des EJob
        à partir de l'API Jobup
    """
    @staticmethod
    def getLastPostedJob() -> Union[EJob, HTTP_CODES]:
        """Retourne le poste le plus récent 

        Returns:
                Union[EJob, HTTP_CODES]: Le poste le plus récent, ou le code d'erreur
        """
        job = private.getLastJob()
        if type(job) is HTTP_CODES:
            return job
        else:
            return EHelper.MapObjectToNewType(job, EJob)

    @staticmethod
    def getJobFromID(id: str) -> Union[EJob, HTTP_CODES]:
        """Retourne le poste le plus récent 

        Returns:
                Union[EJob, HTTP_CODES]: Le poste le plus récent
        """
        job = private.getJob(id)
        if type(job) is HTTP_CODES:
            return job
        else:
            return EHelper.MapObjectToNewType(job, EJob)

    @staticmethod
    def getCompanyFromID(id:str) -> Union[ECompany, HTTP_CODES]:
        """Retourne l'entreprise avec l'ID spécifiée

        Args:
            id (str): L'ID de l'entreprise

        Returns:
            Union[ECompany, HTTP_CODES]: L'entreprise, en objet ECompany
        """
        company = private.getCompany(id)
        
        if type(company) is HTTP_CODES:
            return company
        else:
            return EHelper.MapObjectToNewType(company, ECompany)    

    
    @staticmethod
    def getAllAvailableJobIDsFromJobup() -> list:
        """Retourne l'ID de tous les postes actuellement jobup


        Returns:
            list: Une liste contenant l'ID de tous les postes sur jobup
        """
        currPage = 1
        result = []
        currPageIDs = []

        while True:
            EHelper.printInfo("Scraping page de recherche", str(currPage) + '/?')
            page = private.getSearchPage(currPage)
            if type(page) is HTTP_CODES:
                if page is HTTP_CODES.ERR_GATEWAY:
                #l'API renvoie une gateway error sur certaines requêtes
                #Cela ne veut pas dire qu'il n'y a plus de résultats
                #/!\ Généralement, une requête qui retourne une gateway error retournera toujours une gateway error/!\
                #@TODO Trouver un moyen de régler les gateway error
                    print('')
                    EHelper.printError(f"Gateway error page N°{page.value}, on attend 10 secondes avant de réessayer")
                    sleep(10)
                     #currPage ne sera pas incrémenté, ainsi on peut simplement passer
                     #à la boucle suivante pour réessayer de scraper la page actuelle
                    continue
                elif page is HTTP_CODES.ERR_JOBUP_SEARCH_LIMIT:
                    #La limite de recherche est atteinte, la recherche est finie
                    print('')
                    return result
                else:
                    print('')
                    #Erreur inconnue
                    EHelper.printError("Erreur inconnue lors du scraping de la page, abandon")
                    return result
            else:
                currPageIDs = list(map(lambda job: job['job_id'], page['documents']))
                result.append(currPageIDs)
                currPage += 1
                #La fonction va envoyer entre 20 et 100 requêtes, selon le nombre de lignes retournées
                #On attend 500ms entre chaque requête, afin d'éviter de surcharger le service
                sleep(0.5)

    @staticmethod
    def getAllNewJobs(lastJobID:str)-> list:
        """Retourne tous les jobs postés depuis le poste le plus récent en DB

        Args:
            lastJobID (str): l'ID du job le plus récent en DB

        Returns:
            list: Retourne une liste d'EJob
        """
        #La recherche étant triée par ordre chronologique, on utilise celle-ci
        # pour trouver les jobs les plus récents
        pageNumber = 1
        result = []
        tmpJob:EJob
        tmpJobID:str = ''

        while True:
            currPage = private.getSearchPage(pageNumber)
            if type(currPage) is HTTP_CODES:
                EHelper.printError("Erreur lors du scraping de la page " + str(pageNumber), currPage.name)
                return result
            progress = 0
            total = len(currPage['documents'])
            for job in currPage['documents']:
                tmpJobID = job['job_id']
                if tmpJobID == lastJobID:
                    print('')
                    return result
                
                tmpJob = private.getJob(tmpJobID)
                #@TODO Error checking network requests
                if type(tmpJob) is HTTP_CODES:
                    continue
                result.append(tmpJob)

                EHelper.printInfo("Job récupéré, pause de 0.5s", f"{progress}/{total}")
                sleep(0.5)

            pageNumber += 1









            


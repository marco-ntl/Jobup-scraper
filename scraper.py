#
#   SCRAPING JOBUP
#
#   Ce fichier contient tout ce qui touche au scraping
#   Utilisation: from EScraper import EScraper
import json
import requests
from EJob import EJob

class API:
    BASE = "https://www.jobup.ch/api/v1/public"
    SEARCH = BASE + '/search'
    JOB = SEARCH + '/job/'

class private:
    """ Contient les méthodes privées.
        Toutes les méthodes qui exécutent des requêtes sont privées,
        afin de forcer l'utilisation d'EJob

    """
    @staticmethod
    def getJobRaw(jobID: str = ""):
        """ Retourne les informations d'un poste au format brut (JSON)

        Args:
                jobID (str): L'ID du job à rechercher

        Returns:
                str: Les données du job, en JSON
        """

        return requests.get(API.JOB + jobID).text

    @staticmethod
    def getLastJobRaw():
        """Retourne les informations du dernier job posté sur jobup, via la page de recherche

        Returns:
            str: Les données du dernier job, au format JSON
        """
        return requests.get(API.SEARCH).text
        
class EScraper:
    """ Contient différentes méthodes publiques permettant de récupérer des EJob
        à partir de l'API Jobup
    """
    _private = private()
    _API = API()

    @staticmethod
    def getLastPostedJob():
        """Retourne le poste le plus récent 

        Returns:
                str: Le poste le plus récent
        """
        return EJob.fromJSONVar(private.getLastJobRaw())



    



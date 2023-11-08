#   SCRAPING JOBUP
#
#   Ce fichier contient l'objet ECompany,
#   qui représente une entreprise sur jobup
#   Utilisation: from ECompany import ECompany

class private:
    """Contient les méthodes et variables privées
    """
    #Ce dictionnaire mappe les lignes de l'objet JSON retourné par jobup avec les attributs d'une entreprise
    #Utilisation : rowToCompMap[key](val)
    rowToCompMap: dict = {
    'portrait_descriptions_search': lambda val: {
        'description_de': val['de'],
        'description_fr': val['fr'],
        'description_en': val['en'],
    },
    'social_urls': lambda val: private.MapSocialURLs(val),
    'child_ids': lambda val: None,
    'portrait': lambda val: None,
    'portrait_urls': lambda val: None,
    'portrait_descriptions': lambda val: None,
    'images': lambda val: None,
    'videos': lambda val: None,
    'metadata': lambda val: None,
    'badges': lambda val: None,
    'benefits': lambda val: None,
    'addresses': lambda val: {'address_id': private.MapAddress(val)},
    'contact_address': lambda val: { 'contact_address_id': private.MapAddress(val)},
    'ratings': lambda val: {
        "ratings_total": val['total'],
        "ratings_average": val['average']
        }
    }

    @staticmethod
    def MapAddress(val:dict) -> str:
        from EAddress import EAddress
        from EHelper import EHelper
        from EDatabase import EDatabase
        """Mappe une addresse, l'ajoute à la DB puis retourne son id 

        Args:
            val (dict): L'addresse à mapper

        Returns:
            str: L'ID de la nouvelle addresse
        """
        #Jobup contient parfois plusieurs addresses
        #On ne récupère que la première pour simplifier la DB
        if(type(val) is list):
            val = val[0]
        address:EAddress = EAddress
        for innerKey, innerVal in val.items():
            EHelper.MapKeyValueToObject(innerKey, innerVal, address)

        return EDatabase.insertAddress(address)

    @staticmethod
    def MapSocialURLs(vals:list) -> dict:
        """Mappe une liste de réseaux sociaux au format de jobup aux attributs d'ECompany

        Args:
            vals (list): La liste de réseaux sociaux

        Returns:
            dict: Dictionnaire au format ['Nom de la colonne' -> url]
        """
        if(len(vals) == 0):
            return

        result:dict = {}
        for item in vals:
            platform = item['type']
            url = item['url']
            result['social_' + platform] = url
        return result

class ECompany:
    """Représente une entreprise sur jobup
    """
    id:int = -1
    description_de:str = ''
    description_fr:str = ''
    description_en:str = ''
    slug:str = ''
    is_visible:str = ''
    datapool_id:str = ''
    name:str = ''
    last_modified:str = ''
    industry:str = ''
    founding_year:str = ''
    url:str = ''
    address_id:str = ''
    contact_address_id:str = ''
    portrait_urls:str = ''
    portrait_descriptions:str = ''
    phone:str = ''
    ratings_total:str = ''
    ratings_average:str = ''
    social_facebook:str = ''
    social_twitter:str = ''
    social_linkedin:str = ''
    social_youtube:str = ''
    social_instagram:str = ''
    social_xing:str = ''
    social_viadeo:str = ''
    @staticmethod
    def getMap()->dict:
        """Retourne le dictionnaire de mapping

        Returns:
            dict: Le dictionnaire de mapping
        """
        return private.rowToCompMap
#   SCRAPING JOBUP
#
#   Ce fichier contient l'objet EAddress,
#   qui représente l'objet address de jobup
#   Utilisation: from EAddress import EAddress
class private:
    """Contient les variables et fonctions privées
    """
    rowToAddressMap: dict = {
        'city_translations': lambda val:{
            'city_de': val['de'],
            'city_en': val['en'],
            'city_fr': val['fr']
        },
        'coordinates': lambda val: None if val is None else {'longitude': val['lon'], 'latitude': val['lat']},
    }

class EAddress:
    """Représente l'objet addresse de jobup
    """
    street1:str = ''
    street2:str = ''
    city:str = ''
    city_de:str = ''
    city_en:str = ''
    city_fr:str = ''
    zip_code:str = ''
    country_code:str = ''
    tel_1:str = ''
    tel_2:str = ''
    fax:str = ''
    firstname:str = ''
    lastname:str = ''
    email:str = ''
    latitude:str = ''
    longitude:str = ''

    @staticmethod
    def getMap()->dict:
        """Retourne le dictionnaire de mapping

        Returns:
            dict: Le dictionnaire de mapping
        """
        return private.rowToAddressMap
#
#   SCRAPING JOBUP
#
#   Ce fichier contient l'objet EJob, représentant un job sur jobup
#   Utilisation: from EJob import EJob



class private:
    """ Contient les méthodes privées.
    """
    #Ce dictionnaire mappe les lignes de l'objet JSON retourné par jobup avec les attributs d'un job
    #Utilisation : rowToCompMap[key](val)
    rowToJobMap: dict = {
    'detail_fr': lambda val: val['href'],
    'detail_en': lambda val: val['href'],
    'detail_de': lambda val: val['href'],
    'coordinates': lambda val: {'coordinatesLon': val['lon'], 'coordinatesLat': val['lat']},
    'contact_person': lambda val: private.MapContactPerson(val)
    }

    @staticmethod
    def MapContactPerson(val:dict) -> dict:
        """Mappe le champ contact_person aux champs d'EJob


        Args:
            val (dict): Les données du champ contact_person

        Returns:
            dict: Un dictionnaire avec des clefs correspondant aux champs d'EJob
        """
        if type(val) is list:
            return {}
        
        result:dict = {        
            'contact_firstName': val.get("firstName", ''),
            'contact_lastName': val.get("lastName", ''),
            'contact_gender': val.get("gender", '')
        }
        adresses:dict = {}
        if len(val["address"]) > 0:
            adresses = {
                'contact_city': val["address"].get('city', ''),
                'contact_street': val["address"].get('street', ''),
                'contact_countryCode': val["address"].get('countryCode', ''),
                'contact_postalCode': val["address"].get('postalCode', ''),
                'contact_lat': val["address"].get('latitude', ''),
                'contact_lon': val["address"].get('longitude', '')
            }

        #On retourne le dictionnaire crée par la fusion de result et addresses
        return result.update(adresses)

class EJob:
    """Représente un Job
    """
    # /!\ Pour certaines entreprises (tel que Randstadt), l'id  /!\
    # /!\ est un hash hexadécimal de taille arbitraire          /!\
    job_id: str = ""
    detail_de:str = ""
    detail_fr:str = ""
    detail_en:str = ""
    title:str = ""
    raw_template:str = ""
    slug:str = ""
    company_slug:str = ""
    application_method:str = ""
    job_source_type:str = ""
    last_online_date:str = ""
    datapool_id: int = -1
    company_name:str = ""
    company_id: int = -1
    industry_id: int = -1
    publication_date:str = ""
    initial_publication_date:str = ""
    place:str = ""
    street:str = ""
    external_url:str = ""
    application_url:str = ""
    zipcode:str = ""
    source_platform_id:str = ""
    synonym:str = ""
    template_profession:str = ""
    template_text:str = ""
    template_lead_text:str = ""
    template_contact_adress:str = ""
    offer_id:str = ""
    is_active: int = -1
    is_responsive: int = -1
    is_paid: int = -1
    coordinatesLon:str = ""
    coordinatesLat:str = ""
    source_hostname:str = ""
    headhunter_application_allowed:str = ""
    contact_city:str = ""
    contact_street:str = ""
    contact_countryCode:str = ""
    contact_postalCode:str = ""
    contact_lat:str = ""
    contact_lon:str = ""
    contact_firstName:str = ""
    contact_lastName:str = ""
    contact_gender:str = ""
    is_highlighted:str = ""

    @staticmethod
    def getMap()->dict:
        """Retourne le dictionnaire de mapping

        Returns:
            dict: Le dictionnaire de mapping
        """
        return private.rowToJobMap
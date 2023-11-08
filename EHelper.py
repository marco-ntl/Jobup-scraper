#   SCRAPING JOBUP
#
#   Ce fichier contient l'objet EHelper,
#   qui contient différentes fonctions utiles au programme
import json
import inspect

class EHelper:

    @staticmethod
    def printInfo(msg:str, progress:str = '', endChars:str='\r'):
        """Print un message d'information dans la console

        Args:
            msg (str): Le message à printer
            progress (str, Optional): Un string indiquant l'état d'avancement (Ex. '90%', '5/15', etc...)
            endChars (str, Optional): Le(s) caractère(s) à utiliser en fin de ligne. \r par défaut
        """
        result = msg
        if len(progress) > 0:
            #1 tabulation = 4 espaces
            #Pour garder une taille consistante, on regarde la longuer de progress
            #en tabulations, et on enlève une tabulation pour chaque 4 caractères
            #formule : maxTabs - (txtSize / tabSize)
            nbTabs = (1 - int(len(progress) / 4))
            if(nbTabs < 0):
                nbTabs = 0

            spacing = '\t' * nbTabs
            result = f"[{progress}] {spacing}{result}"
        if endChars == '\r':
            #Si la ligne finit par \r, il faut padder la fin du string avec des espaces
            #afin d'enlever les caractères qui pourraient rester si le string précédent est plus long
            result = result + (' ' * 120)
        print(result, end=endChars)

    @staticmethod
    def printError(msg:str, code:str = ''):
        """Print un message d'erreur dans la console, ainsi qu'un code d'erreur si précisé

        Args:
            msg (str): Le message à afficher
            code (str, optional): (Optionnel)Le code d'erreur à afficher. Vide par défaut.
        """
        #Retourne des informations sur la fonction qui print l'erreur
        callerInfo = inspect.stack()[1]
        print(f"{callerInfo.function}:{callerInfo.lineno}\t{msg}")
        if(len(code) > 0):
            print("Code d'erreur :\t" + str(code))

    @staticmethod
    def ObjHasMethod(obj:object, name:str)->bool:
        """Retourne True si object contient une méthode avec le nom spécifié
        Args:
            obj (object): L'objet dans lequel rechercher
            name (str): Le nom de la méthode
        Returns:
            bool: Retourne True si l'objet contient la méthode spécifiée
        """
        return (callable(getattr(obj, name, None)) is True)

    @staticmethod
    def MapKeyValueToObject(key: any, val: any, obj: object) -> None:
        """ Modifie un EJob à partir d'un key-value pair (Ex. id => 12)
        Args:
            key (any): L'index de la valeur
            val (any): La valeur
            obj (object): L'objet à modifier
        """
        if EHelper.ObjHasMethod(obj, 'getMap'):
            map = obj.getMap()
        else:
            #On initialise map en tant que dictionnaire vide afin que 
            # if(key in map) ne retourne pas d'erreur
            map:dict = {}
        if key in map:
                tmp = map[key](val)
                if(type(tmp) is dict):
                    for innerKey, innerVal in tmp.items():
                        setattr(obj, innerKey, innerVal)
                elif tmp is not None:
                    setattr(obj, key, tmp)
        # https://docs.python.org/3/library/json.html#json-to-py-table
        # JSON.loads transforme les objets en dictionnaire, et les arrays en listes
        # Tous les champs qui nous intéressent sont nommés (pas d'array de valeurs)
        # Ainsi, les données recherchées se trouveront forcément dans un dictionnaire
        elif type(val) is dict:
            # Si val est une collection, on la traverse récursivement avec MapKeyValueToObject
            for innerKey, innerVal in val.items():
                EHelper.MapKeyValueToObject(innerKey, innerVal, obj)
        # Si val est une liste, on va chercher les dictionnaires qu'elle contient
        # afin de les traverser récursivement
        elif type(val) is list:
            for item in val:
                if type(item) is list or type(item) is dict:
                    EHelper.MapKeyValueToObject('noKey', item, obj)
        # Sinon, si un attribut correspondant à key (le nom de la colonne) existe
        # On lui donne la valeur correspondante.
        # Si l'attribut n'est pas trouvé, getattr renverra False
        elif getattr(obj, key, False) is not False:
            setattr(obj, key, val)

    @staticmethod
    def MapObjectToNewType(JSONObj:object, objectType:type) -> object:
        """Crée un objet à partir du résultat brut (au format JSON) d'une query
        Args:
            JSONObj (object): L'objet à mapper aux nouveau type
            objectType (type): Le nouveau type voulu

        Returns:
            object: Le nouvel objet, au type objectType
        """
        if type(objectType) is not type:
            objectType = type(objectType)
        result: objectType = objectType()

        if 'errors' in JSONObj.keys():
            return None

        for key, val in JSONObj.items():
            EHelper.MapKeyValueToObject(key, val, result)

        return result

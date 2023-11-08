#   SCRAPING JOBUP
#
#   Ce fichier contient l'objet EDatabase,
#   qui gère toute la partie base de données
#   Utilisation: from EDatabase import EDatabase


import sqlite3
from EJob import EJob
from os.path import isfile
from EAddress import EAddress
from ECompany import ECompany

#Le nom des différentes tables
JOBS = 'jobs'
COMPANY = 'company'
ADDRESS = "address"
DB_NAME:str = 'jobup.db'
DEFAULT_ID_COL = '_id_'

class private:
    """Python n'ayant pas de classes privées, cette classe est utilisée à la place
    """
    
    @staticmethod
    def CreateTableFromObject(c:sqlite3.Connection, obj:type, tableName:str) -> None:
        """Crée une table à partir d'un objet ou de son type

        Args:
            c (sqlite3.Connection): La connexion à la table
            obj (type): La définition de l'objet (EJob, EScraper, etc...)
            tableName (str): Le nom de la table
            pkColName (str): Le nom de la colonne qui sera la primary key
            idColType (str): Le type de la colonne primary key (par défaut : INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE)

        """
        #Cette fonction travaille directement avec le type, donc si l'objet passé n'est pas
        #de type "type", on le réassigne à son type via la fonction type()
        if type(obj) is not type:
            obj = type(obj)

        colsAndTypes:dict = {}

        #Procédure :
        #1. On extrait tous les attributs du type
        #2. Pour chaque attribut, on définit le type (au format SQLite) de celui-ci
        #3. On utilise la liste d'attributs et de types pour générer la structure de la table
        for key in vars(obj):
            #On vérifie que la clef ne soit ni un attribut par défaut, ni une fonction
            if key.startswith('__') or callable(getattr(obj,key, False)) is True:
                continue
            elif type(getattr(EJob, key, False)) is int:
                colsAndTypes[key] = "INTEGER"
            #Les champs sont représentés comme des strings par défaut
            else:
                colsAndTypes[key] = "TEXT"

        #On set la PK après tous les autres, car le champ peut ne pas être
        #dans obj. De plus, cela évite tous risques que celle-ci soit affectée
        #par les autres champs
        colsAndTypes[DEFAULT_ID_COL] = 'INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE'
        formattedCols:str = ''
        #On formatte les colonnes au format SQLite
        for key, val in colsAndTypes.items():
            formattedCols += f'"{key}"  {val},'
        #On retire la dernière virgule
        formattedCols = formattedCols[:-1]
        c.execute(f'''CREATE TABLE "{tableName}" ({formattedCols});''')
        c.commit()
        
        

    @staticmethod
    def createTables() -> sqlite3.Connection:
        """Crée le fichier de base de données (si requis), et crée les tables dans celui-ci
        Returns:
            sqlite3.Connection: La connexion à la nouvelle DB
        """
        if not isfile(DB_NAME):
            c = sqlite3.connect(DB_NAME)

        private.CreateTableFromObject(c, EAddress, ADDRESS)
        private.CreateTableFromObject(c, ECompany, COMPANY)
        private.CreateTableFromObject(c, EJob, JOBS)
        return c

    @staticmethod
    def valAlreadyInDB(conn, val:str, table:str, col:str) -> bool:
        """Retourne True si une colonne contenant val existe déjà dans la table spécifiée

        Args:
            val (str): La valeur à vérifier
            table (str): Le nom de la table
            col (str): Le nom de la colonne

        Returns:
            bool: Est-ce que la valeur est déjà présente dans la colonne spécifiée
        """
        queryResult = conn.execute(f"SELECT {col} FROM {table} WHERE {col} = '{val}'").fetchone()
        return (queryResult is not None)

    @staticmethod
    def insertObj(conn:sqlite3.Connection, obj:object, table:str) -> str:
        """Insère un objet en base de données, et retourne son id

        Args:
            conn (sqlite3.Connection): La connexion à utiliser
            obj (object): L'objet à mettre en DB
            table (str): Le nom de la table

        Returns:
            str: L'ID du nouvel objet
        """
        #On récupère la liste de noms de colonne, et on ajoute des quotes ("") autour de chaque nom de colonne
        #pour la query
        objData:dict = {}
        for key, val in obj.__dict__.items():
            if key.startswith('__') is False and callable(getattr(obj, key, False)) is False:
                objData[key] = val

        cols = map(lambda val: f'"{val}"', objData.keys())
        #La documentation sqlite spécifie que les strings doivent être échappés avec des apostrophes
        #Ainsi, on entoure chaque valeur d'apostrophes.
        #On double aussi tous les apostrophes, afin de les échapper
        #https://www.sqlite.org/lang_expr.html
        data = map(lambda val: "'" + str(val).replace("'", "''") + "'" ,objData.values())
        #On génère la liste de colonnes et de valeurs séparées par des virgules via string.join
        query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(data)});"
        c = conn.cursor()
        c.execute(query)
        return c.lastrowid
    
    @staticmethod
    def selectOne(conn:sqlite3.Connection, cols:list, table:str, conditions:str = '', sortCol:str = ''):
        """Éxécute un SELECT avec les paramètres spécifiés, et retourne la première ligne

        Args:
            conn (sqlite3.Connection): La connexion
            cols (list): Une liste contenant les différentes colonnes à SELECT (ou un str pour une seule colonne)
            table (str): la table sur laquelle appliquer la requête
            condition (str, optional): Les conditions de la requête (tout ce qui va après WHERE)
            sortCol (str, optional): La colonne et l'orientation à utiliser pour le sort (Ex. 'id ASC')

        Returns:
           tuple : La ligne retournée par fetchone
        """
        return private.select(conn, cols, table, conditions, sortCol).fetchone()


    @staticmethod
    def selectAll(conn:sqlite3.Connection, cols:list, table:str, conditions:str = '', sortCol:str = ''):
        """Éxécute un SELECT avec les paramètres spécifiés, et retourne la première ligne

        Args:
            conn (sqlite3.Connection): La connexion
            cols (list): Une liste contenant les différentes colonnes à SELECT (ou un str pour une seule colonne)
            table (str): la table sur laquelle appliquer la requête
            condition (str, optional): Les conditions de la requête (tout ce qui va après WHERE)
            sortCol (str, optional): La colonne et l'orientation à utiliser pour le sort (Ex. 'id ASC')

        Returns:
           tuple : La ligne retournée par fetchone
        """
        return private.select(conn, cols, table, conditions, sortCol).fetchall()


    @staticmethod
    def delete(conn:sqlite3.Connection, table:str, cond:str = ''):
        """Exécute un DELETE FROM avec les paramètres spécifiés

        Args:
            conn (sqlite3.Connection): La connexion
            table (str): La table
            cond (str, optional): La condition. Defaults to ''.
        """
        query:str = "DELETE FROM " + table
        if len(cond) > 0:
            query = query + " WHERE " + cond
        conn.execute(query)
    

    @staticmethod
    def update(conn:sqlite3.Connection, table:str, vals:dict, cond:str = ''):
        """Exécute un UPDATE avec les paramètres spécifiés

        Args:
            conn (sqlite3.Connection): La connexion
            table (str): La table
            vals (dict): Un dictionnaire avec les colonnes et valeurs
            cond (str, optional): La condition. Defaults to ''.
        """
        query:str = "UPDATE " + table 

        for col, val in vals.items():
            query = f"{query} SET '{col}' = '{val}',"

        #On enlève la dernière virgule
        query = query[:-1]
        if len(cond) > 0:
            query = query + " WHERE " + cond
        conn.execute(query)

    @staticmethod
    def select(conn:sqlite3.Connection, cols:list, table:str, conditions:str = '', sortCol:str = ''):
        """Éxécute un SELECT avec les paramètres spécifiés, et retourne la réponse

        Args:
            conn (sqlite3.Connection): La connexion
            cols (list): Une liste contenant les différentes colonnes à SELECT (ou un str pour une seule colonne)
            table (str): la table sur laquelle appliquer la requête
            condition (str, optional): Les conditions de la requête (tout ce qui va après WHERE)
            sortCol (str, optional): La colonne et l'orientation à utiliser pour le sort (Ex. 'id ASC')

        Returns:
           object: la réponse
        """
        columnsStr:str = ''
        if type(cols) is list:
            #On sépare les colonnes par une virgule, et on enlève la dernière virgule avec une slice [:-1]
            columnsStr = ','.join(cols)[:-1]
        else:
            columnsStr = cols

        conditionsStr = ''
        if type(conditions) is str and len(conditions) > 0:
            conditionsStr = 'WHERE ' + conditions

        sortStr = ''
        if type(sortCol) is str and len(sortCol) > 0:
            sortStr = 'WHERE ' + sortCol


    
        return conn.execute(f"SELECT {columnsStr} FROM {table} {conditionsStr} {sortStr}")


_private = private()
_conn:sqlite3.Connection = None

class EDatabase:

    @staticmethod
    def getConn():
        """Crée une connexion si aucune n'existe, ou retourne la connexion existante

        Returns:
            sqlite3.Connection: La connexion
        """
        global _conn

        if(type(_conn) is not sqlite3.Connection):
            if not isfile(DB_NAME):
                _conn = private.createTables()
            else:
                _conn = sqlite3.connect(DB_NAME)
        
        return _conn

    @staticmethod
    def insertJob(job:EJob) -> str:
        """Insère un job dans la base de données

        Args:
            job (EJob): Le job à insérer

        Returns:
            str: l'id du nouveau job
        """
        #On vérifie que le job n'existe pas déjà
        if(EDatabase.jobExists(job.job_id)):
            return

        return private.insertObj(EDatabase.getConn(), job, JOBS)
        
    @staticmethod
    def insertCompany(company:ECompany) -> str:
        """Insère une entreprise dans la base de données

        Args:
            company (ECompany): L'entreprise à insérer
        
        Returns:
            str: l'id de la nouvelle entreprise
        """
        #On vérifie que l'entreprise n'existe pas déjà
        if(EDatabase.companyExists(company.id)):
            return
        
        return private.insertObj(EDatabase.getConn(), company, COMPANY)

    @staticmethod
    def insertAddress(address:EAddress) -> str:
        #insertObj récupère tous les attributs afin de les insérer en base de données
        #on veut cependant que l'ID ne soit pas spécifiée dans la requête
        #car celui-ci est de type autoincrement
        if getattr(address, DEFAULT_ID_COL, False) is not False:
            delattr(address, DEFAULT_ID_COL)
        return private.insertObj(EDatabase.getConn(), address, ADDRESS)

    @staticmethod
    def saveChanges():
        """Sauvegarde l'état de la base de données
        """
        EDatabase.getConn().commit()

    @staticmethod
    def jobExists(id:str) -> bool:
        """Vérifie si un job existe à partir de son ID

        Args:
            id (int): L'id du Job

        Returns:
            bool: Est-ce que le job existe déjà
        """
        return private.valAlreadyInDB(EDatabase.getConn(), id, JOBS, DEFAULT_ID_COL)
    
    @staticmethod
    def companyExists(id:int) -> bool:
        """Vérifie si une entreprise existe à partir de son id

        Args:
            id (int): l'id de l'entreprise

        Returns:
            bool: Est-ce que l'entreprise existe déjà
        """
        return private.valAlreadyInDB(EDatabase.getConn(), id, COMPANY, DEFAULT_ID_COL)
    
    @staticmethod
    def countJobs() -> int:
        """Retourne le nombre de jobs en base de données

        Returns:
            int: Le nombre d'entrées dans la table "jobs"
        """
        queryResult = private.selectOne(EDatabase.getConn(), f'COUNT({DEFAULT_ID_COL})', JOBS)
        return int(queryResult[0])

    @staticmethod
    def getAllMissingCompaniesID() -> list:
        """Retourne l'ID (jobup) de toutes les entreprises qui sont dans jobs mais pas dans companies

        Returns:
            list: Toutes les entreprises dont l'ID est trouvable dans job mais pas dans company
        """
        queryResult = private.selectAll(EDatabase.getConn(), 'DISTINCT company_id', JOBS, f"company_id NOT IN (SELECT id FROM {COMPANY}) AND length(company_id) > 0")
        return queryResult

    @staticmethod
    def updateJobCompanyID(jobID:str, newID:str):
        """Update la company_id d'un job

        Args:
            jobID (str): L'ID du job à modifier
            newID (str): La nouvelle ID
        """        
        private.update(EDatabase.getConn(), JOBS, {"company_id": newID}, 'company_id  = ' + str(jobID))
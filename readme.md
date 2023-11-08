# Scrapers - Jobup.ch
## Dependencies
### Software
- **[Python](https://www.python.org/downloads/)**
  - Python version 3.7 minimum
### Python
- **[Requests](https://pypi.org/project/requests/)**
  - *pip install requests*
  - requests est utilisé pour faciliter les requêtes à l'API de jobup
## Usage
### main.py
Pour démarrer le scraper, simplement exécuter main.py.
Si le fichier jobup.db n'existe pas (tel que lors d'un premier lancement), le script ira récolter tous les postes dans le domaine IT. Il créera ensuite la base de données, et y ajoutera tous les postes.

Si la base de données existe, le script récupérera tous les jobs postés depuis son dernier lancement.

Avant la fin de chaque éxécution, le script ira récupérer les informations de toute les entreprises qu'il ne trouve pas dans la DB


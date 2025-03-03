# Développez une architecture back-end sécurisée avec Python et SQL

## Français

### Introducion

Une application CRM en ligne de commandes

# Installation

Pré-requis:

- Python >= 3.12
- Git 2.x (uniquement pour cloner le repo)

```sh
git clone https://github.com/GromPras/oc-projet_12.git
```

`Ou téléchargez le fichier ZIP depuis https://github.com/GromPras/oc-projet_12/archive/refs/heads/main.zip`

Créez un environement virtuel à l'intérieur du dossier cloné:

```sh
cd oc-projet_12
python3 -m venv {/path/to/virtual/environment}
```

Sur Windows, appelez la commande venv comme suit :

```sh
c:\>c:\Python3\python -m venv c:\path\to\myenv
```

Activer l'environement virtuel :

```sh
source {/path/to/virtual/environment}/bin/activate
```

Sur Windows, appelez la commande venv comme suit :

```sh
C:\> <venv>\Scripts\activate.bat
```

Installez les dépendances du projet à l'aide de votre gestionnaire favori:

```sh
uv sync
```

Si vous avez un problème avec la création de l'environnement consultez la documentation : `https://docs.python.org/fr/3/library/venv.html#creating-virtual-environments`

### Post Installation

#### Pour lancer le programme, exécutez les commandes suivantes :
Préparer la base de données et importer les données de test
```sh
cd api/
python3 flask db upgrade
sqlite3 instance/app.db < db.txt
```

Lancer le server flask
```sh
python3 flask run
```

Utilisez les commandes du CRM
```sh
python3 -m cli.main --help
```

### Logins pour tests
Admin user: testadmin@test.com
Sales user: testsales@test.com
Support user: testsupport@test.com

Password: test

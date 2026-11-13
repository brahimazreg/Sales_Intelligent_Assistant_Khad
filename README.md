

<div align="center">

<img src="assets/sales-assistant-banner.png" alt="Sales Intelligent Assistant Khady" width="100%">

# Sales Intelligent Assistant Khady

### Interroger ses données commerciales en langage naturel grâce à l'IA

</div>

# 🤖 Sales Intelligent Assistant Khady

**Assistant intelligent d'analyse commerciale utilisant l'intelligence artificielle, le RAG et le langage naturel pour interroger une base de données SQL Server.**


---

## 📌 Présentation du projet

**Sales Intelligent Assistant Khady** est une application intelligente conçue pour faciliter l'exploitation des données commerciales à travers une interface conversationnelle.

L'objectif est de permettre aux utilisateurs d'interroger une base de données commerciale en langage naturel, sans avoir besoin de maîtriser le SQL.

L'utilisateur pose une question en français et l'assistant :

1. Comprend la question.
2. Recherche les informations pertinentes dans le schéma de la base de données grâce au RAG.
3. Génère automatiquement une requête SQL avec un modèle de langage.
4. Vérifie la requête avant son exécution.
5. Exécute la requête sur SQL Server.
6. Interprète les résultats et formule une réponse en français.

L'application dispose également d'une interface web développée avec Streamlit.

## 🎯 Objectifs

- Simplifier l'accès aux données commerciales.
- Interroger une base de données en langage naturel.
- Automatiser la génération de requêtes SQL.
- Exploiter les capacités des modèles de langage locaux.
- Faciliter l'analyse des clients, produits, commandes et fournisseurs.
- Rendre les données plus accessibles aux utilisateurs non techniques.

## 🏗️ Architecture du projet

Le projet repose sur une architecture combinant RAG, LLM et SQL Server.

```text
                 UTILISATEUR
                      |
                      v
             INTERFACE STREAMLIT
                      |
                      v
             QUESTION EN FRANÇAIS
                      |
                      v
             RAG - CHROMADB
                      |
             Recherche du schéma
                      |
                      v
             SQL GENERATOR
                 Qwen3:8b
                      |
                      v
              SQL VALIDATOR
                      |
                      v
              SQL EXECUTOR
                      |
                      v
                SQL SERVER
                      |
                 Résultats
                      |
                      v
              Qwen3:8b
             Interprétation
                      |
                      v
             RÉPONSE EN FRANÇAIS
```

## 🛠️ Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Langage principal |
| Streamlit | Interface utilisateur |
| Ollama | Exécution locale des modèles IA |
| Qwen3:8b | Génération SQL et réponses |
| Nomic Embed Text | Génération des embeddings |
| ChromaDB | Base vectorielle pour le RAG |
| SQL Server | Base de données commerciale |
| PyODBC | Connexion à SQL Server |
| SQLAlchemy | Outils de connexion et de gestion SQL |
| Pandas | Manipulation des données |
| Plotly | Visualisations |

## 📂 Structure du projet

```text
Sales_Intelligent_Assistant_Khady/
│
├── config/
│
├── data/
│   └── chroma_db/
│
├── database/
│   ├── schema.json
│   └── business_schema.json
│
├── llm/
│   ├── sql_generator.py
│   └── sql_validator.py
│
├── rag/
│   ├── business_schema_generator.py
│   ├── document_builder.py
│   ├── embedding_manager.py
│   ├── chroma_store.py
│   └── retriever.py
│
├── services/
│   ├── schema_database.py
│   ├── sql_executor.py
│   └── query_pipeline.py
│
├── tests/
│
├── Utils/
│
├── app.py
├── main.py
├── .env
├── .gitignore
└── README.md
```

## ⚙️ Prérequis

Avant de démarrer le projet, il faut disposer de :

- Python 3.11 ou version compatible.
- SQL Server.
- Microsoft ODBC Driver 17 for SQL Server.
- Ollama installé et opérationnel.
- Une base de données commerciale accessible.
- Git.

### Modèles Ollama

Les deux modèles utilisés sont :

**Modèle de langage :**

```powershell
ollama pull qwen3:8b
```

**Modèle d'embeddings :**

```powershell
ollama pull nomic-embed-text:latest
```

Vérifier leur installation :

```powershell
ollama list
```

## 🚀 Installation

### 1. Cloner le dépôt

```powershell
git clone https://github.com/brahimazreg/Sales_Intelligent_Assistant_Khad.git
```

Accéder au projet :

```powershell
cd Sales_Intelligent_Assistant_Khad
```

### 2. Créer un environnement virtuel

```powershell
python -m venv venv
```

Activer l'environnement :

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
pip install streamlit pandas plotly chromadb pyodbc sqlalchemy python-dotenv
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet.

Exemple de configuration :

```env
OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_LLM_MODEL=qwen3:8b
OLLAMA_EMBED_MODEL=nomic-embed-text:latest

CHROMA_PATH=./data/chroma_db
CHROMA_COLLECTION=sales_business_schema

SQL_SERVER_CONNECTION_STRING=DRIVER={ODBC Driver 17 for SQL Server};SERVER=VOTRE_SERVEUR;DATABASE=VOTRE_BASE;Trusted_Connection=yes;TrustServerCertificate=yes;

RAG_TOP_K=6
```

**Important :** adapter les paramètres SQL Server à votre environnement. Ne jamais publier de mots de passe, identifiants ou informations confidentielles dans le dépôt GitHub.

### 5. Vérifier Ollama

Démarrer Ollama et vérifier que son API est accessible :

```powershell
ollama list
```

L'API locale est normalement disponible à :

```text
http://localhost:11434
```

## ▶️ Lancement de l'application

Une fois la configuration terminée, lancer l'application avec :

```powershell
streamlit run app.py
```

Streamlit ouvre l'application dans le navigateur.

Il est également possible de lancer le pipeline conversationnel directement depuis le terminal :

```powershell
python -m services.query_pipeline
```

## 💬 Exemples de questions

L'utilisateur peut poser des questions commerciales en français.

**Clients**
- Quels sont les clients enregistrés dans notre base ?
- Quels sont les 5 clients qui ont passé le plus de commandes ?
- Combien de clients avons-nous par région ?

**Produits**
- Quels produits avons-nous en stock ?
- Quels produits ont un stock inférieur au seuil de réapprovisionnement ?
- Quels sont les produits les plus chers ?

**Commandes**
- Combien de commandes avons-nous enregistrées ?
- Quel est le nombre de commandes par statut ?

**Fournisseurs**
- Quels sont les fournisseurs enregistrés dans notre base ?
- Quels fournisseurs sont situés en Belgique ?

## 🔐 Sécurité

Le projet intègre un validateur SQL afin de contrôler les requêtes générées avant leur exécution.

Les principales précautions sont :

- Autorisation des requêtes de lecture uniquement.
- Refus de plusieurs instructions SQL dans une même requête.
- Contrôle de certains mots-clés dangereux.
- Validation avant l'accès à SQL Server.

Pour une utilisation en production, il est recommandé d'utiliser un compte SQL Server disposant uniquement des permissions de lecture nécessaires.

## ⚠️ Limitations actuelles

- Les modèles Ollama fonctionnent localement et nécessitent des ressources matérielles suffisantes.
- La qualité des réponses dépend de la qualité des requêtes SQL générées.
- Le validateur SQL constitue une première protection et ne remplace pas les permissions de sécurité SQL Server.
- L'historique conversationnel Streamlit est conservé en mémoire de session et n'est pas encore persistant.
- Les données et la structure de la base doivent être correctement configurées avant utilisation.

## 🔮 Améliorations futures

- Persistance de l'historique des conversations.
- Amélioration de la validation et de la génération SQL.
- Ajout de graphiques et d'indicateurs commerciaux.
- Amélioration de l'expérience utilisateur.
- Gestion avancée des erreurs et des requêtes complexes.
- Déploiement de l'application sur un serveur.

## 👨‍💻 Auteur

**Brahim Azreg**

GitHub : https://github.com/brahimazreg

Dépôt du projet :  
https://github.com/brahimazreg/Sales_Intelligent_Assistant_Khad

## 📄 Licence

Ce projet est distribué sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.


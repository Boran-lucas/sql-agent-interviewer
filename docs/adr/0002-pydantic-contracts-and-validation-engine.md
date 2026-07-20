# ADR 0002 — Contrats Pydantic, moteur de validation Pandas, et interface LLM abstraite

## Décision
Introduire trois éléments en Phase 2 :
1. Des modèles Pydantic (`domain/models.py`) comme contrat de données entre
   toutes les couches (API, validation, fournisseur de questions).
2. Un moteur de validation (`domain/validator.py`) qui compare le résultat
   de la requête du candidat à celui de la requête attendue via des
   DataFrames Pandas.
3. Une interface abstraite `QuestionProvider` (`infrastructure/llm/base.py`)
   avec une implémentation mock (`MockQuestionProvider`), même si le vrai
   client LLM n'arrive qu'en Phase 3.

## Pourquoi

### Contrats Pydantic
- Valide et documente la forme des données à la frontière de l'API — une
  requête malformée est rejetée avec une erreur 422 claire, plutôt que de
  provoquer un `AttributeError` ou un bug silencieux plus loin dans la
  logique métier.
- Sert de documentation vivante (via le schéma OpenAPI généré
  automatiquement par FastAPI) — utile pour le frontend Streamlit à venir.

### Comparaison par DataFrame plutôt que par égalité stricte du résultat
- **L'ordre des lignes n'est pas garanti en SQL sans `ORDER BY`.** Un
  candidat peut écrire une requête parfaitement correcte dont les lignes
  sortent dans un ordre différent de la requête de référence. Comparer
  les DataFrames après tri (`_normalize`) évite de pénaliser une bonne
  réponse à cause d'un détail non-sémantique.
- **L'ensemble des colonnes est comparé indépendamment de leur ordre**,
  pour la même raison : `SELECT name, salary` et `SELECT salary, name`
  doivent être considérés équivalents.
- Alternative écartée : comparer les résultats bruts du curseur SQLite
  (tuples dans l'ordre d'origine) — trop fragile, aurait généré des faux
  négatifs fréquents et frustrants pour l'utilisateur.

### Échec de requête = résultat de validation, pas une exception 500
- Le SQL soumis par le candidat est une **frontière de confiance** : une
  requête invalide (faute de syntaxe, table inexistante) est un cas
  attendu, pas un bug de l'application. `validate_answer` capture
  l'exception et renvoie un `ValidationResult` avec `correct=False` et un
  message explicite, plutôt que de laisser un statut 500 remonter à
  l'utilisateur.

### Interface `QuestionProvider` introduite avant le vrai client LLM
- Correspond directement au nœud `LLM_Svc` du diagramme d'architecture :
  l'API ne dépend jamais d'un client LLM concret, seulement de
  l'interface. En Phase 3, remplacer `MockQuestionProvider` par un
  fournisseur réel (Groq/OpenAI) ne demandera **aucune modification** à
  `app/main.py` — seule la fonction `get_question_provider` (injection de
  dépendance FastAPI) changera.
- Bénéfice concret déjà obtenu : les tests de `test_api.py` s'exécutent
  sans appel réseau, sans clé API, et de façon déterministe.

## Trade-off / limite connue
L'état de l'application (`_db_conn`, `_questions`) est actuellement stocké
dans des variables globales au niveau du module `app/main.py`. Ça
fonctionne pour un seul process avec une connexion partagée
(`check_same_thread=False`, voir ADR 0001), mais ce n'est pas un modèle de
session par utilisateur — deux candidats en parallèle partageraient le
même dictionnaire `_questions`. À revisiter si l'app doit gérer plusieurs
candidats simultanés (probable dès qu'un vrai déploiement multi-utilisateur
est envisagé) : il faudra un état par session (ex. token de session en
en-tête, store type Redis) plutôt qu'un état global de process.

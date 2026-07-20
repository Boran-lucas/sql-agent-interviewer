# ADR 0001 — SQLite en mémoire comme couche base de données de l'entretien

## Décision
Utiliser `sqlite3` (bibliothèque standard) avec une connexion en mémoire
(`:memory:`) comme base de données sur laquelle chaque session d'entretien
s'exécute, réamorcée à chaque appel à `create_seeded_db()`.

## Pourquoi
- **Isolation par session** : chaque candidat/session obtient un jeu de
  données neuf et identique, sans coût de mise en place et sans risque de
  fuite d'état entre sessions — pas de job de nettoyage, pas de bug d'état
  partagé.
- **Statelessness pour la scalabilité** : aucune base persistante à
  provisionner, migrer, ou pooler. L'app peut scaler horizontalement sans
  coordonner l'accès à une base entre instances.
- **Zéro dépendance infra pour un MVP** : aucun service de base de données
  externe à faire tourner, déployer, ou payer pendant qu'on valide le
  produit.

## Alternatives envisagées
- **Base persistante (Postgres/fichier SQLite)** : écartée pour l'instant —
  ajouterait de la charge de migration/ops sans bénéfice pour le MVP,
  puisqu'il n'y a pas (encore) de besoin de conserver l'historique des
  sessions. À reconsidérer si des analytics sur la performance des
  candidats dans le temps deviennent un besoin (nécessiterait un store
  dédié, pas un détournement de cette base d'entretien).

## Détails d'implémentation à retenir (les pièges)

- **`PRAGMA foreign_keys = ON` doit être activé sur chaque connexion.**
  SQLite n'applique pas les contraintes `FOREIGN KEY` par défaut. Sans ça,
  le problème n'est pas une erreur bruyante : une donnée orpheline (ex.
  `department_id = 999` qui n'existe pas) s'insère **silencieusement**,
  sans exception. C'est le danger réel — un bug d'intégrité référentielle
  invisible, pas un crash (voir `test_foreign_keys_are_enforced`).

- **`conn.row_factory = sqlite3.Row`** pour accéder aux colonnes par nom
  (`row["name"]`) plutôt que par index positionnel — utile dès que le
  moteur de validation (Phase 2) extrait des colonnes par nom.

- **Toutes les insertions du seed utilisent des requêtes paramétrées**
  (`?`), jamais de formatage de chaîne. Sur ces données de seed, le risque
  réel est nul puisqu'on contrôle la donnée nous-mêmes — mais c'est le
  réflexe anti-injection SQL (OWASP) qu'on prend maintenant, sur du code
  sans enjeu, pour qu'il soit automatique une fois que cette même couche
  de connexion exécutera du SQL soumis par un candidat (donnée non fiable,
  surface d'attaque réelle).

- **`check_same_thread=False` est nécessaire dès que la connexion est
  partagée entre requêtes HTTP (Phase 2).** Par défaut, `sqlite3` interdit
  d'utiliser une connexion depuis un thread différent de celui qui l'a
  créée. FastAPI exécute les routes synchrones (`def`) dans un threadpool
  interne — donc une connexion créée au démarrage de l'app peut être
  sollicitée depuis un thread différent à chaque requête, ce qui lève
  `sqlite3.ProgrammingError` sans ce flag. Ce n'est pas un problème de
  thread-safety résolu pour autant (voir trade-off ci-dessous) : ça
  autorise juste l'usage cross-thread, l'accès concurrent reste protégé
  par les verrous internes de SQLite (donc correct pour du read-mostly,
  pas garanti pour de l'écriture concurrente intensive).

## Trade-off accepté
Pas de persistance = pas de trace d'audit intégrée de ce qu'un candidat a
réellement exécuté. Si c'est nécessaire plus tard, ça doit être une
préoccupation de logging séparée et explicite — pas glissée dans la base
d'entretien elle-même.

Autre limite connue : une connexion globale unique en mémoire par
processus (voir ADR 0002) convient à un seul worker/process ; ça devra
être repensé si l'app tourne un jour avec plusieurs workers/processus en
parallèle (Phase 4 / déploiement).

---
*Note de convention : ce fichier et les futurs ADR sont rédigés en
français ; le code (noms de variables, docstrings, commentaires) reste en
anglais, conformément aux conventions habituelles du projet.*

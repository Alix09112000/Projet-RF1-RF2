# Décisions techniques

Chaque décision structurante est notée ici avec sa date et sa raison. On n'efface pas une
décision : on en ajoute une nouvelle qui la remplace.

## D1 — Système indépendant de Canalbox (2026-10)
L'outil ne se connecte à aucun système Canalbox, Power BI compris, ni maintenant ni plus tard.
Les équipes Canalbox déposent elles-mêmes les fichiers. Conséquence : hébergement dédié,
comptes propres à l'outil, import par fichiers.

## D2 — Périmètre : Côte d'Ivoire, Abidjan seulement (2026-10)
Une seule ville, `ABJ`. La table `cities` est conservée pour pouvoir en ajouter sans refonte.
Les lignes d'autres pays présentes dans un fichier déposé sont ignorées avec un avertissement.

## D3 — FastAPI + React séparés (2026-10)
API Python (même langage que le moteur de calcul), interface React servie en statique par
Caddy, qui relaie `/api/*`. Une seule origine en production : pas de souci de cookies tiers.

## D4 — Sessions par cookie signé (2026-10)
Jeton JWT HS256 dans un cookie `httpOnly`, `SameSite=Lax`, `Secure` en HTTPS.
Mots de passe hachés avec argon2.

## D5 — Rôles en énumération (2026-10)
Quatre rôles fixes (`contributor`, `controller`, `viewer`, `admin`) stockés sur l'utilisateur.
Une table de rôles n'apporterait rien tant que les droits ne sont pas paramétrables.

## D6 — Moteur de calcul prouvé bloc par bloc (2026-10)
Chaque bloc de formules Excel est réécrit puis comparé aux valeurs d'un RF réel rempli
(`api/tests/golden/`). Un bloc n'est terminé que si son test passe.

## D7 — Commentaires par règles derrière une interface (2026-10)
Le moteur de commentaires expose une interface unique. La première implémentation est par
règles ; une implémentation IA pourra la remplacer sans toucher au reste.

## D8 — Import en deux temps (2026-10)
Un dépôt est d'abord vérifié (`/imports/{type}/preview`) : rien n'entre dans les réalisés.
Il n'est enregistré qu'après confirmation explicite, avec acquittement des avertissements s'il y en a.
Un fichier refusé n'est jamais enregistré, mais son dépôt reste dans l'historique.

## D9 — Fichier d'origine archivé en base (2026-10)
Chaque fichier déposé est conservé tel quel (`import_batches.content`, avec son empreinte SHA-256),
téléchargeable depuis l'historique. Volume attendu : quelques centaines de Ko par mois.

## D10 — Réalisés en format long (2026-10)
`actual_values` : une ligne par source × ville × mois × indicateur (× ancienneté pour les échus).
Un mois réimporté remplace entièrement le précédent. Ajouter une colonne au fichier ne demande
pas de migration.

## D11 — Reprise de l'historique par le même import (2026-10)
L'historique (octobre 2017 à juin 2025) se charge en déposant une fois l'onglet actuel :
les lignes hors Côte d'Ivoire sont ignorées, les colonnes de cumul aussi. Pas de script dédié.

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

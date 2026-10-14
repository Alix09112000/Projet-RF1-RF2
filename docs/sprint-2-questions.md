# Sprint 2 — questions ouvertes et anomalies

Sources lues (dossier Drive « 02 - Fichiers Canalbox ») : `Fiche_onglet_B2C1`, `Fiche_onglet_SME1`.
Les autres fiches seront lues au moment du sprint qui les concerne.

## Fichiers introuvables dans le dossier Drive

Je ne les ai pas trouvés, ni par leur nom ni par une recherche :

- `Fiche_import_Source_BR_PBI_et_Source_echus` : je n'ai donc pas pu vérifier l'import du Sprint 1 par rapport à cette fiche.
- `Cartographie_Country_PL`
- `Moteur_B2C_1_blocs_de_codage` (nécessaire pour coder le moteur B2C1)
- Une fiche pour l'onglet `List`. Les 14 entités de List viennent de notre inventaire (`Inventaire_saisies_manuelles_Abidjan.csv`, lignes 2 à 15).

## Import (Sprint 1) — ce que l'on peut vérifier sans la fiche import

- Les **34 colonnes A à AH** sont contrôlées à l'identique : c'est conforme.
- Les **cumuls AI à AL** sont ignorés avec un avertissement. La feuille « Colonnes sources » de B2C1 montre que les lignes 34 à 36 et 291 lisent AI, AJ, AK et AL. Le moteur B2C1 devra donc les recalculer à partir des ventes D, E et F. Ce calcul n'est pas encore codé, il est prévu avec le moteur.
- **Mois de référence des échus** : le format long exige une date complète dans `Mois`. Le format croisé, lui, demande seulement l'année au moment du dépôt. Si la fiche import exige un mois de référence explicite (et pas seulement l'année), il faudra ajouter un champ « mois de référence » au dépôt. À confirmer en lisant la fiche.

## Anomalies relevées dans les fiches

Je les ai signalées sans les corriger.

1. **B2C1, lignes 405 et 406** : dans « Colonnes sources », SiS + VAD lit `AF` (`Reabonnement_espace_client`) et Espace Client lit `AE` (`Reabonnement Shop_in_shop`). Les deux colonnes semblent inversées.
2. **B2C1, ligne 5** : le libellé est « City › Paris » dans un modèle Abidjan.
3. **B2C1, ligne 80** : la ligne lit directement `DROPE1!Q282` au lieu de passer par une clé (anomalie déjà notée dans la fiche).
4. **B2C1, ligne 312** : la variation mensuelle 0,01 est écrite en dur (déjà notée).
5. **SME1, lignes 116, 143, 226, 238 et 291** : ces libellés « B2C … » ont été conservés dans un onglet PME.
6. **SME1, ligne 233** : la ligne s'appelle « Mix OFFRE 1 », alors que les offres s'appellent « Offer SME 50 / 200 Mbps ».
7. **SME1, ligne 261** : « Relocations N-1 » est notée ENTRÉE, alors que la même ligne est un CALCUL dans B2C1 (ligne 294).
8. **SME1, lignes 295 à 349** : les prix et FAS se saisissent aussi sur les mois réels (I à N). Dans B2C1, ils ne se saisissent que sur les mois RF2 et BI (O à AF).
9. **SME1, ligne 396** : le coût par CPE est « à renseigner en négatif ». En B2C1 (ligne 434), aucune consigne n'est donnée. Le signe doit être harmonisé.

## Questions ouvertes

Les questions reprises des fiches figurent en premier.

| N° | Question | Origine | Bloque |
|---|---|---|---|
| Q1 | Où passe la frontière entre réel et RF2 : fin juin (B2C1, colonne N) ou fin juillet (KPI, colonne L) ? | Fiche B2C1, Q1 | Moteur |
| Q2 | Peut-on obtenir B2C1 avec ses formules de prévision ? | Fiche B2C1, Q2 | Moteur |
| Q3 | Les lignes 192 à 222 (winback par ancienneté) servent-elles ? | Fiche B2C1, Q3 | Moteur |
| Q4 | La ligne 312 (variation mensuelle) est-elle une saisie ou une valeur fixe ? | Fiche B2C1, Q4 | Saisie |
| Q5 | Quels sont les noms commerciaux des 4 offres PME (« OFFRE 3 », « OFFRE 4 ») ? | Fiche SME1, Q1 | Libellés |
| Q6 | SME1 ligne 40 : est-elle saisie par la DRCOM ou calculée à partir de la DROPE ? | Fiche SME1, Q2 | Moteur |
| Q7 | Les soldes « 1 − parts » sont-ils corrects pour B2C1 ligne 396 et SME1 lignes 18, 187 et 358 ? Je les ai déduits des valeurs du modèle vide (1 en RF2 et BI). Pour B2C1 lignes 30 et 225 (START), la fiche les confirme. | Sprint 2 | Non (affiché « règle à confirmer ») |
| Q8 | Quelles plages de valeurs sont autorisées pour chaque hypothèse (par exemple un taux entre 0 et 100 %, ou une valeur négative admise) ? Les fiches n'en donnent aucune, donc aucun contrôle de plage n'est appliqué. | Sprint 2 | Non |
| Q9 | Lignes MIXTE : quelles cellules exactement sont beiges ? La fiche donne seulement la plage (O à AF ou I à AF). J'ai considéré toute la plage comme saisissable. | Sprint 2 | Non |
| Q10 | La saisie de B2C1 et SME1 est-elle bien réservée à la DRCOM ? Et DRB2B, que le fichier dit « incluse dans DRCOM », doit-elle aussi pouvoir saisir ? | Fiche SME1 (Qui remplit) | Droits |
| Q11 | Pour les mois réels, les lignes I à N (congés, effectifs, ajustement du parc) se saisissent-elles à chaque cycle ou une seule fois ? | Sprint 2 | Non |
| Q12 | La table List contient-elle d'autres listes de choix que entité / pays / ville ? Il faut la fiche List. | Sprint 2 | Paramètres |

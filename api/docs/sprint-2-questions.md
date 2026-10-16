# Sprint 2 — questions ouvertes et anomalies

Sources lues : `Fiche_onglet_B2C1`, `Fiche_onglet_SME1`, `Fiche_import_Source_BR_PBI_et_Source_echus`.

## Import (Sprint 1) — vérifié avec « Fiche_import_Source_BR_PBI_et_Source_echus »

J'ai vérifié la structure des vrais fichiers (en-têtes, types, nombre de lignes) sans copier aucune donnée.

| Contrôle demandé par la fiche | Dans l'outil |
|---|---|
| En-têtes A à AH exacts | Conforme. Les 34 libellés sont identiques au vrai fichier. La lecture se fait par nom de colonne, pas par lettre : une colonne déplacée ne fausse donc rien. |
| AI à AL recalculés | Les colonnes sont ignorées avec un avertissement. Dans le vrai fichier, ce sont bien des formules. Le recalcul se fera avec le moteur B2C1. |
| Mois du 1er, sans trou | Un mois manquant produit un **avertissement**, pas un blocage. **Écart, à confirmer : faut-il bloquer ?** |
| Une seule ligne par (ville, mois) | Conforme : un doublon bloque le dépôt. |
| Dernier mois = dernier mois réel annoncé | **Pas encore fait.** Il faut le paramètre « dernier mois réel » du cycle, qui viendra avec le moteur. |
| Valeurs numériques positives | Un texte bloque le dépôt. Une valeur négative produit désormais un **avertissement** (ajouté). |
| Échus : ancienneté ≥ 1, ville connue | **Corrigé.** L'ancienneté était plafonnée à 40, alors que le vrai fichier va jusqu'à 63 pour ABJ : il aurait été refusé. Il n'y a plus de plafond. Au-delà de 120 mois, l'outil affiche un avertissement. |
| Échus : mois de référence explicite | L'année est demandée au dépôt du format croisé. Chaque valeur est stockée avec une date complète (mois + année). Le choix du mois lu par B2C1 (C = janvier, H = juin) viendra du « dernier mois réel » du cycle. |
| Historique et recalcul sur un ancien import | Chaque dépôt est conservé (date, fichier, utilisateur). Le recalcul viendra avec le moteur. |

**Structure réelle de « Source échus » :** le fichier a 2 lignes d'en-tête. La première porte les mois, la seconde « Ancienneté (Mois) / Villes / ECHUS ». La seconde est maintenant reconnue et ignorée. 5 tests reproduisent cette structure avec des valeurs fictives.

**Anomalie dans les données échus :** ABJ a une ligne d'ancienneté **663 mois**, soit 55 ans, isolée après 63. Est-ce une erreur d'export, ou une ligne « reliquat » à garder ?

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
| Q13 | Faut-il bloquer un dépôt Réalisés qui a un mois manquant (aujourd'hui, simple avertissement) ? | Fiche import | Non |
| Q14 | Ancienneté 663 dans les échus ABJ : erreur d'export ou ligne à garder ? | Fichier réel | Non |
| Q15 | L'extrait Power BI est-il complet (tout l'historique) ou seulement les nouveaux mois ? Aujourd'hui, l'outil remplace les mois déposés et garde les autres. | Fiche import, Q2 | Non |
| Q16 | Qui charge les deux fichiers : la DRCOM ou la direction financière ? Aujourd'hui, ce sont le contrôle de gestion et l'administrateur. | Fiche import, Q5 | Droits |

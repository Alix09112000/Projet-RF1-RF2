# Backlog — à transformer en issues GitHub

Format : une issue par ligne, titre en gras, critères d'acceptation en dessous.

## Sprint 1 — Import des données (livré, à valider sur fichiers réels)

- **Déposer le fichier Réalisés commerciaux**
  - Un utilisateur `controller` dépose un .xlsx ou .csv de la forme « Source BR PBI » (colonnes A à AH).
  - Les 34 en-têtes sont vérifiés à l'identique ; une colonne manquante bloque l'import.
  - Seules les lignes `Cote d Ivoire` / `ABJ` sont importées ; les autres sont ignorées avec un avertissement.
- **Déposer le fichier Échus**
  - Format long : Ville, Mois, Anciennete_mois, Nb_echus.
  - Le format croisé actuel est accepté si l'année est saisie au dépôt.
- **Contrôles bloquants** : en-têtes, ville, mois sans année, texte dans une colonne numérique, doublons.
- **Avertissements** : total ≠ somme du détail, variation > 30 % sur un mois, mois déjà importé, mois absent.
- **Rapport d'import** : liste des erreurs avec numéro de ligne et colonne, lisible par un non-technicien.
- **Historique des dépôts** : table `import_batches`, fichier d'origine archivé, avertissements confirmés.
- **Reprise de l'historique** : script unique qui charge les mois passés depuis le fichier Excel existant.

## Sprint 2 — Saisie et paramètres

- **Saisir une hypothèse** par segment, ligne et mois, pour la version RF en brouillon.
- **Contrôler la saisie** : plage autorisée (bloquant), plage attendue (justification obligatoire).
- **Historiser** chaque changement : ancienne valeur, nouvelle valeur, auteur, date, justification.
- **Régler les paramètres** (taux de change, barèmes, seuil d'écart) — rôle `controller`.
- **Consulter l'historique** des saisies, paramètres et dépôts, filtrable.

## À obtenir de Canalbox

- [ ] Démonstration du fichier RF1/RF2 par un utilisateur quotidien (avant S1)
- [ ] Un fichier réel de chaque source (avant S1)
- [ ] Liste des directions, contributeurs et droits (avant S2)
- [ ] Un RF complet rempli, référence du moteur de calcul (avant S3)

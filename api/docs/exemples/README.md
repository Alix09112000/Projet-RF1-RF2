# Fichiers d'exemple (valeurs fictives)

Pour tester l'écran Import. Aucune donnée Canalbox réelle.

| Fichier | Résultat attendu |
| --- | --- |
| 1_realises_valide.csv | Valide : 3 mois (avril à juin 2026), aucun avertissement |
| 2_realises_avec_avertissements.csv | Valide avec avertissements : total incohérent, ligne Gabon ignorée, variation, mois manquant si 1 a été importé |
| 3_realises_erreurs.csv | Refusé : ville ABI, mois « juillet », texte « n/a » |
| 4_echus_valide.csv | Valide : 3 mois × 12 anciennetés |
| 5_echus_format_croise.csv | Refusé sans année ; valide avec l'année 2026 (ligne LBV ignorée) |

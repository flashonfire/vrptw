---
title: Projet – Vehicle Routing Problem with Time Windows (VRPTW)
author: ["Guillaume Calderon", "Eymeric Dechelette"]
date: 11/05/2026
---

# Introduction

## Objectif

Le but du projet est de produire des solutions valides au Vehicle Routing Problem with Time Windows (VRPTW) et de comparer plusieurs approches de recherche locale / métaheuristiques sur des instances fournies.

La comparaison porte sur :

- Temps d’exécution
- Nombre de véhicules utilisés
- Distance totale parcourue

Méthodes comparées :

- Marche aléatoire (baseline)
- Descente (hill-climbing)
- Recherche tabou
- Recuit simulé

## Choix technologique : pourquoi Rust ?

Nous avons choisi Rust pour :

- Performance : compilation native, exécution rapide.
- Mesures plus propres : moins d’effet d’un interpréteur ou d’une VM sur les temps.
- Robustesse : gestion d’erreurs explicite (crate `anyhow`) ce qui permet au LLM de développer plus éfficacement et mieux cibler leur erreurs.
- Habitude : nous avons déjà une expérience avec Rust, ce qui nous a permis de démarrer rapidement.
- Reproductibilité : environnement optionnel via `flake.nix`.

# Travail réalisé

## Construction d’une solution initiale

Les méthodes comparées partent d’une solution initiale construite par un procédé simple :

- Ordre initial des clients généré aléatoirement
- Insertion séquentielle dans la tournée courante
- Si insertion impossible (capacité ou temps), création d’une nouvelle tournée

Cette partie sert de base commune afin de comparer les méthodes de manière équitable.

## Opérateurs de voisinage

Les méthodes utilisent des mouvements de voisinage pour produire des solutions voisines. Nous comparons trois configurations de voisinage :

- `relocate`
- `relocate` + `swap`
- `relocate` + `swap` + `2-opt`

Dans tous les cas, un mouvement est accepté uniquement si la solution obtenue reste valide (capacité et fenêtres de temps).

### Relocate

Principe : déplacer un client d’une position vers une autre.

Deux variantes sont utilisées :

- relocate intra-tournée : retirer un client d’une tournée et le réinsérer à une autre position dans la même tournée
- relocate inter-tournées : retirer un client d’une tournée et l’insérer dans une autre tournée

Ce mouvement permet d’ajuster finement l’affectation des clients aux véhicules et l’ordre de visite.

### Swap

Principe : échanger deux clients.

Deux variantes sont utilisées :

- swap intra-tournée : échanger la position de deux clients dans une même tournée
- swap inter-tournées : échanger un client d’une tournée A avec un client d’une tournée B

Ce mouvement est utile pour corriger des “mauvaises associations” (un client dans la mauvaise tournée) ou pour réduire la distance localement.

### 2-opt

Principe : choisir deux arêtes dans une tournée et inverser le segment intermédiaire afin de supprimer des croisements et raccourcir le trajet.

Dans ce projet, `2-opt` est appliqué en intra-tournée uniquement.

### Vérification de validité

Après chaque mouvement, on vérifie :

- capacité : la somme des demandes de chaque tournée ne dépasse pas la capacité du véhicule
- fenêtres de temps : pour chaque tournée, on simule la progression temporelle dans l’ordre de visite
  - le temps augmente avec le temps de trajet
  - si arrivée avant `ready_time`, attente jusqu’à `ready_time`
  - si arrivée après `due_time`, la tournée est invalide
  - le temps de service est ajouté à chaque client

Si la solution est invalide, le voisin est rejeté.

### Remarque sur l’évaluation

Pour comparer équitablement les voisinages, on utilise la même fonction d’évaluation et la même règle de comparaison des solutions.

# Protocole de comparaison

## Mesures et métriques

Pour chaque instance et chaque méthode, on mesure :

- Qualité
  - `K` (nombre de véhicules)
  - `D` (distance totale)
  - Faisabilité (valide / invalide)
- Performance
  - Temps d’exécution

Mesure du temps : temps d’exécution du binaire compilé en mode release. Pour éviter d’inclure du temps de compilation.

## Répétitions et paramètres

- Répétitions : nombre de runs par méthode et par instance (à renseigner)
- Graine aléatoire : à renseigner, ou bien indiquer qu’on utilise des graines différentes
- Budget : temps maximum ou nombre d’itérations (à renseigner)

## Machine et environnement

- CPU, RAM, OS : à renseigner
- Version Rust : à renseigner

# Résultats

## Tableaux

Tableau minimal recommandé :

| Instance | Méthode | Faisable | Véhicules K | Distance D | Temps |
| -------- | ------- | -------- | ----------: | ---------: | ----: |

Si plusieurs runs sont effectués, ajouter :

- moyenne et écart-type sur `D`
- meilleure valeur sur `D`

## Graphiques

Pour illustrer les résultats, on fournit :

- Courbes de convergence (distance en fonction des itérations ou du temps)
- Distribution des résultats (par exemple boxplot par méthode)
- Visualisation 2D des tournées pour quelques instances

Insérer ici les figures générées, par exemple :

- `figures/data101_routes_tabu.png`
- `figures/data101_routes_recuit.png`
- `figures/data101_convergence.png`

# Discussion

Points à discuter :

- Compromis temps / qualité : quelle méthode atteint de bonnes solutions le plus vite
- Robustesse : variance entre runs, sensibilité à la graine
- Sensibilité aux paramètres : impact des paramètres principaux sur le résultat
- Impact des voisinages : quels mouvements apportent le plus

# Conclusion

- Résumer les conclusions de la comparaison (temps, qualité)
- Limites observées
- Améliorations possibles

# Annexe — Comment exécuter

## Avec Cargo

Depuis la racine du projet (dossier contenant `Cargo.toml`) :

- Exécution (debug) : `cargo run`
- Exécution (optimisée) : `cargo run --release`

Remarque : le programme charge pour l’instant une instance via un chemin relatif (ex : `data/data101.vrp`). Il faut lancer la commande depuis la racine du dépôt pour que les chemins vers `data/` fonctionnent.

## Mesurer le temps sous Linux

Compilation (une fois) :

- `cargo build --release`

Exemple de mesure du temps sur le binaire release :

- `/usr/bin/time -p ./target/release/vrptw`

Le champ d’intérêt dans la sortie est notamment :

- `real`

## Avec Nix (optionnel)

- Entrer dans le shell : `nix develop`
- Puis exécuter : `cargo run --release`

Alternative (en une commande) : `nix develop -c cargo run --release`

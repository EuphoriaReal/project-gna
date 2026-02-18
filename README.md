# Projet GNA — Générateurs de Nombres Aléatoires

Implémentation et analyse de générateurs de nombres pseudo-aléatoires (PRNG), tests statistiques de qualité, et démonstrations d'attaques cryptographiques pédagogiques.

## Structure du projet

```
src/
├── generators/
│   ├── lcg.py                # Linear Congruential Generator
│   ├── mersenne_twister.py   # Mersenne Twister (MT19937)
│   ├── bbs.py                # Blum-Blum-Shub
│   ├── box_muller.py         # Transformée de Box-Muller (uniforme -> normale)
│   ├── drbg.py               # HMAC-DRBG (NIST SP 800-90A)
│   ├── os_urandom.py         # os.urandom (référence système)
│   └── xor_nrbg.py           # Combinaison XOR de plusieurs générateurs
│
├── tests_statistiques/
│   ├── entropie_shannon.py   # Entropie de Shannon
│   ├── chi2.py               # Test du Chi-carré
│   ├── ks_test.py            # Test de Kolmogorov-Smirnov
│   └── autocorrelation.py    # Test d'autocorrélation
│
├── attaques/
│   ├── lcg_seed_recovery.py  # Récupération des paramètres d'un LCG
│   └── mt_state_recovery.py  # Reconstruction de l'état interne du MT19937
│
└── test_generateurs.py       # Script principal
```

## Prérequis

- Python 3.8+

## Installation

```bash
git clone https://github.com/EuphoriaReal/project-gna
cd projet-gna

python3 -m venv .venv
source .venv/bin/activate

pip install matplotlib
```

## Utilisation

### Tester les générateurs

Depuis la racine du projet :

```bash
python3 src/test_generateurs.py
```

Lance une démonstration de chaque générateur, suivie des tests statistiques (Shannon, Chi², KS, Autocorrélation) sur 10 000 octets.

### Lancer les attaques

```bash
cd src

python3 -m attaques.lcg_seed_recovery   # Récupération des paramètres LCG
python3 -m attaques.mt_state_recovery   # Clonage de l'état MT19937
```

> ⚠️ Ces attaques sont strictement pédagogiques. Toute utilisation sur des systèmes réels est interdite.

## Détail des implémentations

### Générateurs

Chaque générateur expose la même interface :

| Méthode              | Description                             |
| --------------------- | --------------------------------------- |
| `__init__(graine)`  | Initialise le générateur              |
| `generate_bytes(n)` | Renvoie `n` octets pseudo-aléatoires |
| `generate(n)`       | Renvoie `n` entiers                   |

### Tests statistiques

| Test                | Ce qu'il mesure                                                 |
| ------------------- | --------------------------------------------------------------- |
| Entropie de Shannon | Quantité d'information — cible : ~8.0 bits/octet              |
| Chi-carré          | Uniformité de la distribution des octets                       |
| Kolmogorov-Smirnov  | Écart entre distribution empirique et uniforme théorique      |
| Autocorrélation    | Absence de corrélation entre valeurs successives — cible : ~0 |

### Génération des graphiques

```bash
python3 src/generer_graphiques.py
```

### Attaques

**LCG Seed Recovery** — À partir de 6 sorties consécutives, on retrouve le module `m` (méthode des différences + PGCD), le multiplicateur `a` (inverse modulaire), puis l'incrément `c`. Les sorties futures sont alors prédictibles à 100%.

**MT State Recovery** — Le tempering du MT19937 est une bijection inversible. En observant 624 sorties consécutives, on inverse le tempering pour reconstruire les 624 mots de l'état interne et cloner le générateur.

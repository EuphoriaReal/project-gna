"""
Génération des graphiques pour chaque test statistique.

Produit des figures dans :
  resultats/shannon/
  resultats/chi2/
  resultats/ks/
  resultats/autocorrelation/
  resultats/box_muller/
  resultats/comparatif/
"""

import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from generators.lcg import LCG
from generators.mersenne_twister import MersenneTwister
from generators.bbs import BbsGenerator
from generators.drbg import HmacDrbgGenerator
from generators.os_urandom import SystemGenerator
from generators.xor_nrbg import XorGenerator
from generators.box_muller import BoxMullerGenerator

from tests_statistiques.entropie_shannon import ShannonEntropyTest
from tests_statistiques.chi2 import Chi2Test
from tests_statistiques.autocorrelation import AutocorrelationTest
from tests_statistiques.ks_test import KsTest


# --- Configuration ---
N_OCTETS = 10000
DOSSIER_BASE = os.path.join(os.path.dirname(__file__), "resultats")

COULEURS = {
    "LCG":         "#e74c3c",
    "MT19937":     "#3498db",
    "BBS":         "#2ecc71",
    "HMAC-DRBG":   "#9b59b6",
    "os.urandom":  "#f39c12",
    "XOR(LCG+MT)": "#1abc9c",
    "Box-Muller":  "#e67e22",
}


def box_muller_to_bytes(n):
    """Convertit n valeurs gaussiennes en octets (mu=127.5, sigma=40, clamp [0,255])."""
    gen_bm = BoxMullerGenerator(MersenneTwister(42).next_float)
    octets = []
    for _ in range(n):
        val = gen_bm.next() * 40 + 127.5
        octets.append(int(max(0, min(255, val))))
    return bytes(octets)


def construire_echantillons():
    """Génère les échantillons pour chaque générateur."""
    return {
        "LCG":         LCG(42).generate_bytes(N_OCTETS),
        "MT19937":     MersenneTwister(42).generate_bytes(N_OCTETS),
        "BBS":         BbsGenerator(12345, 3334888603, 3996958799).generate_bytes(N_OCTETS),
        "HMAC-DRBG":   HmacDrbgGenerator(os.urandom(32), os.urandom(16)).generate_bytes(N_OCTETS),
        "os.urandom":  SystemGenerator().generate_bytes(N_OCTETS),
        "XOR(LCG+MT)": XorGenerator([LCG(1), MersenneTwister(7)]).generate_bytes(N_OCTETS),
        "Box-Muller":  box_muller_to_bytes(N_OCTETS),
    }


def creer_dossier(nom):
    chemin = os.path.join(DOSSIER_BASE, nom)
    os.makedirs(chemin, exist_ok=True)
    return chemin


# ───────────────────── Shannon ─────────────────────

def graphiques_shannon(echantillons):
    """Barres comparatives d'entropie + histogramme de fréquences par générateur."""
    dossier = creer_dossier("shannon")
    test = ShannonEntropyTest()

    # 1. Barres comparatives
    noms = list(echantillons.keys())
    entropies = [test.run(echantillons[n]) for n in noms]
    couleurs = [COULEURS[n] for n in noms]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(noms, entropies, color=couleurs, edgecolor="white", linewidth=0.8)
    ax.axhline(y=8.0, color="gray", linestyle="--", label="Maximum (8.0)")
    ax.set_ylabel("Entropie (bits/octet)")
    ax.set_title("Entropie de Shannon par générateur")
    ax.set_ylim(0, 8.5)
    ax.legend()
    for bar, val in zip(bars, entropies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "comparatif_entropie.png"), dpi=150)
    plt.close(fig)

    # 2. Histogramme de fréquences des octets pour chaque générateur
    for nom, donnees in echantillons.items():
        freq = [0] * 256
        for octet in donnees:
            freq[octet] += 1

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.bar(range(256), freq, color=COULEURS[nom], width=1.0, edgecolor="none")
        attendu = N_OCTETS / 256
        ax.axhline(y=attendu, color="red", linestyle="--", linewidth=1,
                    label=f"Fréquence attendue ({attendu:.1f})")
        ax.set_xlabel("Valeur de l'octet")
        ax.set_ylabel("Fréquence")
        ax.set_title(f"Distribution des octets — {nom}")
        ax.legend()
        fig.tight_layout()
        nom_fichier = nom.replace(".", "_").replace("(", "").replace(")", "")
        fig.savefig(os.path.join(dossier, f"distribution_{nom_fichier}.png"), dpi=150)
        plt.close(fig)

    print(f"  Shannon : {len(echantillons) + 1} figures -> {dossier}")


# ───────────────────── Chi² ─────────────────────

def graphiques_chi2(echantillons):
    """Barres de statistique chi² et p-values."""
    dossier = creer_dossier("chi2")
    test = Chi2Test()

    noms = list(echantillons.keys())
    stats = []
    pvals = []
    verdicts = []
    for n in noms:
        s, p, v = test.run(echantillons[n])
        stats.append(s)
        pvals.append(p)
        verdicts.append(v)

    couleurs = [COULEURS[n] for n in noms]

    # 1. Statistique chi²
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(noms, stats, color=couleurs, edgecolor="white")
    ax.axhline(y=255, color="gray", linestyle="--", label="df = 255 (valeur attendue)")
    ax.set_ylabel("Statistique χ²")
    ax.set_title("Test du Chi-carré — Statistique par générateur")
    ax.legend()
    for bar, val, v in zip(bars, stats, verdicts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.1f}\n{v}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "chi2_statistique.png"), dpi=150)
    plt.close(fig)

    # 2. P-values
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(noms, pvals, color=couleurs, edgecolor="white")
    ax.axhline(y=0.05, color="red", linestyle="--", label="Seuil α = 0.05")
    ax.set_ylabel("p-value")
    ax.set_title("Test du Chi-carré — P-values")
    ax.set_ylim(0, 1.1)
    ax.legend()
    for bar, val, v in zip(bars, pvals, verdicts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "chi2_pvalues.png"), dpi=150)
    plt.close(fig)

    print(f"  Chi²    : 2 figures -> {dossier}")


# ───────────────────── Kolmogorov-Smirnov ─────────────────────

def graphiques_ks(echantillons):
    """CDF empirique vs théorique + barres de statistique D."""
    dossier = creer_dossier("ks")
    test = KsTest()

    noms = list(echantillons.keys())
    stats_d = []
    pvals = []
    verdicts = []
    for n in noms:
        s, p, v = test.run(echantillons[n])
        stats_d.append(s)
        pvals.append(p)
        verdicts.append(v)

    # 1. CDF empirique vs théorique pour chaque générateur
    for nom, donnees in echantillons.items():
        valeurs = sorted(octet / 255.0 for octet in donnees)
        n = len(valeurs)
        cdf_emp = [(i + 1) / n for i in range(n)]

        fig, ax = plt.subplots(figsize=(8, 5))
        # On sous-échantillonne pour ne pas surcharger le graphique
        pas = max(1, n // 1000)
        ax.plot([valeurs[i] for i in range(0, n, pas)],
                [cdf_emp[i] for i in range(0, n, pas)],
                color=COULEURS[nom], linewidth=1.2, label="CDF empirique")
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="CDF uniforme")
        ax.set_xlabel("Valeur normalisée")
        ax.set_ylabel("Probabilité cumulée")
        ax.set_title(f"Test KS — CDF empirique vs uniforme — {nom}")
        ax.legend()
        fig.tight_layout()
        nom_fichier = nom.replace(".", "_").replace("(", "").replace(")", "")
        fig.savefig(os.path.join(dossier, f"cdf_{nom_fichier}.png"), dpi=150)
        plt.close(fig)

    # 2. Barres comparatives de la statistique D
    couleurs_list = [COULEURS[n] for n in noms]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(noms, stats_d, color=couleurs_list, edgecolor="white")
    ax.set_ylabel("Statistique D")
    ax.set_title("Test de Kolmogorov-Smirnov — Distance maximale D")
    for bar, val, v in zip(bars, stats_d, verdicts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f"D={val:.4f}\n{v}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "ks_statistique_d.png"), dpi=150)
    plt.close(fig)

    print(f"  KS      : {len(echantillons) + 1} figures -> {dossier}")


# ───────────────────── Autocorrélation ─────────────────────

def graphiques_autocorrelation(echantillons):
    """Coefficients d'autocorrélation par lag pour chaque générateur."""
    dossier = creer_dossier("autocorrelation")
    test = AutocorrelationTest()
    lags = [1, 2, 4, 8, 16, 32]

    # 1. Un graphique par générateur
    for nom, donnees in echantillons.items():
        resultats = test.run(donnees, lags=lags)

        fig, ax = plt.subplots(figsize=(8, 5))
        valeurs = [resultats[lag] for lag in lags]
        ax.bar([str(l) for l in lags], valeurs, color=COULEURS[nom], edgecolor="white")
        ax.axhline(y=0, color="black", linewidth=0.5)
        ax.axhline(y=0.05, color="red", linestyle="--", linewidth=0.8, label="Seuil ±0.05")
        ax.axhline(y=-0.05, color="red", linestyle="--", linewidth=0.8)
        ax.set_xlabel("Lag")
        ax.set_ylabel("Coefficient d'autocorrélation")
        ax.set_title(f"Autocorrélation — {nom}")
        ax.set_ylim(-0.3, 0.3)
        ax.legend()
        fig.tight_layout()
        nom_fichier = nom.replace(".", "_").replace("(", "").replace(")", "")
        fig.savefig(os.path.join(dossier, f"autocorr_{nom_fichier}.png"), dpi=150)
        plt.close(fig)

    # 2. Comparatif : toutes les courbes sur un même graphique
    fig, ax = plt.subplots(figsize=(10, 5))
    for nom, donnees in echantillons.items():
        resultats = test.run(donnees, lags=lags)
        valeurs = [resultats[lag] for lag in lags]
        ax.plot(lags, valeurs, marker="o", label=nom, color=COULEURS[nom], linewidth=1.5)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.axhline(y=0.05, color="red", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.axhline(y=-0.05, color="red", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Lag")
    ax.set_ylabel("Coefficient d'autocorrélation")
    ax.set_title("Autocorrélation comparée — Tous les générateurs")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "comparatif_autocorrelation.png"), dpi=150)
    plt.close(fig)

    print(f"  Autocorr: {len(echantillons) + 1} figures -> {dossier}")


# ───────────────────── Comparatif global ─────────────────────

def graphique_comparatif(echantillons):
    """Tableau visuel récapitulatif de tous les tests."""
    dossier = creer_dossier("comparatif")

    test_shan = ShannonEntropyTest()
    test_chi2 = Chi2Test()
    test_ks = KsTest()
    test_ac = AutocorrelationTest()

    noms = list(echantillons.keys())
    resultats = {}
    for nom in noms:
        d = echantillons[nom]
        shan = test_shan.run(d)
        _, p_chi, v_chi = test_chi2.run(d)
        _, p_ks, v_ks = test_ks.run(d)
        ac = test_ac.run(d, lags=[1, 8])
        max_ac = max(abs(v) for v in ac.values())
        v_ac = "PASS" if max_ac < 0.05 else "FAIL"
        resultats[nom] = {
            "Shannon": shan,
            "Chi²": v_chi,
            "KS": v_ks,
            "Autocorr": v_ac,
        }

    # Tableau visuel avec couleurs
    tests = ["Shannon", "Chi²", "KS", "Autocorr"]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")

    # Données du tableau
    cell_text = []
    cell_colors = []
    for nom in noms:
        row = []
        row_colors = []
        for t in tests:
            val = resultats[nom][t]
            if t == "Shannon":
                row.append(f"{val:.4f}")
                row_colors.append("#d4edda" if val > 7.9 else "#f8d7da")
            else:
                row.append(val)
                row_colors.append("#d4edda" if val == "PASS" else "#f8d7da")
        cell_text.append(row)
        cell_colors.append(row_colors)

    table = ax.table(
        cellText=cell_text,
        rowLabels=noms,
        colLabels=tests,
        cellColours=cell_colors,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    ax.set_title("Récapitulatif des tests statistiques", fontsize=14, pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "recapitulatif.png"), dpi=150)
    plt.close(fig)

    print(f"  Recap   : 1 figure  -> {dossier}")


# ───────────────────── Box-Muller (gaussien) ─────────────────────

def graphique_box_muller():
    """Histogramme de la distribution gaussienne + courbe N(0,1)."""
    dossier = creer_dossier("box_muller")

    gen_bm = BoxMullerGenerator(MersenneTwister(42).next_float)
    valeurs = gen_bm.generate(N_OCTETS)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(valeurs, bins=80, density=True, color=COULEURS["Box-Muller"],
            edgecolor="white", alpha=0.8, label="Box-Muller (échantillons)")

    # courbe théorique N(0, 1)
    x = [i / 100.0 for i in range(-400, 401)]
    y = [math.exp(-0.5 * xi * xi) / math.sqrt(2 * math.pi) for xi in x]
    ax.plot(x, y, "k-", linewidth=2, label="Densité N(0, 1)")

    ax.set_xlabel("Valeur")
    ax.set_ylabel("Densité")
    ax.set_title("Box-Muller — Distribution gaussienne vs N(0,1) théorique")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "distribution_gaussienne.png"), dpi=150)
    plt.close(fig)

    # QQ-plot simplifié
    valeurs_triees = sorted(valeurs)
    n = len(valeurs_triees)
    # quantiles théoriques via approximation inverse CDF normale
    quantiles_theo = []
    for i in range(n):
        p = (i + 0.5) / n
        # approximation de l'inverse de la CDF normale (Beasley-Springer-Moro)
        t = math.sqrt(-2 * math.log(min(p, 1 - p)))
        c0, c1, c2 = 2.515517, 0.802853, 0.010328
        d1, d2, d3 = 1.432788, 0.189269, 0.001308
        q = t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)
        if p < 0.5:
            q = -q
        quantiles_theo.append(q)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(quantiles_theo, valeurs_triees, s=2, color=COULEURS["Box-Muller"], alpha=0.5)
    lim = max(abs(min(valeurs_triees)), abs(max(valeurs_triees)), 4)
    ax.plot([-lim, lim], [-lim, lim], "k--", linewidth=1, label="Diagonale (N(0,1) parfaite)")
    ax.set_xlabel("Quantiles théoriques N(0,1)")
    ax.set_ylabel("Quantiles observés")
    ax.set_title("QQ-Plot — Box-Muller vs N(0,1)")
    ax.legend()
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "qqplot.png"), dpi=150)
    plt.close(fig)

    print(f"  BoxMull : 2 figures -> {dossier}")


# ───────────────────── Main ─────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  GENERATION DES GRAPHIQUES")
    print("=" * 50)

    print(f"\nGeneration des echantillons ({N_OCTETS} octets)...")
    echantillons = construire_echantillons()
    print("OK\n")

    print("Generation des figures :")
    graphiques_shannon(echantillons)
    graphiques_chi2(echantillons)
    graphiques_ks(echantillons)
    graphiques_autocorrelation(echantillons)
    graphique_box_muller()
    graphique_comparatif(echantillons)

    print(f"\nTermine. Toutes les figures sont dans : {DOSSIER_BASE}/")

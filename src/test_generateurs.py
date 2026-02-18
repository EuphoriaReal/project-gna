"""
Script principal : démonstration et tests statistiques

Lance deux phases :
  1. demonstration_generateurs : affiche quelques octets de chaque générateur.
  2. execution_tests_statistiques : fait tourner les 4 tests statistiques
     (Shannon, chi-carré, KS, autocorrélation) sur 10 000 octets par générateur.
"""

import os

from generators.lcg import LCG
from generators.mersenne_twister import MersenneTwister
from generators.box_muller import BoxMullerGenerator
from generators.bbs import BbsGenerator
from generators.drbg import HmacDrbgGenerator
from generators.os_urandom import SystemGenerator
from generators.xor_nrbg import XorGenerator

from tests_statistiques.entropie_shannon import ShannonEntropyTest
from tests_statistiques.chi2 import Chi2Test
from tests_statistiques.autocorrelation import AutocorrelationTest
from tests_statistiques.ks_test import KsTest


def demonstration_generateurs():
    """
    Affiche 8 octets produits par chaque générateur du projet.

    Permet de vérifier rapidement que tous les générateurs fonctionnent
    et de comparer visuellement leurs sorties.
    """
    print("=" * 60)
    print("  DEMONSTRATION DES GENERATEURS")
    print("=" * 60)

    print(f"LCG (8 octets)       : {list(LCG(42).generate_bytes(8))}")
    print(f"MT19937 (8 octets)   : {list(MersenneTwister(42).generate_bytes(8))}")
    print(f"BBS (8 octets)       : {list(BbsGenerator(12345, 58067, 35323).generate_bytes(8))}")
    print(f"HMAC-DRBG (8 octets) : {list(HmacDrbgGenerator(os.urandom(32), os.urandom(16)).generate_bytes(8))}")
    print(f"os.urandom (8 octets): {list(SystemGenerator().generate_bytes(8))}")
    print(f"XOR LCG+MT (8 oct)   : {list(XorGenerator([LCG(1), MersenneTwister(7)]).generate_bytes(8))}")

    # Box-Muller : on utilise MT comme source de nombres uniformes
    mt_source = MersenneTwister(123)
    gen_bm = BoxMullerGenerator(mt_source.next_float)
    normales = gen_bm.generate(5)
    valeurs_arrondies = [round(x, 4) for x in normales]
    print(f"Box-Muller (5 val)   : {valeurs_arrondies}")


def execution_tests_statistiques(n_octets: int = 10000):
    """
    Exécute les 4 tests statistiques sur chaque générateur.

    Génère n_octets octets par générateur, puis calcule l'entropie de Shannon,
    le chi-carré, le test KS et l'autocorrélation (lags 1, 2, 8).

    Args:
        n_octets (int): taille de l'échantillon par générateur (défaut : 10 000).
    """
    print("\n" + "=" * 60)
    print(f"  TESTS STATISTIQUES ({n_octets} octets)")
    print("=" * 60)

    echantillons = {
        "LCG"        : LCG(42).generate_bytes(n_octets),
        "MT19937"    : MersenneTwister(42).generate_bytes(n_octets),
        "BBS"        : BbsGenerator(12345, 3334888603, 3996958799).generate_bytes(n_octets),
        "HMAC-DRBG"  : HmacDrbgGenerator(os.urandom(32), os.urandom(16)).generate_bytes(n_octets),
        "os.urandom" : SystemGenerator().generate_bytes(n_octets),
        "XOR(LCG+MT)": XorGenerator([LCG(1), MersenneTwister(7)]).generate_bytes(n_octets),
    }

    test_shannon  = ShannonEntropyTest()
    test_chi2     = Chi2Test()
    test_ks       = KsTest()
    test_autocorr = AutocorrelationTest()

    for nom, donnees in echantillons.items():
        print(f"\n--- {nom} ---")

        entropie = test_shannon.run(donnees)
        print(f"  Entropie Shannon : {entropie:.6f}  (attendu ~8.0)")

        stat, p, verdict = test_chi2.run(donnees)
        print(f"  Chi-carre        : stat={stat:>8.2f}, p={p:.4f} -> {verdict}")

        stat, p, verdict = test_ks.run(donnees)
        print(f"  Kolmogorov-Smir. : stat={stat:.4f},   p={p:.4f} -> {verdict}")

        autocorr = test_autocorr.run(donnees, lags=[1, 2, 8])
        ligne = "  ".join(f"lag={lag}: {val:+.4f}" for lag, val in autocorr.items())
        print(f"  Autocorrelation  : {ligne}")


if __name__ == "__main__":
    demonstration_generateurs()
    execution_tests_statistiques()
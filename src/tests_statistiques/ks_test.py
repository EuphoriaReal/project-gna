"""
Test de Kolmogorov-Smirnov

On compare la distribution empirique des octets à une uniforme sur [0, 255].
D = écart maximal entre la CDF empirique et la CDF théorique.
Plus D est petit, plus la distribution est uniforme.

La p-value est calculée avec l'approximation asymptotique de Kolmogorov,
convergence rapide en pratique (moins de 20 termes en général).
"""

import math


class KsTest:

    def _kolmogorov_pvalue(self, stat: float, n: int) -> float:
        """
        Calcule la p-value via la formule asymptotique de Kolmogorov.
        λ = (√n + 0.12 + 0.11/√n) * D, puis on somme la série alternée.

        Args:
            stat (float): statistique D.
            n    (int)  : nombre d'observations.

        Returns:
            float: p-value dans [0.0, 1.0].
        """
        lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * stat
        if lam == 0:
            return 1.0
        somme = 0.0
        for k in range(1, 100):
            terme = (-1) ** (k + 1) * math.exp(-2 * k * k * lam * lam)
            somme += terme
            if abs(terme) < 1e-15:  # convergence atteinte
                break
        return max(0.0, min(1.0, 2 * somme))

    def run(self, donnees: bytes) -> tuple[float, float, str]:
        """
        Trie les valeurs normalisées et mesure l'écart max des deux côtés
        de chaque point par rapport à la diagonale (CDF de l'uniforme).

        Args:
            donnees (bytes): séquence d'octets à analyser.

        Returns:
            tuple[float, float, str]: (statistique D, p-value, verdict).
                PASS si p-value > 0.01, FAIL sinon.
        """
        n = len(donnees)
        if n == 0:
            return 0.0, 1.0, "PASS"

        valeurs = sorted(octet / 255.0 for octet in donnees)
        d_plus, d_moins = 0.0, 0.0

        for i in range(n):
            v = valeurs[i]
            d_plus  = max(d_plus,  (i + 1) / n - v)
            d_moins = max(d_moins, v - i / n)

        stat = max(d_plus, d_moins)
        p_value = self._kolmogorov_pvalue(stat, n)
        verdict = "PASS" if p_value > 0.01 else "FAIL"

        return stat, p_value, verdict


def test_ks(donnees: bytes) -> tuple[float, float, str]:
    """
    Raccourci pour lancer le test sans instancier KsTest à la main.

    Args:
        donnees (bytes): séquence d'octets à analyser.

    Returns:
        tuple[float, float, str]: (statistique D, p-value, verdict).
    """
    return KsTest().run(donnees)
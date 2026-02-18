"""
ks_test.py — Test de Kolmogorov-Smirnov

Compare la distribution empirique des octets à une loi uniforme sur [0, 255].
La statistique D est la distance maximale entre la CDF empirique et la CDF
théorique. Plus D est petit, plus la distribution est uniforme.

La p-value est estimée par l'approximation asymptotique de Kolmogorov
(série alternée, convergence rapide pour n grand).
"""

import math


class KsTest:
    """
    Test de Kolmogorov-Smirnov contre une loi uniforme continue.

    Chaque octet est normalisé dans [0, 1] en le divisant par 255, puis la
    distance maximale entre la CDF empirique triée et la diagonale est calculée.
    La p-value est estimée par la formule asymptotique de Kolmogorov.
    """

    def _kolmogorov_pvalue(self, stat: float, n: int) -> float:
        """
        Approximation asymptotique de la p-value (Numerical Recipes).

        Calcule λ = (√n + 0.12 + 0.11/√n) · D puis somme la série alternée
        2 · Σ (-1)^(k+1) · exp(-2k²λ²). Converge en général en moins de
        20 termes.

        Args:
            stat (float): statistique D (distance maximale).
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
            if abs(terme) < 1e-15:
                break

        return max(0.0, min(1.0, 2 * somme))

    def run(self, donnees: bytes) -> tuple[float, float, str]:
        """
        Exécute le test KS sur la séquence d'octets.

        Args:
            donnees (bytes): séquence d'octets à analyser.

        Returns:
            tuple[float, float, str]: (statistique D, p-value, verdict).
                Le verdict vaut "PASS" si p-value > 0.01, "FAIL" sinon.
        """
        n = len(donnees)
        if n == 0:
            return 0.0, 1.0, "PASS"

        valeurs = sorted(octet / 255.0 for octet in donnees)

        d_plus = 0.0
        d_moins = 0.0

        for i in range(n):
            v = valeurs[i]
            d_plus  = max(d_plus,  (i + 1) / n - v)
            d_moins = max(d_moins, v - i / n)

        stat = max(d_plus, d_moins)
        p_value = self._kolmogorov_pvalue(stat, n)
        verdict = "PASS" if p_value > 0.01 else "FAIL"

        return stat, p_value, verdict


# Fonction wrapper
def test_ks(donnees: bytes) -> tuple[float, float, str]:
    test = KsTest()
    return test.run(donnees)
"""
chi2.py — Test du chi-carré pour l'uniformité des octets

Hypothèse nulle (H0) : la séquence est uniformément distribuée sur [0, 255].
Si la p-value est > 0.01 on ne rejette pas H0 (PASS), sinon la distribution
est significativement non uniforme (FAIL).

Pour df = 255 (grand), la statistique chi-carré est approximée par une loi
normale via le Z-score : Z = (X - df) / sqrt(2 * df).
"""

import math


class Chi2Test:
    """
    Test du chi-carré pour vérifier l'uniformité de la distribution des octets.

    Compte les occurrences de chaque valeur 0-255, calcule la statistique
    chi-carré par rapport à la fréquence attendue n/256, puis estime la
    p-value par approximation normale (valable pour df = 255 grand).
    """

    def _norm_cdf(self, x: float) -> float:
        """
        Fonction de répartition de la loi normale standard via math.erf.

        Args:
            x (float): quantile.

        Returns:
            float: probabilité P(X ≤ x).
        """
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _approx_p_value(self, stat: float, df: int) -> float:
        """
        Approxime la p-value du chi-carré par une loi normale (df grand).

        Utilise Z = (stat - df) / sqrt(2 * df) et retourne 1 - CDF(Z),
        ce qui correspond à un test unilatéral à droite.

        Args:
            stat (float): statistique chi-carré observée.
            df   (int)  : degrés de liberté (255 pour 256 catégories).

        Returns:
            float: p-value dans [0.0, 1.0].
        """
        if stat < 0:
            return 1.0
        z = (stat - df) / math.sqrt(2 * df)
        return 1.0 - self._norm_cdf(z)

    def run(self, donnees: bytes, alpha: float = 0.05) -> tuple[float, float, str]:
        """
        Exécute le test du chi-carré sur la séquence d'octets.

        Args:
            donnees (bytes) : séquence d'octets à analyser.
            alpha   (float) : seuil de signification (défaut : 0.05).
                              Valeurs courantes : 0.01 (strict), 0.05 (standard), 0.10 (souple).

        Returns:
            tuple[float, float, str]: (statistique, p-value, verdict).
                Le verdict vaut "PASS" si p-value > alpha, "FAIL" sinon.
        """
        n = len(donnees)
        if n == 0:
            return 0.0, 1.0, "FAIL"

        degres_liberte = 255
        attendu = n / 256.0

        frequences = [0] * 256
        for octet in donnees:
            frequences[octet] += 1

        stat = sum((compte - attendu) ** 2 / attendu for compte in frequences)

        p_value = self._approx_p_value(stat, degres_liberte)
        verdict = "PASS" if p_value > alpha else "FAIL"

        return stat, p_value, verdict


# Fonction wrapper
def test_chi2(donnees: bytes, alpha: float = 0.05) -> tuple[float, float, str]:
    test = Chi2Test()
    return test.run(donnees, alpha)
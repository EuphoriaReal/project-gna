"""
Test du chi-carré pour l'uniformité des octets

On vérifie que les 256 valeurs possibles apparaissent avec la même fréquence.
Avec 255 degrés de liberté on utilise une approximation normale pour la
p-value plutôt que les tables — suffisamment précis pour nos besoins.
PASS si p-value > alpha, FAIL sinon.
"""

import math


class Chi2Test:

    def _norm_cdf(self, x: float) -> float:
        """
        CDF de la loi normale standard, calculée via math.erf.

        Args:
            x (float): quantile.

        Returns:
            float: P(X <= x) pour X ~ N(0, 1).
        """
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _approx_p_value(self, stat: float, df: int) -> float:
        """
        Approximation normale de la p-value du chi-carré.
        On centre/réduit la stat : Z = (stat - df) / sqrt(2*df), puis on retourne 1 - CDF(Z).

        Args:
            stat (float): statistique chi-carré observée.
            df   (int)  : degrés de liberté.

        Returns:
            float: p-value dans [0.0, 1.0].
        """
        if stat < 0:
            return 1.0
        z = (stat - df) / math.sqrt(2 * df)
        return 1.0 - self._norm_cdf(z)

    def run(self, donnees: bytes, alpha: float = 0.05) -> tuple[float, float, str]:
        """
        Lance le test sur la séquence. Compare les fréquences observées
        à la fréquence théorique n/256.

        Args:
            donnees (bytes) : séquence d'octets à analyser.
            alpha   (float) : seuil de signification, 0.05 par défaut.

        Returns:
            tuple[float, float, str]: (statistique, p-value, verdict).
        """
        n = len(donnees)
        if n == 0:
            return 0.0, 1.0, "FAIL"

        attendu = n / 256.0
        frequences = [0] * 256
        for octet in donnees:
            frequences[octet] += 1

        stat = sum((compte - attendu) ** 2 / attendu for compte in frequences)
        p_value = self._approx_p_value(stat, 255)
        verdict = "PASS" if p_value > alpha else "FAIL"

        return stat, p_value, verdict


def test_chi2(donnees: bytes, alpha: float = 0.05) -> tuple[float, float, str]:
    """
    Raccourci pour lancer le test sans instancier Chi2Test à la main.

    Args:
        donnees (bytes) : séquence d'octets à analyser.
        alpha   (float) : seuil de signification.

    Returns:
        tuple[float, float, str]: (statistique, p-value, verdict).
    """
    return Chi2Test().run(donnees, alpha)
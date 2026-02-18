"""
Autocorrélation d'une séquence d'octets

Mesure la corrélation linéaire entre les valeurs séparées par un décalage (lag).
Un bon générateur doit donner des valeurs proches de 0 pour tout lag > 0.
"""


class AutocorrelationTest:
    """
    Calcule le coefficient d'autocorrélation normalisé pour plusieurs lags.

    Le coefficient pour un lag k est défini comme la covariance entre
    (x_i) et (x_{i+k}) divisée par la variance globale. Il vaut 1 en
    cas de corrélation parfaite, 0 en l'absence de corrélation.
    """

    def run(self, donnees: bytes, lags: list[int] = [1, 2, 4, 8, 16]) -> dict[int, float]:
        """
        Calcule l'autocorrélation pour chaque lag demandé.

        Args:
            donnees (bytes)    : séquence d'octets à analyser.
            lags    (list[int]): liste des décalages à tester.

        Returns:
            dict[int, float]: dictionnaire {lag: coefficient} avec des
                              valeurs dans [-1.0, 1.0]. Retourne 0.0 pour
                              les lags >= len(donnees) ou si la variance est nulle.
        """
        n = len(donnees)

        if n < 2:
            return {lag: 0.0 for lag in lags}

        valeurs = [float(octet) for octet in donnees]
        moyenne = sum(valeurs) / n

        variance = sum((v - moyenne) ** 2 for v in valeurs) / n

        if variance == 0:
            return {lag: 0.0 for lag in lags}

        resultats = {}
        for lag in lags:
            if lag >= n:
                resultats[lag] = 0.0
                continue

            s = 0.0
            for i in range(n - lag):
                s += (valeurs[i] - moyenne) * (valeurs[i + lag] - moyenne)

            covariance = s / (n - lag)
            resultats[lag] = covariance / variance

        return resultats


def autocorrelation(donnees: bytes, lags: list[int] = [1, 2, 4, 8, 16]) -> dict[int, float]:
    test = AutocorrelationTest()
    return test.run(donnees, lags)
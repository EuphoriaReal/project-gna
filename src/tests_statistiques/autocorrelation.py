"""
Autocorrélation d'une séquence d'octets

On mesure si les valeurs sont liées à leurs voisines décalées de k positions.
Un bon générateur doit donner des coefficients proches de 0 pour tout lag > 0.
Un LCG par exemple présente souvent une corrélation à lag=1 à cause de sa
structure linéaire.

Coefficient = covariance(x_i, x_{i+k}) / variance globale.
"""


class AutocorrelationTest:

    def run(self, donnees: bytes, lags: list[int] = [1, 2, 4, 8, 16]) -> dict[int, float]:
        """
        Calcule l'autocorrélation pour chaque lag. Pour un lag k, on compare
        les n-k paires (x_i, x_{i+k}) et on normalise par la variance globale.
        Retourne 0.0 si le lag est trop grand ou si la séquence est constante.

        Args:
            donnees (bytes)    : séquence d'octets à analyser.
            lags    (list[int]): liste des décalages à tester.

        Returns:
            dict[int, float]: {lag: coefficient} avec des valeurs dans [-1.0, 1.0].
        """
        n = len(donnees)
        if n < 2:
            return {lag: 0.0 for lag in lags}

        valeurs = [float(octet) for octet in donnees]
        moyenne = sum(valeurs) / n
        variance = sum((v - moyenne) ** 2 for v in valeurs) / n

        if variance == 0:
            # séquence constante, aucune corrélation n'a de sens
            return {lag: 0.0 for lag in lags}

        resultats = {}
        for lag in lags:
            if lag >= n:
                resultats[lag] = 0.0
                continue
            s = sum(
                (valeurs[i] - moyenne) * (valeurs[i + lag] - moyenne)
                for i in range(n - lag)
            )
            resultats[lag] = (s / (n - lag)) / variance

        return resultats


def autocorrelation(donnees: bytes, lags: list[int] = [1, 2, 4, 8, 16]) -> dict[int, float]:
    """
    Calcul l'autocorrélation.

    Args:
        donnees (bytes)    : séquence d'octets à analyser.
        lags    (list[int]): liste des décalages à tester.

    Returns:
        dict[int, float]: {lag: coefficient} avec des valeurs dans [-1.0, 1.0].
    """
    return AutocorrelationTest().run(donnees, lags)
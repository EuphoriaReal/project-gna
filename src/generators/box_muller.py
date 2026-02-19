"""
Transformée de Box-Muller

Permet de produire des nombres suivant N(0,1) à partir d'uniformes.
Forme basique :
  u0, u1 dans (0,1]
  z0 = sqrt(-2*ln(u0)) * cos(2*pi*u1)
  z1 = sqrt(-2*ln(u0)) * sin(2*pi*u1)

On utilise la forme polaire (Marsaglia) qui évite les appels cos/sin :
  on tire des points (u, v) dans le carré [-1,1]^2 jusqu'à tomber dans le cercle,
  puis on utilise la distance au centre comme facteur d'échelle.
"""

import math
import random


class BoxMullerGenerator:
    """
    Générateur normal via Box-Muller polaire.

    La méthode polaire génère deux normales indépendantes à la fois.
    La seconde est mise en réserve pour éviter de refaire un calcul
    au prochain appel.

    La qualité des normales produites dépend entièrement de la source
    uniforme passée en paramètre : avec un LCG la sortie sera moins qu'avec un ,
    avec os.urandom.

    Args:
        source_uniforme (callable | None): fonction () -> float dans [0, 1).
            Par défaut random.random, mais on peut passer lcg.next_float,
            mt.next_float, etc.
    """

    def __init__(self, source_uniforme=None):
        self.source = source_uniforme or random.random
        self._reserve = None  # on genere deux valeurs a la fois, on stocke la seconde

    def next(self) -> float:
        """
        Retourne la prochaine valeur normale N(0, 1).

        Consomme la réserve si elle existe, sinon génère une nouvelle paire
        par la méthode polaire et met la seconde valeur de côté.

        Returns:
            float: valeur suivant N(0, 1).
        """
        if self._reserve is not None:
            val = self._reserve
            self._reserve = None
            return val

        # Methode polaire : on rejette les points hors du cercle unite
        while True:
            u = 2.0 * self.source() - 1.0
            v = 2.0 * self.source() - 1.0
            s = u*u + v*v
            if 0.0 < s < 1.0:
                break

        coeff = math.sqrt(-2.0 * math.log(s) / s)
        self._reserve = v * coeff
        return u * coeff

    def generate(self, n: int, mu: float = 0.0, sigma: float = 1.0) -> list[float]:
        """
        Génère n valeurs suivant N(mu, sigma).

        Applique simplement z_final = mu + sigma * z avec z ~ N(0, 1).

        Args:
            n     (int)  : nombre de valeurs voulues.
            mu    (float): espérance de la loi cible.
            sigma (float): écart-type de la loi cible.

        Returns:
            list[float]: n valeurs issues de N(mu, sigma).
        """
        resultats = []
        for i in range(n):
            resultats.append(mu + self.next() * sigma)
        return resultats


def box_muller_basique(u0: float, u1: float) -> tuple[float, float]:
    """
    Forme trigonométrique originale de Box-Muller (1958).

    Transforme deux uniformes indépendants en deux normales N(0, 1).
    Moins efficace que la forme polaire à cause des appels cos/sin.

    Args:
        u0 (float): premier uniforme dans (0, 1].
        u1 (float): second uniforme dans (0, 1].

    Returns:
        tuple[float, float]: deux valeurs indépendantes suivant N(0, 1).
    """
    r = math.sqrt(-2.0 * math.log(u0))
    z0 = r * math.cos(2.0 * math.pi * u1)
    z1 = r * math.sin(2.0 * math.pi * u1)
    return z0, z1


if __name__ == "__main__":
    bm = BoxMullerGenerator() 
    print("normales (10) :", bm.generate(10))
    print("N(5, 2)   (5) :", bm.generate(5, mu=5.0, sigma=2.0))
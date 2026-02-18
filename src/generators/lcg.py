"""
Générateur Congruentiel Linéaire (LCG)

Formule : X_{n+1} = (a * X_n + c) mod m
Paramètres par défaut : ceux de la glibc (a=1103515245, c=12345, m=2^31).

C'est le générateur le plus simple qui soit. Il est rapide et suffit pour
des simulations, mais il est totalement prévisible et ne doit pas être utilisé pour la cryptographie.
"""


class LCG:
    """
    Implémentation du Linear Congruential Generator.

    L'état interne est un simple entier mis à jour à chaque appel.
    Avec les paramètres glibc, la période vaut 2^31.

    Args:
        graine (int): valeur initiale X_0.
        a      (int): multiplicateur.
        c      (int): incrément.
        m      (int): modulo.
    """

    def __init__(self, graine, a=1103515245, c=12345, m=2**31):
        self.etat = graine
        self.a = a
        self.c = c
        self.m = m

    def next(self) -> int:
        """
        Calcule le prochain entier de la suite.

        Returns:
            int: entier dans [0, m-1].
        """
        self.etat = (self.a * self.etat + self.c) % self.m
        return self.etat

    def next_float(self) -> float:
        """
        Retourne la prochaine valeur normalisée dans [0, 1).

        Returns:
            float: valeur dans [0.0, 1.0).
        """
        return self.next() / self.m

    def generate(self, n: int) -> list[int]:
        """
        Génère une liste de n entiers consécutifs.

        Args:
            n (int): nombre de valeurs voulues.

        Returns:
            list[int]: liste de n entiers dans [0, m-1].
        """
        resultats = []
        for i in range(n):
            resultats.append(self.next())
        return resultats

    def generate_bytes(self, n: int) -> bytes:
        """
        Génère n octets en gardant seulement les 8 bits de poids faible
        de chaque valeur produite.

        Args:
            n (int): nombre d'octets voulus.

        Returns:
            bytes: séquence de n octets.
        """
        octets = []
        for i in range(n):
            octets.append(self.next() & 0xFF)
        return bytes(octets)

if __name__ == "__main__":
    gen = LCG(12345)
    print("entiers  :", gen.generate(10))
    print("octets   :", list(LCG(12345).generate_bytes(10)))
    print("flottants:", LCG(12345).next_float())
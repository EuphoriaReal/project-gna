"""
Générateur Congruentiel Linéaire (LCG)

Formule : X_{n+1} = (a * X_n + c) mod m
On utilise les paramètres de la glibc, les mêmes que rand() en C.
Période de 2^31, état interne = un seul entier, totalement prévisible.
"""


class LCG:
    """
    LCG avec les paramètres glibc par défaut. On peut en passer d'autres à l'instanciation.

    Args:
        graine (int): valeur de départ X_0.
        a      (int): multiplicateur.
        c      (int): incrément.
        m      (int): modulo, détermine la période maximale.
    """

    def __init__(self, graine, a=1103515245, c=12345, m=2**31):
        self.etat = graine
        self.a = a
        self.c = c
        self.m = m

    def next(self) -> int:
        """
        Un pas de la formule, met à jour l'état et retourne la nouvelle valeur.

        Returns:
            int: entier dans [0, m-1].
        """
        self.etat = (self.a * self.etat + self.c) % self.m
        return self.etat

    def next_float(self) -> float:
        """
        Même chose mais normalisé dans [0, 1), utile pour alimenter Box-Muller.

        Returns:
            float: valeur dans [0.0, 1.0).
        """
        return self.next() / self.m

    def generate(self, n: int) -> list[int]:
        """
        Appelle next() n fois et retourne les résultats dans une liste.

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
        Génère n octets en gardant les 8 bits de poids faible de chaque valeur.
        Ces bits ont une période encore plus courte que le reste, point le plus faible du LCG.

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
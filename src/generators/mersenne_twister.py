"""
Mersenne Twister MT19937

Période : 2^19937 - 1. État interne : 624 mots de 32 bits.
C'est le générateur par défaut de Python, R, Ruby entre autres.

Statistiquement très bon (passe Diehard, BigCrush…), mais pas
cryptographique : 624 sorties 32-bits consécutives suffisent à
reconstruire l'état complet et prédire toute la suite.
"""


class MersenneTwister:
    """
    Implémentation pure Python du MT19937.

    Le tableau d'état (624 mots) est régénéré par l'opération de twist
    dès qu'il est épuisé. Une étape de tempering est appliquée à chaque
    sortie pour améliorer la distribution, mais elle est réversible
    ce qui rend l'attaque de reconstruction d'état possible.

    Args:
        graine (int): valeur initiale pour l'algorithme d'initialisation de Knuth.
    """

    # Constantes MT19937
    N           = 624         # taille du tableau d'état (nombre de mots 32-bits)
    M           = 397         # décalage de récurrence dans le twist
    MATRIX_A    = 0x9908B0DF  # vecteur de la matrice rationnelle normale A
    UPPER_MASK  = 0x80000000  # masque du bit de poids fort
    LOWER_MASK  = 0x7FFFFFFF  # masque des 31 bits de poids faible
    INIT_CONST  = 0x6C078965  # constante de Knuth pour l'initialisation (1812433253)
    WORD_MASK   = 0xFFFFFFFF  # masque 32-bits
    TEMPERING_B = 0x9D2C5680  # masque tempering shift left 7
    TEMPERING_C = 0xEFC60000  # masque tempering shift left 15

    def __init__(self, graine):
        self.graine = graine
        self.etat = [0] * self.N
        self.index = self.N
        self._init_etat(graine)

    def _init_etat(self, graine):
        """
        Remplit le tableau d'état à partir de la graine (initialisation Knuth).

        Chaque mot est dérivé du précédent via la constante 1812433253,
        ce qui diffuse la graine sur les 624 mots.

        Args:
            graine (int): valeur de départ.
        """
        self.etat[0] = graine & self.WORD_MASK
        for i in range(1, self.N):
            # Constante de Knuth, chaque mot depend du precedent
            self.etat[i] = (self.INIT_CONST * (self.etat[i-1] ^ (self.etat[i-1] >> 30)) + i) & self.WORD_MASK

    def _twist(self):
        """
        Régénère les 624 mots de l'état via la matrice rationnelle normale.

        Appelée automatiquement quand l'index atteint N. Remet l'index à 0.
        """
        for i in range(self.N):
            y = (self.etat[i] & self.UPPER_MASK) | (self.etat[(i + 1) % self.N] & self.LOWER_MASK)
            self.etat[i] = self.etat[(i + self.M) % self.N] ^ (y >> 1)
            if y % 2 != 0:
                self.etat[i] ^= self.MATRIX_A
        self.index = 0

    def _tempering(self, y) -> int:
        """
        Applique la transformation de tempering sur un mot 32-bits.

        Améliore l'équidistribution des sorties brutes du tableau.
        Cette transformation est entièrement réversible, ce qui est
        l'une des raisons pour lesquelles le MT n'est pas cryptographique.

        Args:
            y (int): mot 32-bits issu du tableau d'état.

        Returns:
            int: mot transformé dans [0, 2^32 - 1].
        """
        # Transformation pour ameliorer la distribution des sorties
        y ^= (y >> 11)
        y ^= (y << 7)  & self.TEMPERING_B
        y ^= (y << 15) & self.TEMPERING_C
        y ^= (y >> 18)
        return y & self.WORD_MASK

    def next(self) -> int:
        """
        Retourne le prochain entier 32-bits et avance l'index d'un cran.

        Déclenche un twist si tous les mots ont déjà été consommés.

        Returns:
            int: entier dans [0, 2^32 - 1].
        """
        if self.index >= self.N:
            self._twist()
        y = self.etat[self.index]
        self.index += 1
        return self._tempering(y)

    def generate(self, n: int) -> list[int]:
        """
        Génère une liste de n entiers 32-bits.

        Args:
            n (int): nombre de valeurs voulues.

        Returns:
            list[int]: liste de n entiers dans [0, 2^32 - 1].
        """
        resultats = []
        for _ in range(n):
            resultats.append(self.next())
        return resultats

    def generate_bytes(self, n: int) -> bytes:
        """
        Génère n octets en gardant l'octet de poids faible de chaque sortie.

        Args:
            n (int): nombre d'octets voulus.

        Returns:
            bytes: séquence de n octets.
        """
        octets = []
        for i in range(n):
            octets.append(self.next() & 0xFF)
        return bytes(octets)

    def next_float(self) -> float:
        """
        Retourne le prochain flottant dans [0, 1).

        Returns:
            float: valeur dans [0.0, 1.0).
        """
        return self.next() / 2**32

if __name__ == "__main__":
    gen = MersenneTwister(12345)
    print("entiers :", gen.generate(10))
    print("octets  :", list(MersenneTwister(12345).generate_bytes(10)))
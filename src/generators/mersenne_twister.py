"""
Mersenne Twister MT19937

Période 2^19937 - 1, état interne = 624 mots de 32 bits.
On peut noté que avec 624 sorties consécutives on peut reconstruire l'état complet et
prédire toute la suite.
"""


class MersenneTwister:
    """
    Implémentation du MT19937.

    L'état interne est un tableau de 624 mots de 32 bits. Quand tous
    les mots ont été consommés, le tableau est régénéré par l'opération
    de twist. Une étape de tempering est appliquée à chaque sortie pour
    améliorer la distribution mais cette étape est réversible, ce qui
    est précisément ce qui rend l'attaque de reconstruction d'état possible.

    Args:
        graine (int): valeur initiale.
    """

    # Constantes MT19937 définies par la spec
    N           = 624         # taille du tableau d'état (mots de 32 bits)
    M           = 397         # décalage utilisé dans le twist
    MATRIX_A    = 0x9908B0DF  # vecteur de la matrice rationnelle normale A
    UPPER_MASK  = 0x80000000  # bit de poids fort
    LOWER_MASK  = 0x7FFFFFFF  # les 31 bits restants
    INIT_CONST  = 0x6C078965  # constante de Knuth (1812433253) pour l'init
    WORD_MASK   = 0xFFFFFFFF  # masque pour rester sur 32 bits
    TEMPERING_B = 0x9D2C5680  # masque pour le tempering (shift left 7)
    TEMPERING_C = 0xEFC60000  # masque pour le tempering (shift left 15)

    def __init__(self, graine):
        self.graine = graine
        self.etat = [0] * self.N
        self.index = self.N
        self._init_etat(graine)

    def _init_etat(self, graine):
        """
        Remplit le tableau d'état à partir de la graine.

        Chaque mot est calculé à partir du précédent en utilisant la
        constante de Knuth 1812433253. Ça diffuse la graine sur les 624
        positions même si elle est petite.

        Args:
            graine (int): valeur de départ.
        """
        self.etat[0] = graine & self.WORD_MASK
        for i in range(1, self.N):
            self.etat[i] = (
                self.INIT_CONST * (self.etat[i-1] ^ (self.etat[i-1] >> 30)) + i
            ) & self.WORD_MASK

    def _twist(self):
        """
        Régénère les 624 mots de l'état.

        Appelée automatiquement dès que l'index atteint N, c'est-à-dire
        quand tous les mots du tableau ont été consommés. Remet l'index à 0.
        """
        for i in range(self.N):
            y = (self.etat[i] & self.UPPER_MASK) | (self.etat[(i + 1) % self.N] & self.LOWER_MASK)
            self.etat[i] = self.etat[(i + self.M) % self.N] ^ (y >> 1)
            if y % 2 != 0:
                self.etat[i] ^= self.MATRIX_A
        self.index = 0

    def _tempering(self, y) -> int:
        """
        Transformation appliquée à chaque mot avant de le retourner.

        Améliore la distribution des sorties brutes du tableau (qui serait
        trop régulière sinon).

        Args:
            y (int): mot 32 bits issu du tableau d'état.

        Returns:
            int: mot transformé, toujours dans [0, 2^32 - 1].
        """
        y ^= (y >> 11)
        y ^= (y << 7)  & self.TEMPERING_B
        y ^= (y << 15) & self.TEMPERING_C
        y ^= (y >> 18)
        return y & self.WORD_MASK

    def next(self) -> int:
        """
        Retourne le prochain entier 32 bits.

        Déclenche un twist si le tableau est épuisé, sinon avance
        simplement l'index d'une position.

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
        Génère n entiers 32 bits d'un coup.

        Args:
            n (int): nombre de valeurs voulues.

        Returns:
            list[int]: liste de n entiers dans [0, 2^32 - 1].
        """
        resultats = []
        for i in range(n):
            resultats.append(self.next())
        return resultats

    def generate_bytes(self, n: int) -> bytes:
        """
        Génère n octets en gardant seulement le dernier octet de chaque
        sortie 32 bits. Simple et suffisant pour nos comparaisons.

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
        Retourne la prochaine valeur dans [0, 1).

        Returns:
            float: valeur dans [0.0, 1.0).
        """
        return self.next() / 2**32

if __name__ == "__main__":
    gen = MersenneTwister(12345)
    print("entiers :", gen.generate(10))
    print("octets  :", list(MersenneTwister(12345).generate_bytes(10)))
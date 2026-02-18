"""
bbs.py — Générateur Blum-Blum-Shub (BBS)

Principe :
  - On choisit deux grands premiers p et q congrus à 3 mod 4 ("premiers de Blum")
  - On calcule n = p * q
  - On part de X0 = graine^2 mod n
  - À chaque itération : X_{n+1} = X_n^2 mod n
  - On extrait le bit de poids faible de chaque X_n

Sa sécurité repose sur la difficulté de factoriser n : sans connaître p et q,
il est impossible de prédire les bits suivants. C'est l'un des rares PRNG
avec une preuve de sécurité formelle. En contrepartie il est très lent :
un seul bit utile par itération (carré modulaire).
"""

try:
    from generators.mersenne_twister import MersenneTwister
except ImportError:
    from mersenne_twister import MersenneTwister


def isprime(n: int) -> bool:
    """
    Teste si n est un nombre premier par division trial jusqu'à √n.

    Args:
        n (int): entier à tester.

    Returns:
        bool: True si n est premier, False sinon.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def is_blum_prime(n: int) -> bool:
    """
    Vérifie qu'un entier est un premier de Blum (premier et congru à 3 mod 4).

    Les premiers de Blum sont nécessaires pour que la séquence BBS ait
    une période maximale et que la sécurité soit garantie.

    Args:
        n (int): entier à tester.

    Returns:
        bool: True si n est premier et n % 4 == 3, False sinon.
    """
    return isprime(n) and n % 4 == 3


def generate_blum_prime(bits: int = 10, graine: int = 42) -> int:
    """
    Génère un premier de Blum aléatoire via le Mersenne Twister.

    Utilise le MT pour produire des candidats impairs dans l'intervalle
    [2^(bits-1), 2^bits - 1] et les teste jusqu'à en trouver un qui soit
    un premier de Blum.

    Args:
        bits   (int): taille souhaitée en bits du premier généré.
        graine (int): graine pour le Mersenne Twister.

    Returns:
        int: un premier de Blum à `bits` bits.
    """
    mt = MersenneTwister(graine)
    lo = 2 ** (bits - 1)
    hi = 2 ** bits - 1
    while True:
        candidat = lo + (mt.next() % (hi - lo + 1))
        candidat |= 1  # on force l'imparité
        if is_blum_prime(candidat):
            return candidat

class BbsGenerator:
    """
    Générateur Blum-Blum-Shub (BBS).

    L'état interne est un entier X mis à jour par X ← X² mod n à chaque
    appel. Seul le bit de poids faible de X est extrait, ce qui garantit
    qu'observer les sorties ne permet pas de remonter à X (sous hypothèse
    de difficulté de factorisation de n).

    Args:
        graine (int): valeur initiale, doit être première avec n.
        p      (int): premier de Blum (p ≡ 3 mod 4).
        q      (int): premier de Blum (q ≡ 3 mod 4).
    """

    def __init__(self, graine, p, q):
        if not is_blum_prime(p):
            raise ValueError(f"{p} n'est pas un premier de Blum")
        if not is_blum_prime(q):
            raise ValueError(f"{q} n'est pas un premier de Blum")
        
        self.n = p * q
        # etat initial : X0 = graine^2 mod n
        self.etat = (graine * graine) % self.n

    def next_bit(self) -> int:
        """
        Génère le prochain bit en avançant l'état d'un pas.

        Applique X ← X² mod n et retourne le bit de poids faible.

        Returns:
            int: 0 ou 1.
        """
        # Xn+1 = Xn^2 mod n
        self.etat = (self.etat * self.etat) % self.n
        # on prend le bit de poids faible
        return self.etat & 1

    def next_byte(self) -> int:
        """
        Génère un octet en appelant next_bit huit fois.

        Les bits sont empilés du plus significatif au moins significatif.

        Returns:
            int: entier dans [0, 255].
        """
        val = 0
        for i in range(8):
            val = (val << 1) | self.next_bit()
        return val

    def generate_bits(self, nb_bits: int) -> list[int]:
        """
        Génère une liste de bits consécutifs.

        Args:
            nb_bits (int): nombre de bits voulus.

        Returns:
            list[int]: liste de nb_bits entiers valant 0 ou 1.
        """
        return [self.next_bit() for _ in range(nb_bits)]

    def generate_bytes(self, nb_octets: int) -> bytes:
        """
        Génère nb_octets sous forme d'objet bytes.

        Args:
            nb_octets (int): nombre d'octets voulus.

        Returns:
            bytes: séquence de nb_octets octets.
        """
        octets = []
        for i in range(nb_octets):
            octets.append(self.next_byte())
        return bytes(octets)


# Fonctions de test
def bbs_bits(graine, nb_bits, p=383, q=503):
    gen = BbsGenerator(graine, p, q)
    return gen.generate_bits(nb_bits)

def bbs_octets(graine, nb_octets, p=383, q=503):
    gen = BbsGenerator(graine, p, q)
    return gen.generate_bytes(nb_octets)


if __name__ == "__main__":
    # Génération de vrais premiers de Blum via le MT
    print("Recherche de premiers de Blum...")
    p = generate_blum_prime(bits=64, graine=1234)
    q = generate_blum_prime(bits=64, graine=5678)
    print(f"  p = {p}  (premier de Blum : {is_blum_prime(p)}, p mod 4 = {p % 4})")
    print(f"  q = {q}  (premier de Blum : {is_blum_prime(q)}, q mod 4 = {q % 4})")
    print(f"  n = p * q = {p * q}")

    graine = 12345
    gen = BbsGenerator(graine, p, q)
    print("\nBBS bits (16)  :", gen.generate_bits(16))

    gen = BbsGenerator(graine, p, q)
    print("BBS octets (4) :", list(gen.generate_bytes(4)))
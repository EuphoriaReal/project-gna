"""
Construction XOR NRBG

On combine plusieurs générateurs par XOR octet à octet.
Propriété utile : si au moins UNE source est imprévisible,
le résultat l'est aussi -> robustesse face à la défaillance partielle.
"""


class XorGenerator:
    """
    Combineur XOR de plusieurs générateurs d'octets.

    Prend une liste de générateurs exposant chacun generate_bytes(n)
    et produit la combinaison XOR octet par octet de leurs sorties.

    La sécurité du résultat est aussi bonne que celle du meilleur
    générateur de la liste : une seule source sûre suffit, même si
    toutes les autres sont compromises.

    Args:
        generateurs (list): liste non vide de générateurs exposant
                            chacun la méthode generate_bytes(n) -> bytes.

    Raises:
        ValueError: si la liste est vide.
    """

    def __init__(self, generateurs):
        if not generateurs:
            raise ValueError("Au moins un generateur est requis")
        self.generateurs = generateurs

    def generate_bytes(self, n: int) -> bytes:
        """
        Génère n octets en XOR-ant les sorties de tous les générateurs.

        Le premier générateur initialise le tampon, les suivants sont
        XOR-és dans l'ordre de la liste.

        Args:
            n (int): nombre d'octets voulus.

        Returns:
            bytes: séquence de n octets issus du XOR de toutes les sources.
        """
        resultat = bytearray(self.generateurs[0].generate_bytes(n))

        for gen in self.generateurs[1:]:
            octets = gen.generate_bytes(n)
            for i in range(n):
                resultat[i] ^= octets[i]

        return bytes(resultat)


if __name__ == "__main__":
    from lcg import LCG
    from mersenne_twister import MersenneTwister
    from os_urandom import SystemGenerator

    gen = XorGenerator([LCG(12345), MersenneTwister(12345), SystemGenerator()])
    print("XOR (16 octets) :", list(gen.generate_bytes(16)))
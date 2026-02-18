"""
Générateur système (os.urandom)

Fait appel directement au système d'exploitation (/dev/urandom sur Linux).
Considéré cryptographiquement sûr en pratique -> référence pour nos comparaisons.
Pas de graine, pas d'état reproductible.
"""

import os


class SystemGenerator:
    """
    Interface unifiée avec les autres générateurs du projet.

    Pas d'état interne exposé. Les méthodes délèguent directement à
    os.urandom pour rester comparables aux autres classes du projet.
    """

    def generate_bytes(self, n: int) -> bytes:
        """
        Retourne n octets aléatoires fournis par l'OS.

        Args:
            n (int): nombre d'octets voulus.

        Returns:
            bytes: séquence de n octets cryptographiquement sûrs.
        """
        return os.urandom(n)

    def generate(self, n: int, n_bytes: int = 4) -> list[int]:
        """
        Génère une liste de n entiers non signés à partir d'os.urandom.

        Args:
            n       (int): nombre de valeurs voulues.
            n_bytes (int): largeur de chaque entier en octets (défaut : 4).

        Returns:
            list[int]: liste de n entiers dans [0, 2^(8*n_bytes) - 1].
        """
        resultats = []
        for i in range(n):
            octets = os.urandom(n_bytes)
            resultats.append(int.from_bytes(octets, 'big'))
        return resultats


if __name__ == "__main__":
    gen = SystemGenerator()
    print("16 octets :", list(gen.generate_bytes(16)))
    print("3 entiers :", gen.generate(3))
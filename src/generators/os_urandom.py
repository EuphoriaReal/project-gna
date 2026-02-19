"""
Générateur système (os.urandom)

On délègue directement au noyau, qui collecte de l'entropie depuis le
matériel (/dev/urandom sous Linux).
"""

import os


class SystemGenerator:
    """
    Générateur d'octets basé sur os.urandom.

    - La sécurité dépend de la qualité de l'entropie collectée par le noyau,
    qui est généralement très bonne sur les systèmes modernes.
    """

    def generate_bytes(self, n: int) -> bytes:
        """Génère n octets en appelant os.urandom(n)."""
        return os.urandom(n)

    def generate(self, n: int, n_bytes: int = 4) -> list[int]:
        """Génère n entiers, chacun construit depuis n_bytes octets bruts en big-endian."""
        resultats = []
        for i in range(n):
            octets = os.urandom(n_bytes)
            resultats.append(int.from_bytes(octets, 'big'))
        return resultats


if __name__ == "__main__":
    gen = SystemGenerator()
    print("16 octets :", list(gen.generate_bytes(16)))
    print("3 entiers :", gen.generate(3))
"""
Entropie de Shannon par octet

H = -sum(pi * log2(pi)), maximum théorique = 8.0 bits/octet.

Plus H est proche de 8.0, plus la distribution des octets est uniforme
et la séquence imprévisible.
"""

import math


class ShannonEntropyTest:
    """
    Mesure la quantité d'information moyenne contenue dans la séquence.

    Calcule les fréquences de chaque octet (0-255) puis applique la formule
    de Shannon. Une source parfaitement uniforme sur 256 symboles donne H = 8.0.
    """

    def run(self, donnees: bytes) -> float:
        """
        Calcule l'entropie de Shannon sur la séquence d'octets.

        Args:
            donnees (bytes): séquence d'octets à analyser.

        Returns:
            float: entropie en bits/octet, dans [0.0, 8.0].
        """
        n = len(donnees)
        if n == 0:
            return 0.0

        frequences = [0] * 256
        for octet in donnees:
            frequences[octet] += 1

        entropie = 0.0
        for compteur in frequences:
            if compteur > 0:
                proba = compteur / n
                entropie -= proba * math.log2(proba)

        return entropie

def entropie_shannon(donnees: bytes) -> float:
    test = ShannonEntropyTest()
    return test.run(donnees)
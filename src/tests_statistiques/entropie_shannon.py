"""
Entropie de Shannon par octet

H = -Σ p_i · log2(p_i), maximum théorique pour 256 symboles : 8.0 bits/octet.

Plus H est proche de 8.0, plus chaque octet est surprenant en moyenne,
c'est-à-dire plus la distribution est proche de l'uniforme.
Un générateur biaisé (par exemple qui surreprésente certaines valeurs)
aura une entropie notablement inférieure à 8.
"""

import math

class ShannonEntropyTest:
    """
    Mesure la quantité d'information moyenne contenue dans la séquence.

    Compte les occurrences de chaque octet (0-255), en déduit les
    probabilités empiriques et applique la formule de Shannon.
    """

    def run(self, donnees: bytes) -> float:
        """
        Calcule l'entropie de Shannon de la séquence.

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
    """
    Calcul l'entropie.

    Args:
        donnees (bytes): séquence d'octets à analyser.

    Returns:
        float: entropie en bits/octet dans [0.0, 8.0].
    """
    return ShannonEntropyTest().run(donnees)
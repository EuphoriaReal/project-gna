"""
drbg.py — HMAC-DRBG (NIST SP 800-90A)

CSPRNG déterministe basé sur HMAC-SHA256.
État interne : deux variables K (clé) et V (valeur) de 32 octets chacune.

Fonctionnement :
  1. Init    : K = 0x00...0, V = 0x01...1
  2. Seeding : K et V sont mis à jour avec l'entropie + nonce fournis
  3. Génération : on applique HMAC(K, V) en boucle pour produire les octets,
     puis on met à jour K et V (forward secrecy : on ne peut pas
     remonter aux sorties précédentes même en volant l'état)
"""

import hmac
import hashlib

class HmacDrbgGenerator:
    """
    Générateur HMAC-DRBG conforme NIST SP 800-90A.

    L'entropie initiale et le nonce est absorbée via _update
    lors de la construction. Chaque appel à generate_bytes met à jour K
    et V en fin de génération pour garantir la forward secrecy.

    Args:
        entropie (bytes): source d'entropie initiale.
        nonce    (bytes): valeur unique par instanciation.
    """

    def __init__(self, entropie, nonce):
        self.K = b"\x00" * 32
        self.V = b"\x01" * 32
        self._update(entropie + nonce)

    def _hmac(self, donnees: bytes) -> bytes:
        """
        Calcule HMAC-SHA256(self.K, donnees).

        Args:
            donnees (bytes): message à authentifier.

        Returns:
            bytes: condensé de 32 octets.
        """
        return hmac.new(self.K, donnees, hashlib.sha256).digest()

    def _update(self, donnees: bytes = b""):
        """
        Met à jour K et V selon la procédure du NIST SP 800-90A.

        Si donnees est non vide (seeding ou reseed), deux passes HMAC sont
        effectuées pour bien diffuser l'entropie dans l'état. Une seule
        passe est faite en post-génération (donnees vide).

        Args:
            donnees (bytes): entropie ou personnalisation à absorber dans l'état.
        """
        # Procedure de mise a jour K/V definie par le NIST
        self.K = self._hmac(self.V + b"\x00" + donnees)
        self.V = self._hmac(self.V)
        if donnees:
            self.K = self._hmac(self.V + b"\x01" + donnees)
            self.V = self._hmac(self.V)

    def reseed(self, entropie: bytes):
        """
        Réensemence le générateur avec une nouvelle source d'entropie.

        Utile si on soupçonne que l'état a pu être observé, ou simplement
        pour renouveler périodiquement l'entropie (bonne pratique NIST).

        Args:
            entropie (bytes): nouvelles données d'entropie fraîches.
        """
        self._update(entropie)

    def generate_bytes(self, n: int) -> bytes:
        """
        Génère n octets pseudo-aléatoires cryptographiquement sûrs.

        V est mis à jour par HMAC(K, V) en boucle jusqu'à avoir assez
        d'octets, puis K et V sont rafraîchis (forward secrecy).

        Args:
            n (int): nombre d'octets voulus.

        Returns:
            bytes: séquence de n octets.
        """
        sortie = b""
        while len(sortie) < n:
            self.V = self._hmac(self.V)
            sortie += self.V
        self._update()
        return sortie[:n]

    def generate(self, n: int, n_bytes: int = 4) -> list[int]:
        """
        Génère une liste de n entiers non signés.

        Args:
            n       (int): nombre de valeurs voulues.
            n_bytes (int): largeur de chaque entier en octets (défaut : 4).

        Returns:
            list[int]: liste de n entiers dans [0, 2^(8*n_bytes) - 1].
        """
        resultats = []
        for i in range(n):
            bloc = self.generate_bytes(n_bytes)
            resultats.append(int.from_bytes(bloc, 'big'))
        return resultats


if __name__ == "__main__":
    import os
    drbg = HmacDrbgGenerator(entropie=os.urandom(32), nonce=os.urandom(16))
    print("64 octets :", drbg.generate_bytes(64).hex())

    drbg.reseed(os.urandom(32))
    print("apres reseed :", drbg.generate(4))
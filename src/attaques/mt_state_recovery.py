"""
mt_state_recovery.py — Attaque : reconstruction de l'état interne du MT19937

Le tempering applique 4 opérations XOR sur chaque sortie avant de la retourner.
Chacune est inversible, donc on peut retrouver le mot d'état brut à partir
d'une sortie : c'est l'"untemper".

En faisant ça sur 624 sorties consécutives, on reconstruit les 624 mots
de l'état interne complet et on peut prédire toute la suite.

Les 4 opérations du tempering (dans l'ordre) :
  1. y ^= (y >> 11)
  2. y ^= (y << 7)  & 0x9D2C5680
  3. y ^= (y << 15) & 0xEFC60000
  4. y ^= (y >> 18)

Pour inverser, on les défait dans l'ordre inverse (4 -> 3 -> 2 -> 1).
"""

from generators.mersenne_twister import MersenneTwister


def inverser_xor_droite(y: int, shift: int) -> int:
    """
    Inverse l'opération y ^= (y >> shift).

    Les bits de rang [32-shift .. 31] sont inchangés et servent de point
    de départ. On reconstruit les bits suivants en remontant vers les bits de poids faible.

    Args:
        y     (int): valeur à inverser.
        shift (int): décalage de l'opération originale.

    Returns:
        int: valeur avant l'opération XOR droite.
    """
    resultat = y
    decalage = shift
    while decalage < 32:
        fenetre = (0xFFFFFFFF >> decalage) ^ (0xFFFFFFFF >> min(decalage + shift, 32))
        resultat ^= (resultat >> shift) & fenetre
        decalage += shift
    return resultat


def inverser_xor_gauche_mask(y: int, shift: int, mask: int) -> int:
    """
    Inverse l'opération y ^= (y << shift) & mask.

    Les bits de rang [0 .. shift-1] sont inchangés et servent de point
    de départ. On remonte vers les bits de poids fort.

    Args:
        y     (int): valeur à inverser.
        shift (int): décalage de l'opération originale.
        mask  (int): masque de l'opération originale.

    Returns:
        int: valeur avant l'opération XOR gauche masquée.
    """
    resultat = y
    decalage = shift
    while decalage < 32:
        fenetre = ((1 << shift) - 1) << decalage
        resultat ^= (resultat << shift) & mask & fenetre
        decalage += shift
    return resultat


def untemper(y: int) -> int:
    """
    Inverse complètement le tempering MT19937 sur un mot 32-bits.

    Défait les 4 opérations dans l'ordre inverse de leur application.

    Args:
        y (int): sortie observée du MT (après tempering).

    Returns:
        int: mot d'état brut correspondant (avant tempering).
    """
    y = inverser_xor_droite(y, 18)                   # defait : y ^= (y >> 18)
    y = inverser_xor_gauche_mask(y, 15, 0xEFC60000)  # defait : y ^= (y << 15) & mask
    y = inverser_xor_gauche_mask(y, 7,  0x9D2C5680)  # defait : y ^= (y << 7)  & mask
    y = inverser_xor_droite(y, 11)                   # defait : y ^= (y >> 11)
    return y


def cloner_generateur(observations: list[int]):
    """
    Reconstruit un clone parfait du MT à partir de 624 sorties consécutives.

    Applique untemper sur chaque observation pour retrouver les 624 mots
    d'état bruts, puis injecte cet état dans un nouveau générateur.

    Args:
        observations (list[int]): au moins 624 sorties 32-bits consécutives.

    Returns:
        MersenneTwister: clone du générateur original, ou None si moins
                         de 624 observations sont fournies.
    """
    if len(observations) < 624:
        print("Il faut 624 observations.")
        return None

    etat_reconstruit = [untemper(sortie) for sortie in observations[:624]]

    clone = MersenneTwister(0)
    clone.etat  = etat_reconstruit
    clone.index = 624 

    return clone


def demo():
    print("=" * 55)
    print("  Attaque MT19937 : reconstruction d'etat")
    print("=" * 55)

    graine_inconnue = 98765
    gen_cible = MersenneTwister(graine_inconnue)

    print(f"\nObservation de 624 sorties (graine inconnue : {graine_inconnue})...")
    observations = gen_cible.generate(624)

    gen_clone = cloner_generateur(observations)
    print("Etat interne reconstruit.\n")

    vrais       = gen_cible.generate(10)
    predictions = gen_clone.generate(10)

    print("Prediction des 10 prochaines sorties :")
    nb_ok = 0
    for i in range(10):
        ok = predictions[i] == vrais[i]
        if ok:
            nb_ok += 1
        print(f"  Pred: {predictions[i]:<12}  Vrai: {vrais[i]:<12}  -> {'OUI' if ok else 'NON'}")

    print(f"\nResultat : {nb_ok}/10 predictions correctes")


if __name__ == "__main__":
    demo()
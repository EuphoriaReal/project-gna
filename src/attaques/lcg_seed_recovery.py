"""
lcg_seed_recovery.py — Attaque : récupération des paramètres d'un LCG

On observe des sorties X0, X1, X2, ... sans connaître a, c, m ni la graine.

Idée clé : les différences Ti = Xi+1 - Xi forment elles aussi un LCG,
mais sans incrément : Ti+1 = a * Ti (mod m).
On peut le montrer : Ti+2 - a*Ti+1 = 0 (mod m), donc T_{i+2} * T_i - T_{i+1}^2
est toujours un multiple de m. En calculant le PGCD de plusieurs de ces
multiples, on tombe sur m lui-même.
Une fois m connu, retrouver a et c est une simple équation modulaire.
"""

from math import gcd
from generators.lcg import LCG


def retrouver_m(sorties: list[int]):
    """
    Retrouve le modulo m à partir d'une liste de sorties consécutives.

    Calcule les différences Ti = Xi+1 - Xi, puis exploite le fait que
    T_{i+2} * T_i - T_{i+1}^2 est un multiple de m. Le PGCD de plusieurs
    de ces multiples converge vers m.

    Args:
        sorties (list[int]): au moins 5 sorties consécutives du LCG.

    Returns:
        int | None: valeur de m retrouvée, ou None si impossible.
    """
    diffs = [sorties[i + 1] - sorties[i] for i in range(len(sorties) - 1)]

    multiples = []
    for i in range(1, len(diffs) - 1):
        val = diffs[i + 1] * diffs[i - 1] - diffs[i] ** 2
        if val != 0:
            multiples.append(abs(val))

    if not multiples:
        return None

    m = multiples[0]
    for val in multiples[1:]:
        m = gcd(m, val)

    return m if m > 1 else None


def retrouver_a(x0: int, x1: int, x2: int, m: int):
    """
    Retrouve le multiplicateur a à partir de trois sorties consécutives et m.

    Utilise la relation a = (X2 - X1) * (X1 - X0)^-1 mod m.
    Échoue si (X1 - X0) n'est pas inversible modulo m.

    Args:
        x0 (int): première sortie observée.
        x1 (int): deuxième sortie observée.
        x2 (int): troisième sortie observée.
        m  (int): modulo retrouvé par retrouver_m.

    Returns:
        int | None: valeur de a, ou None si (X1 - X0) non inversible mod m.
    """
    diff0 = (x1 - x0) % m
    diff1 = (x2 - x1) % m
    try:
        return (diff1 * pow(diff0, -1, m)) % m
    except ValueError:
        return None


def retrouver_c(x0: int, x1: int, a: int, m: int):
    """
    Retrouve l'incrément c à partir de deux sorties consécutives, a et m.

    De X1 = a*X0 + c mod m, on tire directement c = X1 - a*X0 mod m.

    Args:
        x0 (int): première sortie observée.
        x1 (int): deuxième sortie observée.
        a  (int): multiplicateur retrouvé par retrouver_a.
        m  (int): modulo retrouvé par retrouver_m.

    Returns:
        int: valeur de c.
    """
    return (x1 - a * x0) % m


def demo():
    print("=" * 55)
    print("  Attaque LCG : recuperation de m, a, c")
    print("=" * 55)

    graine = 12345
    a_reel = 1103515245
    c_reel = 12345
    m_reel = 2 ** 31

    gen = LCG(graine, a_reel, c_reel, m_reel)
    sorties = gen.generate(10)

    print("\nCe que l'attaquant observe (10 sorties) :")
    print(sorties)
    print("\nL'attaquant ne connait ni a, ni c, ni m, ni la graine.")

    m_trouve = retrouver_m(sorties)
    if not m_trouve:
        print("Echec : impossible de retrouver m.")
        return

    a_trouve = retrouver_a(sorties[0], sorties[1], sorties[2], m_trouve)
    if a_trouve is None:
        print("Echec : impossible de retrouver a.")
        return

    c_trouve = retrouver_c(sorties[0], sorties[1], a_trouve, m_trouve)

    print("\n--- Parametres retrouves ---")
    print(f"  m : {m_trouve:<15}  (reel : {m_reel})")
    print(f"  a : {a_trouve:<15}  (reel : {a_reel})")
    print(f"  c : {c_trouve:<15}  (reel : {c_reel})")

    etat  = sorties[-1]
    vrais = gen.generate(5)

    print("\n--- Prediction des sorties futures ---")
    for i in range(5):
        prediction = (a_trouve * etat + c_trouve) % m_trouve
        ok = "OUI" if prediction == vrais[i] else "NON"
        print(f"  Pred: {prediction:<12}  Vrai: {vrais[i]:<12}  -> {ok}")
        etat = prediction


if __name__ == "__main__":
    demo()
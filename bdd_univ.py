from bdd_nfa import BDD_NFA

nfa = BDD_NFA(2, 1, 4, x)
bdd = nfa.bdd


def max_sets(q):
    return list(filter(lambda s: not(any((s != ss and set_leq(s, ss)) for ss in q)), q))


def set_leq(B_s1, B_s2):
    return bdd.apply("->", B_s1, B_s2) == bdd.true


def antichain_leq(q1, q2):
    return all(any(set_leq(s1, s2) for s2 in q2) for s1 in q1)


def antichain_lub(q1, q2):
    q1.extend(q2)
    return max_sets(q1)


def pre_sigma(B_s, B_sigma):
    next_q = bdd.let(nfa.prime, B_s)
    u = nfa.B_trans & B_sigma & next_q
    z = bdd.quantify(u, nfa.Sigma, forall=False)
    B_pre = bdd.quantify(z, nfa.vrs1, forall=False)
    return B_pre


def pre(B_s):
    next_q = bdd.let(nfa.prime, B_s)
    u = nfa.B_trans & next_q
    z = bdd.quantify(u, nfa.Sigma, forall=False)
    B_pre = bdd.quantify(z, nfa.vrs1, forall=False)
    return B_pre


def cpre_sigma(B_s, B_sigma):
    next_q = bdd.let(nfa.prime, B_s)
    u = bdd.apply("->", nfa.B_trans & B_sigma, next_q)
    z = bdd.quantify(u, nfa.Sigma, forall=True)
    B_pre = bdd.quantify(z, nfa.vrs1, forall=True)
    return B_pre


def cpre(B_s):
    next_q = bdd.let(nfa.prime, B_s)
    u = bdd.apply("->", nfa.B_trans, next_q)
    z = bdd.quantify(u, nfa.vrs1, forall=True)
    B_pre = bdd.quantify(z, nfa.Sigma, forall=False)
    return B_pre


def Cpre(q):
    return max_sets(list(map(cpre, q)))


def backward_universality(B_A):
    Start = [nfa.B_init]
    F = [~nfa.B_final]
    Frontier = F
    while Frontier and not antichain_leq(Start, Frontier):
        q = Cpre(Frontier)
        Frontier = q if not antichain_leq(q, F) else []
        # filter(lambda q: not antichain_leq(q, F), Cpre(Frontier))
        F = antichain_lub(F, Frontier)
    return not antichain_leq(Start, Frontier)

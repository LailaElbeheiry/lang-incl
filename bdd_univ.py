from bdd_nfa import BDD_NFA

x = ({'11', '01', '00', '10'},
     {'11': {'1': {'01', '00'}, '0': {'01'}},
      '01': {'1': {'11', '10'}, '0': {'11', '01', '00'}},
      '00': {'1': {'00'}, '0': {'10'}},
      '10': {'1': {'11', '01', '00'}, '0': {'10', '00', '01'}}},
     {'01', '10'})

nfa = BDD_NFA(2, 1, 4, x)
bdd = nfa.bdd


def pre_sigma(B_s, B_sigma):
    next_q = bdd.let(nfa.prime, B_s)
    u = nfa.B_trans & B_sigma & next_q
    B_pre = bdd.quantify(u, nfa.vrs1, forall=False)
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
    p = bdd.apply("^", bdd.add_expr("a") , bdd.add_expr("b"))
    z = bdd.quantify(p & u, nfa.Sigma, forall=False)
    B_pre = bdd.quantify(z, nfa.vrs1, forall=True)
    return B_pre


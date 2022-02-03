from nfa_preprocess import ExplicitNFA, BDD_NFA
from nfa_create import gen_nfa, import_nfa
from automata.fa.dfa import DFA
import timeit
import time

x = ({'11', '01', '00', '10'},
     {'11': {'1': {'01', '00'}, '0': {'01'}},
      '10': {'1': {'11', '01', '00'}, '0': {'10', '00', '01'}},
      '01': {'1': {'11', '10'}, '0': {'11', '01', '00'}},
      '00': {'1': {'00'}, '0': {'10'}}},
     '11',
     # {'11', '01', '00', '10'})
     {'01', '10'})


# x = ({'11', '01', '00', '10'},
#      {'00': {'0': {'01'}, '1': set()},
#       '11': {'1': {'00'}, '0': set()},
#       '10': {'1': set(), '0': {'11'}},
#       '01': {'1': {'10'}, '0': set()}},
#      {'11', '01', '00', '10'})
def flatten(t):
    return [item for sublist in t for item in sublist]


def max_sets(q):
    return list(filter(lambda s1: not(any((s1 != s2 and elem_leq(s1, s2)) for s2 in q)), q))


def elem_leq(s1, s2):
    l1, B_s1 = s1
    l2, B_s2 = s2
    return l1 == l2 and set_leq(B_s1, B_s2)


def set_leq(B_s1, B_s2):
    return bdd.apply("->", B_s1, B_s2) == bdd.true


def antichain_leq(q1, q2):
    # return all(any(elem_leq(s1, s2) for s2 in q2) for s1 in q1)
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

def post_sigma(B_s, B_sigma):
    # next_q = bdd.let(nfa.prime, B_s)
    u = nfa.B_trans & B_sigma & B_s
    z = bdd.quantify(u, nfa.Sigma, forall=False)
    B_post = bdd.quantify(z, nfa.vrs0, forall=False)
    return B_post


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


def cpre(s):
    l, B_s = s
    cpre_0 = cpre_sigma(B_s, nfa.B0)
    cpre_1 = cpre_sigma(B_s, nfa.B1)
    transitions = nfa.nfa2[1][l]
    cpre = [(l_, cpre_0) for l_ in transitions['0'] ]
    cpre.extend([(l_, cpre_1) for l_ in transitions['1'] ])
    return cpre


def Cpre(q):
    cpre = list(map(lambda s : cpre_sigma(s, nfa.B0), q))
    cpre.extend(list(map(lambda s : cpre_sigma(s, nfa.B1), q)))
    return max_sets(cpre)

# def not_empty(q):
#     return any(s[1]!=bdd.false for s in q)

# def not_empty(q):
#     return bool(q)

def backward_lang_incl(bdd_nfa):
    Start = [bdd_nfa.B_init]
    F = [bdd.apply(r" /\ ", l, ~bdd_nfa.B_final) for l in nfa.B_final2]
    Frontier = F
    while Frontier and not antichain_leq(Start, Frontier):
        # for elem in Frontier:
        #     l, B_s = elem
        #     print(l, len(list(bdd.pick_iter(B_s))))
        q = Cpre(Frontier)
        Frontier = q if not antichain_leq(q, F) else []
        # filter(lambda q: not antichain_leq(q, F), Cpre(Frontier))
        F = antichain_lub(F, Frontier)
    return not antichain_leq(Start, Frontier)

def subset_lang_incl(explicit_nfa):
    dfa = DFA.from_nfa(explicit_nfa.nfa)
    dfa2 = DFA.from_nfa(explicit_nfa.nfa2)
    return dfa2.issubset(dfa)


if __name__ == '__main__':

    # rand_nfa = gen_nfa(2, 1, 32, False)  # r, f, n
    # for i in range(1, 101):
    for i in range(1, 6):
        print(i)
        # rand_nfa = import_nfa("aut/A{}.ba".format(i), 32)
        rand_nfa = gen_nfa(2, 1, 32, False)  # r, f, n
        rand_nfa2 = gen_nfa(2, 1, 32, False)  # r, f, n
        explicit_nfa = ExplicitNFA(rand_nfa, rand_nfa2)
        nfa = BDD_NFA(rand_nfa, rand_nfa2)
        bdd = nfa.bdd

        start_time = timeit.default_timer()
        print(subset_lang_incl(explicit_nfa))
        print(timeit.default_timer() - start_time)

        start_time = timeit.default_timer()
        print(backward_lang_incl(nfa))
        print(timeit.default_timer() - start_time)

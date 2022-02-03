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

def set_in_antichain(ls, q):
    return any(elem_leq(ls, ls_) for ls_ in q)


def max_sets(q):
    return list(filter(lambda ls1: not(any((ls1 != ls2 and elem_leq(ls1, ls2)) for ls2 in q)), q))


def elem_leq(ls1, ls2):
    l1, B_s1 = ls1
    l2, B_s2 = ls2
    return l1 == l2 and set_leq(B_s1, B_s2)


def set_leq(B_s1, B_s2):
    return bdd.apply("->", B_s1, B_s2) == bdd.true


def antichain_leq(q1, q2):
    return all(any(elem_leq(ls1, ls2) for ls2 in q2) for ls1 in q1)


def antichain_lub(q1, q2):
    q1.extend(q2)
    return max_sets(q1)

def cpre_sigma(B_s, B_sigma):
    next_q = bdd.let(nfa.prime, B_s)
    u = bdd.apply("->", nfa.B_trans & B_sigma, next_q)
    z = bdd.quantify(u, nfa.Sigma, forall=True)
    B_pre = bdd.quantify(z, nfa.vrs1, forall=True)
    return B_pre

def pre_sigma(l, sigma):
    return nfa.transitions2[l][sigma]


def Cpre(q):
    cpre = []
    seen = {}
    for (l, s) in q:
        if l not in seen:
            pred_l0 = pre_sigma(l, '0')
            pred_l1 = pre_sigma(l, '1')
            seen[l] = (pred_l0, pred_l1)
        else:
            pred_l0 = seen[l][0]
            pred_l1 = seen[l][1]

        if s not in seen:
            cpre0 = cpre_sigma(s, nfa.B0)
            cpre1 = cpre_sigma(s, nfa.B1)
            seen[s] = (cpre0, cpre1)
        else:
            cpre0 = seen[s][0]
            cpre1 = seen[s][1]
        cpre.extend([(l, cpre0) for l in pred_l0])
        cpre.extend([(l, cpre1) for l in pred_l1])
    return max_sets(cpre)


def backward_lang_incl(bdd_nfa):
    Start = [bdd_nfa.B_init]
    F = [(l, ~bdd_nfa.B_final) for l in nfa.B_final2]
    Frontier = F
    while Frontier and not antichain_leq(Start, Frontier):
        # print(len(Frontier))
        q = Cpre(Frontier)
        # Frontier = q if not antichain_leq(q, F) else []
        Frontier = list(filter(lambda ls: not antichain_leq([ls], F), q))
        F = antichain_lub(F, Frontier)
    return not antichain_leq(Start, Frontier)


def subset_lang_incl(explicit_nfa):
    dfa = DFA.from_nfa(explicit_nfa.nfa)
    dfa2 = DFA.from_nfa(explicit_nfa.nfa2)
    return dfa2.issubset(dfa)


if __name__ == '__main__':

    # rand_nfa = gen_nfa(2, 1, 32, False)  # r, f, n
    # for i in range(1, 101):
    for i in range(1, 5):
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

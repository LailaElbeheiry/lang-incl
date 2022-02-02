from nfa_preprocess import ExplicitNFA, BDD_NFA
from nfa_create import gen_nfa, import_nfa
from automata.fa.dfa import DFA
import timeit
import time

# x = ({'11', '01', '00', '10'},
#      {'11': {'1': {'01', '00'}, '0': {'01'}},
#       '10': {'1': {'11', '01', '00'}, '0': {'10', '00', '01'}},
#       '01': {'1': {'11', '10'}, '0': {'11', '01', '00'}},
#       '00': {'1': {'00'}, '0': {'10'}}},
#      # {'11', '01', '00', '10'})
#      {'01', '10'})


# x = ({'11', '01', '00', '10'},
#      {'00': {'0': {'01'}, '1': set()},
#       '11': {'1': {'00'}, '0': set()},
#       '10': {'1': set(), '0': {'11'}},
#       '01': {'1': {'10'}, '0': set()}},
#      {'11', '01', '00', '10'})


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


def backward_universality(bdd_nfa):
    Start = [bdd_nfa.B_init]
    F = [~bdd_nfa.B_final]
    Frontier = F
    while Frontier and not antichain_leq(Start, Frontier):
        q = Cpre(Frontier)
        Frontier = q if not antichain_leq(q, F) else []
        # filter(lambda q: not antichain_leq(q, F), Cpre(Frontier))
        F = antichain_lub(F, Frontier)
    return not antichain_leq(Start, Frontier)

def subset_constr_universality(explicit_nfa):
    dfa = DFA.from_nfa(explicit_nfa.nfa)
    dfa_ = dfa.complement()
    return dfa_.isempty()


if __name__ == '__main__':

    # rand_nfa = gen_nfa(2, 1, 32, False)  # r, f, n
    for i in range(1, 101):
        print(i)
        # rand_nfa = import_nfa("aut/A{}.ba".format(i), 32)
        rand_nfa = gen_nfa(2, 1, 128, False)  # r, f, n
        explicit_nfa = ExplicitNFA(rand_nfa)
        nfa = BDD_NFA(rand_nfa)
        bdd = nfa.bdd

        start_time = timeit.default_timer()
        print(subset_constr_universality(explicit_nfa))
        print(timeit.default_timer() - start_time)

        start_time = timeit.default_timer()
        print(backward_universality(nfa))
        print(timeit.default_timer() - start_time)


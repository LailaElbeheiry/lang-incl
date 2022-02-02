import math
from functools import reduce
from rand_nfa import gen_nfa
from dd import autoref as _bdd


class BDD_NFA:

    bdd = _bdd.BDD()
    bdd.configure(reordering=True)

    def __init__(self, r, f, n, x):
        # Assuming the n is a power of 2 for simplicity
        k = int(math.log2(n))
        # states, transitions, final = gen_nfa(r, f, n, False)
        (states, transitions, final) = x
        vrs0 = ['b{i}'.format(i=k-1-i) for i in range(k)]
        vrs1 = ["b{i}'".format(i=k-1-i) for i in range(k)]
        vrs0.extend(vrs1)
        vrs0.extend(["a"])  # a, b representing 0, 1
        self.k = k
        self.vrs0 = vrs0[:k]
        self.vrs1 = vrs1
        self.prime = dict(zip(self.vrs0, self.vrs1))
        self.Sigma = ["a"]
        self.bdd.declare(*vrs0)

        B_trans = ""
        for index, state in enumerate(transitions):
            if index == 0:
                #  we pick the state 0 to be the initial state
                #  TODO check if one initial state is good enough
                self.B_init = self.bdd.add_expr(self.state_to_str(state, vrs0[:k]))
            if transitions[state]['0']:
                if index != 0:
                    B_trans += r" \/ "
                B_trans += r"({} /\ a /\ ({}))".format(self.state_to_str(state, vrs0[:k]),
                                                       self.disjunct_states(transitions[state]['0']))
            if transitions[state]['1']:
                B_trans += r" \/ "
                B_trans += r"({} /\ ~a /\ ({}))".format(self.state_to_str(state, vrs0[:k]),
                                                        self.disjunct_states(transitions[state]['1']))

        print(B_trans)
        self.trans_str = B_trans
        self.B_trans = self.bdd.add_expr(B_trans)

        B_final = ""
        for index, state in enumerate(final):
            if index != 0:
                B_final += r" \/ "
            B_final += self.state_to_str(state, vrs0[:k])
        self.B_final = self.bdd.add_expr(B_final)


    def state_to_str(self, state, var_set):
        output = r"("
        for idx, bit in enumerate(state):
            if idx != 0:
                output += r" /\ "
            output += (r"{}" if int(bit) else r"~ {}").format(var_set[idx])
        output += r")"
        return output

    def disjunct_states(self, next_states):
        prop = ""
        for idx, next_state in enumerate(next_states):
            if idx != 0:
                prop += r" \/ "
            prop += self.state_to_str(next_state, self.vrs1)
        return prop




# ((~ b1 /\ ~ b0) /\ a /\ ((~ b1' /\ b0')))
# \/
# \/ ((b1 /\ b0) /\ ~a /\ ((~ b1' /\ ~ b0')))
# \/ ((b1 /\ ~ b0) /\ a /\ ((b1' /\ b0')))
# \/
# \/ ((~ b1 /\ b0) /\ ~a /\ ((b1' /\ ~ b0')))

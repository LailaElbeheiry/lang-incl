import math
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
        vrs0.extend(["a", "b"])  # a, b representing 0, 1
        self.k = k
        self.vrs0 = vrs0[:k]
        self.vrs1 = vrs1
        self.prime = dict(zip(self.vrs0, self.vrs1))
        self.Sigma = ["a", "b"]
        self.bdd.declare(*vrs0)

        B_trans = r"("
        for index, state in enumerate(transitions):
            if index != 0:
                B_trans += r" \/ "
            B_trans += r"({} /\ a /\ ({}))".format(self.state_to_str(state, vrs0[:k]),
                                            self.disjunct_states(transitions[state]['0']))
            B_trans += r" \/ "
            B_trans += r"({} /\ b /\ ({}))".format(self.state_to_str(state, vrs0[:k]),
                                            self.disjunct_states(transitions[state]['1']))
        B_trans += r") /\ ~ (a /\ b)"
        self.B_trans = self.bdd.add_expr(B_trans)

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





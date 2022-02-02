import numpy as np
import random
import itertools
from automata.fa.nfa import NFA

symbols = {'0', '1'}

# states = {"0", "1", "2", ..., "n-1"}
# trans_a = [("x_0", "y_0"), ..., ("x_k-1", "y_k-1")]
# where (x_i, y_i) is randomly sampled from states^2
# trans_b similarly defined
# final = [
def gen_nfa(r, f, n, stringify):
    k = int(r * n)
    m = int(f * n)
    kk = int(np.log2(n))
    map_fn = str if stringify else (lambda x : np.binary_repr(x, width = kk))
    states = set(map(map_fn, range(n)))
    state_pairs = set(itertools.product(states, repeat = 2))
    trans_0 = random.sample(state_pairs, k)
    trans_1 = random.sample(state_pairs, k)
    final = random.sample(states, m)
    transitions = {state : {s: set() for s in symbols} for state in states}
    [transitions[l]['0'].add(l_) for l, l_ in trans_0]
    [transitions[l]['1'].add(l_) for l, l_ in trans_1]
    return (states, transitions, set(final))

def ssc_nfa(r, f, n):
    states, transitions, final = gen_nfa(r, f, n, True)
    nfa = NFA(states = states,
              input_symbols = symbols,
              transitions = transitions,
              initial_state = '0',
              final_states = final)
    return nfa

def bdd_nfa(r, f, n):
    states, trans_0, trans_1, final = gen_nfa(r, f, n)














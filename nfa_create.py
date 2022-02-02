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
    initial = random.choice(list(states))
    transitions = {state : {s: set() for s in symbols} for state in states}
    [transitions[l]['0'].add(l_) for l, l_ in trans_0]
    [transitions[l]['1'].add(l_) for l, l_ in trans_1]
    return (states, transitions, initial, set(final))


def import_nfa(filename, n):
    f = open(filename)
    k = int(np.log2(n))
    map_fn = lambda x: np.binary_repr(int(x), width = k)
    initial = map_fn(int(f.readline().strip().replace("[","").replace("]", "")))
    states = set(map(map_fn, range(n)))
    line = f.readline()
    final = []
    trans_0 = []
    trans_1 = []
    while(line.startswith("a")):
        line = line.strip()
        symbol = line[:line.index(",")].replace("a", "")
        trans = line[line.index("["):]
        trans = trans.split("->")
        trans = list(map(lambda s: s.replace("[", "").replace("]", ""), trans))
        if symbol == '0':
            trans_0.append((map_fn(trans[0]), map_fn(trans[1])))
        else:
            trans_1.append((map_fn(trans[0]), map_fn(trans[1])))
        line = f.readline()

    while(line):
        final.append(map_fn(line.strip().replace("[", "").replace("]", "")))
        line = f.readline()

    print(initial)
    transitions = {state: {s: set() for s in symbols} for state in states}
    [transitions[l]['0'].add(l_) for l, l_ in trans_0]
    [transitions[l]['1'].add(l_) for l, l_ in trans_1]

    return (states, transitions, initial, set(final))

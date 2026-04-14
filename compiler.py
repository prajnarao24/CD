import lexery
import re
from prettytable import PrettyTable
from copy import deepcopy

# ── TOKENS ──────────────────────────────────────────────────────────────────
rules = [
    lexery.Rule(identifier='DATATYPE', pattern=re.compile(r'\b(int|char|void)\b')),
    lexery.Rule(identifier='MAIN',     pattern=re.compile(r'\bmain\b')),
    lexery.Rule(identifier='PRINTF',   pattern=re.compile(r'\bprintf\b')),
    lexery.Rule(identifier='IF',       pattern=re.compile(r'\bif\b')),
    lexery.Rule(identifier='BEGIN',    pattern=re.compile(r'\bbegin\b')),
    lexery.Rule(identifier='END',      pattern=re.compile(r'\bend\b')),
    lexery.Rule(identifier='EXPR',     pattern=re.compile(r'\bexpr\b')),
    lexery.Rule(identifier='RELOP',    pattern=re.compile(r'>=|<=|!=|==|>|<|\brelop\b')),
    lexery.Rule(identifier='LPAR',     pattern=re.compile(r'\(')),
    lexery.Rule(identifier='RPAR',     pattern=re.compile(r'\)')),
    lexery.Rule(identifier='COMMA',    pattern=re.compile(r',')),
    lexery.Rule(identifier='SEMI',     pattern=re.compile(r';')),
    lexery.Rule(identifier='VARIABLE', pattern=re.compile(r'\b[a-zA-Z][a-zA-Z0-9_]*\b')),
]

def get_tokens():
    text = open("input.txt", "r").read()
    lexer = lexery.Lexer(rules, skip_whitespace=True)
    tokens = lexer.lex(text=text)
    token_list = []
    print("\n── TOKEN GENERATION ──")
    t = PrettyTable(['Token Type', 'Value'])
    for token_group in tokens:
        for tok in token_group:
            t.add_row([tok.identifier, tok.content])
            token_list.append(tok.identifier)
    print(t)
    return token_list

def get_grammar():
    # Grammar for: int main() begin DECL; IFSTMT IFSTMT IFSTMT end
    grammar = {
        'S':      [['DATATYPE', 'MAIN', 'LPAR', 'RPAR', 'BEGIN', 'STMT', 'END']],
        'STMT':   [['DECL', 'SEMI', 'IFSTMT', 'IFSTMT', 'IFSTMT']],
        'DECL':   [['DATATYPE', 'VARIABLE', 'COMMA', 'VARIABLE', 'COMMA', 'VARIABLE']],
        'IFSTMT': [['IF', 'LPAR', 'EXPR', 'RELOP', 'EXPR', 'RPAR', 'BEGIN',
                    'PRINTF', 'LPAR', 'VARIABLE', 'RPAR', 'SEMI', 'END']],
    }
    return grammar

def remove_left_recursion(diction):
    store = {}
    for A in list(diction.keys()):
        alpha, beta = [], []
        for rule in diction[A]:
            if rule[0] == A:
                alpha.append(rule[1:])
            else:
                beta.append(rule)
        if alpha:
            newNT = A + "'"
            while newNT in diction or newNT in store:
                newNT += "'"
            for rule in beta:
                rule.append(newNT)
            store[newNT] = [r + [newNT] for r in alpha]
            store[newNT].append(['#'])
            diction[A] = beta
    diction.update(store)
    return diction

def left_factoring(diction):
    new_diction = {}
    for A in diction:
        all_rules = diction[A]
        temp = {}
        for rule in all_rules:
            key = rule[0]
            temp.setdefault(key, []).append(rule)
        new_rule = []
        temp_dict = {}
        for key in temp:
            group = temp[key]
            if len(group) > 1:
                A_new = A + "'"
                while A_new in diction or A_new in new_diction:
                    A_new += "'"
                new_rule.append([key, A_new])
                temp_dict[A_new] = [r[1:] if len(r) > 1 else ['#'] for r in group]
            else:
                new_rule.append(group[0])
        new_diction[A] = new_rule
        new_diction.update(temp_dict)
    return new_diction

def find_first(proddict, firstdict, non_terminals, ele):
    if ele in firstdict:
        return firstdict[ele]
    if ele not in proddict:
        return [ele]
    result = []
    for rule in proddict[ele]:
        if not rule or rule == ['#']:
            result.append('#')
            continue
        for symbol in rule:
            sym_first = find_first(proddict, firstdict, non_terminals, symbol)
            result += [s for s in sym_first if s != '#']
            if '#' not in sym_first:
                break
        else:
            result.append('#')
    firstdict[ele] = list(set(result))
    return firstdict[ele]

def compute_firsts(diction):
    non_terminals = list(diction.keys())
    firstdict = {}
    for nt in non_terminals:
        find_first(diction, firstdict, non_terminals, nt)
    return firstdict

def first_of_string(symbols, non_terminals, firstDict):
    result = []
    for sym in symbols:
        if sym not in non_terminals:
            result.append(sym)
            return result
        f = firstDict.get(sym, [sym])
        result += [s for s in f if s != '#']
        if '#' not in f:
            return result
    result.append('#')
    return result

def compute_follows(diction, start, firstDict):
    non_terminals = list(diction.keys())
    follows = {nt: set() for nt in non_terminals}
    follows[start].add('$')
    changed = True
    while changed:
        changed = False
        for lhs in diction:
            for rule in diction[lhs]:
                for i, sym in enumerate(rule):
                    if sym not in non_terminals:
                        continue
                    after = rule[i+1:]
                    f = first_of_string(after, non_terminals, firstDict)
                    before = len(follows[sym])
                    follows[sym].update(t for t in f if t != '#')
                    if '#' in f or not after:
                        follows[sym].update(follows[lhs])
                    if len(follows[sym]) != before:
                        changed = True
    return {nt: list(v) for nt, v in follows.items()}

def create_parse_table(firsts, follows, diction):
    non_terminals = list(diction.keys())
    # Collect terminals from grammar rules
    all_symbols = set()
    for rules in diction.values():
        for rule in rules:
            for sym in rule:
                if sym not in non_terminals and sym != '#':
                    all_symbols.add(sym)
    terminals = sorted(all_symbols) + ['$']

    # Initialize table
    table = {nt: {t: '' for t in terminals} for nt in non_terminals}
    grammar_is_ll = True

    for lhs in diction:
        for rhs in diction[lhs]:
            rhs_first = first_of_string(rhs, non_terminals, firsts)
            for t in rhs_first:
                if t != '#' and t in terminals:
                    if table[lhs][t] == '':
                        table[lhs][t] = f"{lhs}->{''.join(rhs)}"
                    else:
                        table[lhs][t] += f" | {lhs}->{''.join(rhs)}"
                        grammar_is_ll = False
            if '#' in rhs_first:
                for t in follows[lhs]:
                    if t in terminals:
                        if table[lhs][t] == '':
                            table[lhs][t] = f"{lhs}->{''.join(rhs)}"
                        else:
                            table[lhs][t] += f" | {lhs}->{''.join(rhs)}"
                            grammar_is_ll = False

    print("\n── PARSE TABLE ──")
    pt = PrettyTable(['NT'] + terminals)
    for nt in non_terminals:
        pt.add_row([nt] + [table[nt][t] for t in terminals])
    print(pt)
    print(f"\nGrammar is LL(1): {grammar_is_ll}")
    return table, terminals, grammar_is_ll

def validate(parse_table, grammar_ll, terminals, token_list, start_symbol, non_terminals):
    input_tokens = token_list + ['$']
    print(f"\n── VALIDATE: {' '.join(token_list)} ──")
    if not grammar_ll:
        print("Grammar is not LL(1). Cannot parse.")
        return "Invalid: Grammar not LL(1)", []

    stack = [start_symbol, '$']
    idx = 0
    steps = []

    while True:
        top = stack[0]
        cur = input_tokens[idx] if idx < len(input_tokens) else '$'
        buf_str = ' '.join(input_tokens[idx:])
        stk_str = ' '.join(stack)

        if top == '$' and cur == '$':
            steps.append([buf_str, stk_str, "ACCEPT"])
            print_steps(steps)
            return "Valid String!", steps

        elif top == cur:  # terminal match
            steps.append([buf_str, stk_str, f"Match: {top}"])
            stack.pop(0)
            idx += 1

        elif top in non_terminals:
            entry = parse_table.get(top, {}).get(cur, '')
            if not entry:
                steps.append([buf_str, stk_str, f"ERROR: no rule for [{top}][{cur}]"])
                print_steps(steps)
                return "Invalid String!", steps
            # Use first production if multiple
            production = entry.split(' | ')[0]
            rhs = production.split('->')[1]
            rhs_symbols = list(rhs) if not any(len(s) > 1 for s in rhs.split()) else rhs.split()
            # Better: reconstruct rhs as list of grammar symbols
            rhs_symbols = reconstruct_rhs(rhs, non_terminals, terminals)
            steps.append([buf_str, stk_str, production])
            stack.pop(0)
            if rhs_symbols != ['#']:
                stack = rhs_symbols + stack

        else:
            steps.append([buf_str, stk_str, f"ERROR: terminal mismatch {top} vs {cur}"])
            print_steps(steps)
            return "Invalid String!", steps

def reconstruct_rhs(rhs_str, non_terminals, terminals):
    """Greedily match longest symbols from left."""
    all_syms = sorted(non_terminals + terminals, key=lambda x: -len(x))
    result = []
    i = 0
    while i < len(rhs_str):
        matched = False
        for sym in all_syms:
            if rhs_str[i:i+len(sym)] == sym:
                result.append(sym)
                i += len(sym)
                matched = True
                break
        if not matched:
            if rhs_str[i] == '#':
                result.append('#')
            i += 1
    return result if result else ['#']

def print_steps(steps):
    print("\n── VALIDATION STEPS ──")
    sv = PrettyTable(['Buffer', 'Stack', 'Action'])
    sv.max_width = 60
    for s in steps:
        sv.add_row(s)
    print(sv)

# ── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    token_list = get_tokens()

    grammar = get_grammar()
    grammar = remove_left_recursion(grammar)
    grammar = left_factoring(grammar)

    print("\n── GRAMMAR (after processing) ──")
    for k, v in grammar.items():
        for r in v:
            print(f"  {k} -> {' '.join(r)}")

    firsts  = compute_firsts(grammar)
    follows = compute_follows(grammar, 'S', firsts)

    print("\n── FIRST & FOLLOW ──")
    t = PrettyTable(['Non-Terminal', 'FIRST', 'FOLLOW'])
    for nt in grammar:
        t.add_row([nt, sorted(firsts.get(nt, [])), sorted(follows.get(nt, []))])
    print(t)

    non_terminals = list(grammar.keys())
    parse_table, terminals, grammar_ll = create_parse_table(firsts, follows, grammar)

    result, steps = validate(
        parse_table, grammar_ll, terminals,
        token_list, 'S', non_terminals)

    print(f"\n── RESULT: {result} ──")
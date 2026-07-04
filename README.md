# SLR Parser & Mini Compiler

A hand-built compiler that determines the largest number among given values using conditional (`if`) logic — implemented **without parser generators like Lex/Yacc**. The project manually constructs an SLR (Simple LR) parsing table from grammar rules and validates tokenized input against it, demonstrating the internal mechanics of compiler design.

## Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
  - [1. Tokenization](#1-tokenization)
  - [2. Grammar Definition](#2-grammar-definition)
  - [3. FIRST & FOLLOW Set Computation](#3-first--follow-set-computation)
  - [4. LR(0) Item Set & State Construction](#4-lr0-item-set--state-construction)
  - [5. SLR Parse Table Construction](#5-slr-parse-table-construction)
  - [6. Parsing & Validation](#6-parsing--validation)
- [Tech Stack](#tech-stack)
- [Sample Output](#sample-output)
- [Key Concepts Demonstrated](#key-concepts-demonstrated)
- [How to Run](#how-to-run)
- [Why This Project](#why-this-project)

## Overview

Most compiler projects rely on tools like Lex and Yacc to auto-generate lexers and parsers. This project instead builds the core phases of a compiler manually in Python:

1. **Lexical Analysis** — tokenizes raw source code into meaningful symbols (datatypes, keywords, operators, identifiers, etc.)
2. **Syntax Analysis (SLR Parsing)** — constructs LR(0) item sets, FIRST/FOLLOW sets, and a full SLR parsing table (SHIFT / REDUCE / ACCEPT actions)
3. **Semantic Evaluation** — validates whether tokenized input conforms to the defined grammar using a stack-based shift-reduce parser

## How It Works

### 1. Tokenization
Input source code (`input.txt`) is scanned using regex-based lexical rules to identify tokens such as `DATATYPE`, `MAIN`, `PRINTF`, `IF`, `RELOP`, `VARIABLE`, and punctuation (`(`, `)`, `,`, `;`).

### 2. Grammar Definition
A context-free grammar is defined to represent a simplified C-like program structure — including variable declarations and an `if` conditional block used to compare values.

### 3. FIRST & FOLLOW Set Computation
Computed iteratively for all non-terminals to support parse table construction.

### 4. LR(0) Item Set & State Construction
Builds canonical LR(0) collections using `closure()` and `goto()` operations, generating all parser states and state transitions.

### 5. SLR Parse Table Construction
Combines LR(0) states with FOLLOW sets to populate:
- **ACTION table** — shift, reduce, and accept operations
- **GOTO table** — non-terminal state transitions

### 6. Parsing & Validation
A stack-based shift-reduce parser processes the token stream against the parse table, printing each step (stack contents, current input, action taken) until the input is either **accepted** or flagged as an **invalid string**.

## Tech Stack
- **Python**
- `lexery` — regex-based lexical analysis
- `prettytable` — formatted console output for tokens, grammar, FIRST/FOLLOW sets, parse tables, and parsing trace

## Sample Output
The program prints:
- Token generation table
- Grammar rules
- FIRST and FOLLOW sets for each non-terminal
- Total LR(0) states generated
- Full SLR parse table (ACTION + GOTO)
- Step-by-step parsing trace (stack, input, action)
- Final result: `Valid String!` or `Invalid String!`

## Key Concepts Demonstrated
- Bottom-up (shift-reduce) parsing
- LR(0) automaton construction
- SLR(1) parse table generation
- Grammar ambiguity resolution via FOLLOW sets
- Stack-based input validation
- Manual compiler pipeline design (without Lex/Yacc)

## How to Run
```bash
python main.py
```
Ensure `input.txt` contains the source code to be parsed, placed in the same directory.

## Why This Project
Built to strengthen understanding of compiler internals covered in Theory of Computation and Compiler Design coursework — particularly bottom-up parsing and LR grammar analysis — by implementing the theory from first principles rather than relying on automated tooling.
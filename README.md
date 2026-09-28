# Classiq Alignment: Quantum Transpiler

A custom quantum circuit compiler and state vector simulator built from scratch in Python. This engine parses raw quantum instruction strings into an Abstract Syntax Tree (AST), dynamically scales 2D unitary matrices using Kronecker tensor products, and simulates exact quantum state probabilities over time.

## 🏗️ System Architecture

The pipeline is strictly modular, enforcing a strong separation of concerns across three primary components:

### 1. Lexical Analyzer (Lexer)
* **Regex State Machine:** Utilizes a compiled regular expression engine (`re.compile`) to parse single-qubit and multi-qubit instructions (e.g., `H(0)`, `CNOT(0,1)`).
* **AST Generation:** Converts raw string inputs into a highly structured Abstract Syntax Tree of immutable tuples and lists.
* **Fail-Fast Boundary:** Catches syntax errors immediately at the boundary layer before any intensive matrix algebra is attempted, throwing a custom `TranspilerError`.

### 2. Gate Registry
A lightweight mathematical library storing fundamental 2D quantum operators as NumPy arrays, including standard unitaries ($X$, $H$, $I$) and projectors ($P_0$, $P_1$) required for multi-qubit control gates.

### 3. Quantum Compiler & Tensor Engine
* **Dynamic Kronecker Assembly:** Instead of relying on hardcoded 4x4 matrices, the engine dynamically constructs $N$-qubit execution matrices on the fly using `np.kron`. 
* **State Vector Multiplication:** Applies the compiled physical operations against the system's global state vector via precise dot products.
* **ASCII Circuit Rendering:** Generates a visual timeline of the executed quantum circuit upon completion.

## 🚀 Execution & Output

By default, the transpiler runs a standard **Bell State** entanglement circuit: `["H(0)", "CNOT(0,1)"]`.

### Installation
```bash
git clone [https://github.com/EthanM-programin/Classiq_Transpiler.git](https://github.com/EthanM-programin/Classiq_Transpiler.git)
cd Classiq_Transpiler
python transpiler.py
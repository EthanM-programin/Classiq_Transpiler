import re
import math
import numpy as np
from typing import List, Tuple

class TranspilerError(Exception):
    """Custom exception for any parsing or compilation errors."""
    pass

class Lexer:
    """Handles lexical analysis: converting raw text strings into structured AST tokens."""
    PATTERN = re.compile(r"^([A-Z]+)\((\d+),?\s*(\d+)?\)$")

    @staticmethod
    def tokenize(instruction: str) -> Tuple[str, List[int]]:
        """Parses a single instruction string into a (gate, [target_qubits]) tuple."""
        instruction = instruction.strip()
        match = Lexer.PATTERN.match(instruction)

        if not match:
            raise TranspilerError(f"Syntax Error: Invalid instruction '{instruction}'. Expected format like 'H(0)' or 'CNOT(0,1)'.")

        gate = match.group(1)
        targets = [int(match.group(2))]

        if match.group(3):
            targets.append(int(match.group(3)))

        return (gate, targets)

    @staticmethod
    def tokenize_circuit(instructions: List[str]) -> List[Tuple[str, List[int]]]:
        """Parses an entire array of raw strings into an Abstract Syntax Tree (AST)."""
        return [Lexer.tokenize(cmd) for cmd in instructions]

class GateRegistry:
    """Library of fundamental 2D qunatum unitary matrices and projectors."""
    I = np.array([[1, 0],
                [0, 1]])

    X = np.array([[0, 1],
                  [1, 0]])

    H = (1 / math.sqrt(2)) * np.array([[1, 1],
                                      [1, -1]])

    # Projectors required to construct multi-qubit CNOT gates
    P0 = np.array([[1, 0],
                   [0, 0]])
    P1 = np.array([[0, 0],
                   [0, 1]])

class QuantumCompiler:
    """The core engine that scales tensors, applies physical operations, and renders output."""
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits

        # Initialize the state vector to absolute zero: |0...0>
        # An N-qubit system has 2^N total possible states
        self.dim = 2 ** num_qubits
        self.state_vector = np.zeros(self.dim)
        self.state_vector[0] = 1.0

    def _build_single_qubit_matrix(self, gate_matrix: np.ndarray, target: int) -> np.ndarray:
        """Dynamically scales a 2x2 matrix to the full 2^N Hilbert space via Kronecker products."""
        operator = np.array([[1]])
        for i in range(self.num_qubits):
            # If this is the target wire, apply the gate. Otherwise, apply Identity (do nothing).
            current_matrix = gate_matrix if i == target else GateRegistry.I
            operator = np.kron(operator, current_matrix)

        return operator

    def _build_cnot_matrix(self, control: int, target: int) -> np.ndarray:
        """Constructs a mathematically rigorous CNOT matrix for an N-qubit system."""
        # CNOT formula = (|0><0| ⊗ I) + (|1><1| ⊗ X)
        op0 = np.array([[1]])
        op1 = np.array([[1]])

        for i in range(self.num_qubits):
            if i == control:
                op0 = np.kron(op0, GateRegistry.P0)
                op1 = np.kron(op1, GateRegistry.P1)
            elif i == target:
                op0 = np.kron(op0, GateRegistry.I)
                op1 = np.kron(op1, GateRegistry.X)
            else:
                op0 = np.kron(op0, GateRegistry.I)
                op1 = np.kron(op1, GateRegistry.I)

        return op0 + op1

    def compile_and_run(self, raw_instructions: List[str]) -> List[Tuple[str, List[int]]]:
        """Executes the full pipeline: Lexer -> Matrix Assembly -> State Vector Update."""
        ast = Lexer.tokenize_circuit(raw_instructions)

        for gate, targets in ast:
            if gate in ["H", "X"]:
                if len(targets) != 1:
                     raise TranspilerError(f"Gate {gate} requires exactly 1 target.")

                matrix = GateRegistry.H if gate == "H" else GateRegistry.X
                full_operator = self._build_single_qubit_matrix(matrix, targets[0])

            elif gate == "CNOT":
                if len(targets) != 2:
                    raise TranspilerError("CNOT requires exactly 2 targets (control, target).")
                if targets[0] == targets[1]:
                    raise TranspilerError("CNOT control and target cannot be the same qubit.")

                full_operator = self._build_cnot_matrix(targets[0], targets[1])

            else:
                raise TranspilerError(f"Gate '{gate}' is not supported by the current registry.")

            # Physically apply the gate matrix to the state vector via dot product
            self.state_vector = np.dot(full_operator, self.state_vector)

        return ast

    def draw_circuit(self, ast: List[Tuple[str, List[int]]]) -> str:
        """Generates a visual ASCII timeline of the executed quantum circuit."""
        wires = {i: [f"q{i}: ──"] for i in range(self.num_qubits)}

        for gate, targets in ast:
            for i in range(self.num_qubits):
                if gate == "CNOT":
                    c, t = targets[0], targets[1]
                    if i == c:
                        wires[i].append("■───")
                    elif i == t:
                        wires[i].append("X───")
                    else:
                        wires[i].append("────")
                else:
                    if i == targets[0]:
                        wires[i].append(f"{gate}───")
                    else:
                        wires[i].append("────")

        return "\n".join("".join(wires[i]) for i in range(self.num_qubits))

    def get_probabilities(self) -> np.ndarray:
        """Returns the classical measurement probabilites (|amplitude|^2)."""
        return np.round(np.abs(self.state_vector) ** 2, decimals=4)

# Main execution block
if __name__ == "__main__":
    print("Classiq Alignment: Quantum Transpiler")

    # We are inputting a classic Bell State entanglement circuit
    raw_code = ["H(0)", "CNOT(0, 1)"]
    num_qubits = 2

    compiler = QuantumCompiler(num_qubits)

    try:
        print("\n[1] Compiling Abstract Syntax Tree...")
        ast = compiler.compile_and_run(raw_code)
        for token in ast:
            print(f" -> {token}")

        print("\n[2] Generating ASCII Circuit Diagram...")
        print(compiler.draw_circuit(ast))

        print("\n[3] Calculating Exact System Probabilites...")
        probs = compiler.get_probabilities()

        # Iterates through the 2^N probability array and formats the binary strings
        for i, p in enumerate(probs):
            binary_state = format(i, f'0{num_qubits}b')
            print(f" |{binary_state}> : {p * 100:.2f}%")

    except TranspilerError as e:
        print(f"\n[!] Compilation failed: {e}")
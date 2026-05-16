import sys
import os

# Get the path of the current 'solvers' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the path of the parent 'backend' directory
parent_dir = os.path.dirname(current_dir)

# Explicitly inject both paths into Python's search engine
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import kociemba
from cube import Cube  # This absolutely cannot fail now!
def solve(cube):

    """
    Solve a Rubik's cube using Kociemba's algorithm.

    Args:
        cube: Cube instance representing the scrambled state

    Returns:
        List of moves to solve the cube (e.g., ['U', 'R', "F'", 'U2', ...])
        Empty list if cube is already solved

    Raises:
        ValueError: If cube state is invalid or unsolvable
    """
    if not isinstance(cube, Cube):
        raise TypeError(f"Expected Cube instance, got {type(cube)}")

    if cube.is_solved():
        return []

    state = cube.get_state()

    try:
        # Kociemba returns solution as a string like "U R F' U2 B2"
        solution_str = kociemba.solve(state)
        # Parse into list of moves
        moves = solution_str.split() if solution_str else []
        return moves
    except Exception as e:
        raise ValueError(f"Failed to solve cube: {e}")


def get_solver_info():
    """Return information about the solver."""
    return {
        "solver": "Kociemba",
        "description": "Optimal Rubik's cube solver using Kociemba's algorithm",
        "max_moves": 20,  # God's number for 3x3
        "supported_cubes": "3x3 only",
    }

class Cube:
    """Represents a 3x3 Rubik's cube state using the Kociemba format."""

    FACES = {'U', 'D', 'L', 'R', 'F', 'B'}
    INITIAL_STATE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

    def _validate(self):
        state = self.state
        for face in self.FACES:
            count = state.count(face)
            if count != 9:
                raise ValueError(f"Face {face} appears {count} times, expected 9")

    def __init__(self, state=None):
        """
        Initialize cube with given state or solved state.
        State should be 54 characters representing colors on all faces.
        """
        if state is None:
            self.state = self.INITIAL_STATE
        else:
            if len(state) != 54:
                raise ValueError(f"State must have 54 characters, got {len(state)}")
            self.state = state.upper()
            self._validate()


    def get_state(self):
        """Return the current cube state as a string."""
        return self.state

    def set_state(self, state):
        """Set the cube state and validate."""
        if len(state) != 54:
            raise ValueError(f"State must have 54 characters, got {len(state)}")
        self.state = state.upper()
        self._validate()

    def is_solved(self):
        """Check if the cube is in the solved state."""
        return self.state == self.INITIAL_STATE

    def __repr__(self):
        """Return string representation of cube state."""
        return f"Cube('{self.state}')"

    def __str__(self):
        """Return human-readable visualization of the cube."""
        s = self.state
        # Format the cube in an unfolded layout
        lines = [
            f"      {s[0]} {s[1]} {s[2]}",
            f"      {s[3]} {s[4]} {s[5]}",
            f"      {s[6]} {s[7]} {s[8]}",
            f"{s[36]} {s[37]} {s[38]} | {s[9]} {s[10]} {s[11]} | {s[18]} {s[19]} {s[20]} | {s[27]} {s[28]} {s[29]}",
            f"{s[39]} {s[40]} {s[41]} | {s[12]} {s[13]} {s[14]} | {s[21]} {s[22]} {s[23]} | {s[30]} {s[31]} {s[32]}",
            f"{s[42]} {s[43]} {s[44]} | {s[15]} {s[16]} {s[17]} | {s[24]} {s[25]} {s[26]} | {s[33]} {s[34]} {s[35]}",
            f"      {s[45]} {s[46]} {s[47]}",
            f"      {s[48]} {s[49]} {s[50]}",
            f"      {s[51]} {s[52]} {s[53]}",
        ]
        return "\n".join(lines)

    @staticmethod
    def from_face_colors(faces_dict):
        """
        Create a cube from individual face colors.

        Args:
            faces_dict: Dict with keys 'U', 'R', 'F', 'D', 'L', 'B'
                       Each value is a 9-character string for that face

        Returns:
            Cube instance
        """
        face_order = ['U', 'R', 'F', 'D', 'L', 'B']
        state = ""
        for face in face_order:
            if face not in faces_dict:
                raise ValueError(f"Missing face: {face}")
            face_state = faces_dict[face]
            if len(face_state) != 9:
                raise ValueError(f"Face {face} must have 9 colors, got {len(face_state)}")
            state += face_state
        return Cube(state)

    def to_face_colors(self):
        """
        Convert cube state to a dict of face colors.

        Returns:
            Dict with keys 'U', 'R', 'F', 'D', 'L', 'B'
        """
        s = self.state
        return {
            'U': s[0:9],
            'R': s[9:18],
            'F': s[18:27],
            'D': s[27:36],
            'L': s[36:45],
            'B': s[45:54],
        }

    def apply_move(self, move):
        """
        Apply a single move to the cube state.
        
        Args:
            move: Move string (e.g., 'R', 'U'', 'F2')
            
        Modifies self.state in place.
        """
        # Extract base move and modifier
        base = move[0] if move[0].isalpha() else None
        modifier = move[1:] if len(move) > 1 else ''
        
        if not base or base not in self.FACES:
            raise ValueError(f"Invalid move: {move}")
        
        # Apply the move based on type
        if modifier == '2':
            self._rotate_face(base)
            self._rotate_face(base)
        elif modifier == "'":
            # Prime move = 3 clockwise rotations
            for _ in range(3):
                self._rotate_face(base)
        else:
            # Single clockwise rotation
            self._rotate_face(base)
    
    def _rotate_face(self, face):
        """
        Rotate a single face clockwise.
        
        Args:
            face: Face to rotate ('U', 'R', 'F', 'D', 'L', 'B')
        """
        s = list(self.state)
        
        if face == 'U':
            # Rotate U face clockwise
            # Cycle: F_top <- L_top <- B_top <- R_top <- F_top
            temp = [s[0], s[1], s[2]]
            s[0:3] = [s[36], s[37], s[38]]  # L top -> U
            s[36:39] = [s[45], s[46], s[47]]  # B top -> L top
            s[45:48] = [s[9], s[10], s[11]]  # R top -> B top
            s[9:12] = temp  # F top -> R top (saved in temp)
            # Rotate the U face itself
            s[0:9] = self._rotate_face_clockwise(s[0:9])
            
        elif face == 'D':
            # Rotate D face clockwise
            # Cycle: F_bottom -> R_bottom -> B_bottom -> L_bottom -> F_bottom
            temp = [s[24], s[25], s[26]]
            s[24:27] = [s[15], s[16], s[17]]  # R bottom -> F bottom
            s[15:18] = [s[33], s[34], s[35]]  # B bottom -> R bottom
            s[33:36] = [s[42], s[43], s[44]]  # L bottom -> B bottom
            s[42:45] = temp  # F bottom -> L bottom (saved in temp)
            # Rotate the D face itself
            s[27:36] = self._rotate_face_clockwise(s[27:36])
            
        elif face == 'L':
            # Rotate L face clockwise
            # Cycle: F_left <- U_left <- B_right <- D_left <- F_left
            temp = [s[18], s[21], s[24]]
            s[18], s[21], s[24] = s[0], s[3], s[6]  # U left -> F left
            s[0], s[3], s[6] = s[47], s[50], s[53]  # B right (reversed) -> U left
            s[47], s[50], s[53] = s[27], s[30], s[33]  # D left (reversed) -> B right
            s[27], s[30], s[33] = temp[0], temp[1], temp[2]  # F left -> D left
            # Rotate the L face itself
            s[36:45] = self._rotate_face_clockwise(s[36:45])
            
        elif face == 'R':
            # Rotate R face clockwise
            # Cycle: F_right -> U_right -> B_left -> D_right -> F_right
            temp = [s[20], s[23], s[26]]
            s[20], s[23], s[26] = s[6], s[3], s[0]  # U right (reversed) -> F right
            s[6], s[3], s[0] = s[29], s[32], s[35]  # B left (reversed) -> U right
            s[29], s[32], s[35] = s[26], s[23], s[20]  # D right (reversed) -> B left
            s[26], s[23], s[20] = temp[0], temp[1], temp[2]  # F right -> D right
            # Rotate the R face itself
            s[9:18] = self._rotate_face_clockwise(s[9:18])
            
        elif face == 'F':
            # Rotate F face clockwise
            # Cycle: U_bottom -> R_left -> D_top -> L_right -> U_bottom
            temp = [s[6], s[7], s[8]]
            s[6:9] = [s[36], s[39], s[42]]  # L right -> U bottom
            s[36], s[39], s[42] = s[27], s[28], s[29]  # D top -> L right
            s[27:30] = [s[11], s[14], s[17]]  # R left -> D top
            s[11], s[14], s[17] = temp[2], temp[1], temp[0]  # U bottom -> R left (reversed)
            # Rotate the F face itself
            s[18:27] = self._rotate_face_clockwise(s[18:27])
            
        elif face == 'B':
            # Rotate B face clockwise
            # Cycle: U_top <- R_right <- D_bottom <- L_left <- U_top
            temp = [s[0], s[1], s[2]]
            s[0:3] = [s[9], s[12], s[15]]  # R right -> U top
            s[9], s[12], s[15] = s[33], s[34], s[35]  # D bottom -> R right
            s[33:36] = [s[44], s[41], s[38]]  # L left -> D bottom
            s[38], s[41], s[44] = temp[2], temp[1], temp[0]  # U top -> L left (reversed)
            # Rotate the B face itself
            s[45:54] = self._rotate_face_clockwise(s[45:54])
        
        self.state = ''.join(s)
    
    @staticmethod
    def _rotate_face_clockwise(face_str):
        """
        Rotate a 3x3 face clockwise.
        
        Face layout:
        0 1 2
        3 4 5
        6 7 8
        
        After rotation:
        6 3 0
        7 4 1
        8 5 2
        """
        f = list(face_str)
        return ''.join([f[6], f[3], f[0], f[7], f[4], f[1], f[8], f[5], f[2]])

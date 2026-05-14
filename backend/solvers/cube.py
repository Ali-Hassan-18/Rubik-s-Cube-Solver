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

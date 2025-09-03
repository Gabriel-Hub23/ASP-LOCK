# solver_bridge.py
from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
import os

class AspBridge:
    """
    Bridge minimale:
    - set_static(maze) -> prepara rows/cols + wall(X,Y) (una sola volta)
    - decide_move(dynamic_facts: str) -> ritorna (nx, ny) o None
    """
    def __init__(self, dlv2_path: str, encoding_path: str):
        if not os.path.isfile(dlv2_path):
            raise FileNotFoundError(f"DLV2 non trovato: {dlv2_path}")
        if not os.path.isfile(encoding_path):
            raise FileNotFoundError(f"Encoding ASP non trovato: {encoding_path}")
        self.service = DLV2DesktopService(dlv2_path)
        self.encoding_path = encoding_path
        self.static_prog = None

    def set_static(self, maze):
        rows, cols = len(maze), len(maze[0])
        prog = ASPInputProgram()
        prog.add_files_path(self.encoding_path)
        prog.add_program(f"rows({rows}). cols({cols}).")
        walls = []
        for x in range(rows):
            for y in range(cols):
                if maze[x][y] == 1:  # 1 = muro
                    walls.append(f"wall({x},{y}).")
        if walls:
            prog.add_program("\n".join(walls))
        self.static_prog = prog

    def decide_move(self, dynamic_facts: str):
        """
        dynamic_facts: stringa con fatti ASP (pos_silly/2, pos_player/2, lock/2?, coin/2*, lives/1, score/1, tick/1, ecc.)
        ritorna (nx, ny) se trova move/2, altrimenti None
        """
        if self.static_prog is None:
            raise RuntimeError("Chiama set_static(maze) prima di decidere una mossa.")
        handler = DesktopHandler(self.service)
        handler.add_program(self.static_prog)

        dyn = ASPInputProgram()
        dyn.add_program(dynamic_facts)
        handler.add_program(dyn)

        out = handler.start_sync()

        try:
            for answer_set in out.get_answer_sets():
                for atom in answer_set.get_atoms():
                    if atom.startswith("move(") and atom.endswith(")"):
                        inside = atom[5:-1]
                        nx, ny = inside.split(",")
                        return int(nx), int(ny)
        except Exception:
            pass

        print("RAW OUTPUT:", out.get_output() if hasattr(out, "get_output") else out)

        return None

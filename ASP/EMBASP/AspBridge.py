# ASP/EMBASP/AspBridge.py — compatibile con varie versioni di EmbASP
# - Accetta set_static(rows, cols, walls) OPPURE set_static(maze)
# - Accetta decide_move((sx,sy),(px,py),locks?) OPPURE decide_move("pos_silly(...).\npos_player(...).")
# - Usa add_program (singolare) se add_programs non esiste
# - Pulisce l'handler in modo compatibile dopo ogni chiamata

from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
# Se usi iDLV: from embasp.specializations.idlv.desktop.idlv_desktop_service import IDLVDesktopService

from typing import Optional, Tuple, Iterable
import os

class AspBridge:
    def __init__(self, solver_path: str, encoding_path: str, debug: bool = True):
        if not os.path.exists(solver_path):
            raise FileNotFoundError(f"Solver non trovato: {solver_path}")
        if not os.path.exists(encoding_path):
            raise FileNotFoundError(f"Encoding ASP non trovato: {encoding_path}")
        self._solver_path = solver_path
        self._encoding_path = encoding_path
        self._debug = debug
        self._handler = DesktopHandler(DLV2DesktopService(solver_path))
        self._static_prog = ASPInputProgram()
        self._static_ready = False

    def log(self, *args):
        if self._debug:
            print("[ASP]", *args, flush=True)

    # -------- Helper compatibilità handler --------
    def _handler_add(self, prog: ASPInputProgram):
        if hasattr(self._handler, "add_programs"):
            self._handler.add_programs(prog)   # alcune versioni
        elif hasattr(self._handler, "add_program"):
            self._handler.add_program(prog)    # altre versioni (singolare)
        else:
            raise AttributeError("DesktopHandler non ha add_program(s)")

    def _handler_clear(self):
        for m in ("remove_all", "remove_programs", "clear"):
            if hasattr(self._handler, m):
                getattr(self._handler, m)()
                return
        # fallback: ricrea handler se nessun metodo esiste
        self._handler = DesktopHandler(DLV2DesktopService(self._solver_path))

    # -------- Static facts --------
    def set_static(self, *args):
        """
        Formati accettati:
          - set_static(rows, cols, walls)        # walls: Iterable[(x,y)]
          - set_static(maze)                     # maze: matrice 0/1 (1=muro)
        """
        self._static_prog = ASPInputProgram()
        self._static_prog.add_files_path(self._encoding_path)

        if len(args) == 1:
            maze = args[0]
            rows = len(maze)
            cols = len(maze[0]) if rows else 0
            walls = [(x, y) for x, row in enumerate(maze) for y, v in enumerate(row) if v == 1]
        elif len(args) == 3:
            rows, cols, walls = args
        else:
            raise TypeError("set_static vuole (rows, cols, walls) oppure (maze).")

        # celle
        for x in range(rows):
            for y in range(cols):
                self._static_prog.add_program(f"cell({x},{y}).")
        # muri
        for (wx, wy) in set(walls):
            self._static_prog.add_program(f"wall({wx},{wy}).")

        self._static_ready = True
        self.log("Static facts ready (cells/walls).")

    # -------- Dynamic query --------
    def decide_move(self, *args):
        """
        Formati accettati:
          - decide_move((sx,sy), (px,py), locks=Iterable[(x,y)] opzionale)
          - decide_move(dynamic_facts_str)
        """
        if not self._static_ready:
            raise RuntimeError("Chiama set_static(...) prima di decide_move(...)")

        dyn = ASPInputProgram()

        # Caso A: stringa di fatti dinamici
        if len(args) == 1 and isinstance(args[0], str):
            dynamic_facts = args[0]
            if dynamic_facts:
                dyn.add_program(dynamic_facts)

        # Caso B: tuple posizione + locks opzionali
        elif len(args) >= 2 and isinstance(args[0], tuple) and isinstance(args[1], tuple):
            (sx, sy) = args[0]
            (px, py) = args[1]
            locks: Iterable[Tuple[int, int]] = args[2] if len(args) >= 3 else ()
            dyn.add_program(f"pos_silly({sx},{sy}).")
            dyn.add_program(f"pos_player({px},{py}).")
            for (lx, ly) in set(locks or []):
                dyn.add_program(f"lock({lx},{ly}).")
        else:
            raise TypeError("decide_move vuole ((sx,sy),(px,py),locks?) oppure (dynamic_facts_str).")

        # Aggiungi programmi e risolvi
        self._handler_add(self._static_prog)
        self._handler_add(dyn)

        try:
            out = self._handler.start_sync()
        finally:
            self._handler_clear()

        # Parsing answer sets → cerca move(X,Y)
        try:
            for answer_set in out.get_answer_sets():
                for atom in answer_set.get_atoms():
                    s = str(atom)  # ESSENZIALE: atom -> stringa
                    if s.startswith("move(") and s.endswith(")"):
                        inside = s[5:-1]
                        parts = inside.split(",")
                        if len(parts) == 2:
                            nx = int(parts[0].strip())
                            ny = int(parts[1].strip())
                            self.log(f"MOVE({nx},{ny})")
                            return (nx, ny)
        except Exception as e:
            self.log("Errore parsing answer sets:", e)

        self.log("Nessuna mossa trovata.")
        return None

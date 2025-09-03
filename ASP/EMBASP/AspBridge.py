# ASP/EMBASP/AspBridge.py
# Bridge sincrono e robusto tra il gioco e DLV2/IDLV via EmbASP.
# - set_static(rows, cols, walls): prepara encoding + fatti statici (cell/wall)
# - decide_move((sx,sy), (px,py), locks): aggiunge i fatti dinamici (posizioni/lock),
#   invoca il solver e ritorna (nx, ny) se trova "move(X,Y).", altrimenti None.

from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
# Per iDLV usa: from embasp.specializations.idlv.desktop.idlv_desktop_service import IDLVDesktopService

from typing import Optional, Tuple, Iterable
import os

class AspBridge:
    def __init__(self, solver_path: str, encoding_path: str, debug: bool = False):
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

    def set_static(self, rows: int, cols: int, walls: Iterable[Tuple[int,int]]):
        # Prepara i fatti statici (griglia e muri) e carica l'encoding
        self._static_prog = ASPInputProgram()
        # Encoding
        self._static_prog.add_files_path(self._encoding_path)
        # Celle
        for x in range(cols):
            for y in range(rows):
                self._static_prog.add_program(f"cell({x},{y}).")
        # Muri
        for (wx, wy) in set(walls):
            self._static_prog.add_program(f"wall({wx},{wy}).")

        self._static_ready = True
        self.log("Static facts ready.")

    def decide_move(self, pos_silly: Tuple[int,int], pos_player: Tuple[int,int], locks: Iterable[Tuple[int,int]] = ()):
        # Aggiunge i fatti dinamici e interroga il solver. Ritorna (nx,ny) o None.
        if not self._static_ready:
            raise RuntimeError("Chiama set_static(...) prima di decide_move(...)")

        dyn = ASPInputProgram()
        sx, sy = pos_silly
        px, py = pos_player
        dyn.add_program(f"pos_silly({sx},{sy}).")
        dyn.add_program(f"pos_player({px},{py}).")
        for (lx, ly) in set(locks or []):
            dyn.add_program(f"lock({lx},{ly}).")

        self._handler.add_programs(self._static_prog)
        self._handler.add_programs(dyn)

        try:
            out = self._handler.start_sync()
        finally:
            # Importantissimo: pulire il handler per la prossima chiamata
            self._handler.remove_all()

        # Parsing answer sets
        try:
            for answer_set in out.get_answer_sets():
                for atom in answer_set.get_atoms():
                    s = str(atom)  # atomi come stringhe tipo "move(3,4)"
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
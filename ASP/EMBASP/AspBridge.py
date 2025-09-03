# ASP/EMBASP/AspBridge.py
# Bridge minimale tra il tuo gioco e DLV2/IDLV via EmbASP.
# - set_static(maze): carica encoding + fatti statici (rows/cols/wall)
# - decide_move(dynamic_facts): aggiunge i fatti dinamici (posizioni, lock, ecc.),
#   invoca il solver e ritorna (nx, ny) se trova "move(X,Y).", altrimenti None.

from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
# Se usi un wrapper diverso per i-dlv, sostituisci l'import sopra con quello del tuo servizio.

import os
from typing import Optional, Tuple


class AspBridge:
    def __init__(self, dlv2_path: str, encoding_path: str):
        """
        :param dlv2_path: percorso all'eseguibile del solver (es. ASP/DLV/dlv2.exe)
        :param encoding_path: percorso al file .asp (es. ASP/CODE/aiGabriel.asp)
        """
        if not os.path.isfile(dlv2_path):
            raise FileNotFoundError(f"DLV2 non trovato: {dlv2_path}")
        if not os.path.isfile(encoding_path):
            raise FileNotFoundError(f"Encoding ASP non trovato: {encoding_path}")

        # Inizializza il servizio Desktop per DLV2/IDLV
        self.service = DLV2DesktopService(dlv2_path)
        self.encoding_path = encoding_path

        # Programma "statico" (encoding + fatti che non cambiano)
        self.static_prog: Optional[ASPInputProgram] = None

    # ---------------------------------------------------------------------
    # Sezione STATIC: encoding + mappa (rows/cols/wall)
    # ---------------------------------------------------------------------
    def set_static(self, maze) -> None:
        """
        Prepara i fatti statici:
        - rows(R). cols(C).
        - wall(X,Y). per ogni cella con muro (valore == 1)
        Aggiunge anche il file di encoding ASP (self.encoding_path).
        """
        rows, cols = len(maze), len(maze[0])

        prog = ASPInputProgram()
        # Carica il file di encoding ASP
        prog.add_files_path(self.encoding_path)

        # Dimensioni
        prog.add_program(f"rows({rows}). cols({cols}).")

        # Muri (assumiamo 1 = muro nella tua matrice)
        wall_facts = []
        for x in range(rows):
            for y in range(cols):
                if maze[x][y] == 1:
                    wall_facts.append(f"wall({x},{y}).")
        if wall_facts:
            prog.add_program("\n".join(wall_facts))

        self.static_prog = prog

    # ---------------------------------------------------------------------
    # Chiamata sincrona al solver con i fatti dinamici (posizioni, lock, ecc.)
    # ---------------------------------------------------------------------
    def decide_move(self, dynamic_facts: str) -> Optional[Tuple[int, int]]:
        """
        Esegue una chiamata al solver aggiungendo i fatti dinamici correnti.
        :param dynamic_facts: stringa con fatti tipo:
            pos_silly(SX,SY).
            pos_player(PX,PY).
            lock(LX,LY).           (se presente)
            pos_silly_prev(PSX,PSY). (opzionale, se vuoi anti-rimbalzo)
            ...
        :return: (nx, ny) se trova un atomo move(X,Y)., altrimenti None
        """
        if self.static_prog is None:
            raise RuntimeError("Chiama set_static(maze) prima di decide_move().")

        handler = DesktopHandler(self.service)
        # Riusa i fatti statici (encoding + walls + rows/cols)
        handler.add_program(self.static_prog)

        # Aggiungi i fatti dinamici
        dyn = ASPInputProgram()
        if dynamic_facts:
            dyn.add_program(dynamic_facts)
        handler.add_program(dyn)

        # Avvio sincrono
        out = handler.start_sync()

        # DEBUG utile: stampa output grezzo del solver
        try:
            print("RAW OUTPUT:", out.get_output())
        except Exception:
            pass

        # Parsing semplice: cerca una singola mossa "move(X,Y)"
        try:
            for answer_set in out.get_answer_sets():
                for atom in answer_set.get_atoms():
                    # atom è tipicamente una stringa tipo "move(3,4)"
                    if atom.startswith("move(") and atom.endswith(")"):
                        inside = atom[5:-1]
                        nx_str, ny_str = inside.split(",")
                        nx = int(nx_str.strip())
                        ny = int(ny_str.strip())
                        return nx, ny
        except Exception:
            # se fallisce il parsing, ritorniamo None
            pass

        return None

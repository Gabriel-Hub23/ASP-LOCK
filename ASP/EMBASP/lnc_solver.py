# ASP/EMBASP/lnc_solver.py
# Minimal, robust Solver per Lock'n'Chase — usa DLV2 nativo tramite subprocess
# Fornisce API compatibili: set_state, startAsp, recallAsp, clear_ia

import tempfile
import subprocess
import os
import re
from typing import List, Tuple, Optional


class SolverLNC:

    def __init__(self, dlv_path: str, encoding_path: str, debug: bool = False, max_models: int = 1):
        # configurazione esterna
        self.dlv_path = dlv_path
        self.encoding_path = encoding_path
        self.debug = bool(debug)
        self.max_models = int(max_models)

        # opzionale: mappa numerica -> direzioni
        self.dir_map = {"0": "up", "1": "right", "2": "down", "3": "left"}

        # stato dinamico (coordinate Python: (row, col))
        self.self_pos: Tuple[int, int] = (0, 0)
        self.player_pos: Tuple[int, int] = (0, 0)
        self.walls: List[Tuple[int, int]] = []
        # previous position (optional), lock cells list, and optional grid size
        self.prev_pos: Optional[Tuple[int, int]] = None
        self.lock_cells: List[Tuple[int, int]] = []
        self.rows_cols: Optional[Tuple[int, int]] = None

        # carica encoding su stringa
        self._encoding = self.getEncoding(self.encoding_path)

    def set_state(self, self_pos: Tuple[int, int], player_pos: Tuple[int, int], walls: List[Tuple[int, int]], prev_pos: Optional[Tuple[int,int]] = None, rows_cols: Optional[Tuple[int,int]] = None, locks: Optional[List[Tuple[int,int]]] = None):
        self.self_pos = tuple(self_pos)
        self.player_pos = tuple(player_pos)
        self.walls = list(walls) if walls is not None else []
        self.prev_pos = tuple(prev_pos) if prev_pos is not None else None
        self.rows_cols = tuple(rows_cols) if rows_cols is not None else None
        self.lock_cells = list(locks) if locks is not None else []

    def startAsp(self):
        # mantenuta per compatibilità con API: non fa nulla nella versione nativa
        return

    def clear_ia(self):
        # mantenuta per compatibilità
        return

    # --- internals ---
    def __build_bundle(self) -> str:
        # positions in Python are (row, col) — convert to (col,row) for ASP
        sr, sc = self.self_pos
        pr, pc = self.player_pos
        sx, sy = int(sc), int(sr)
        px, py = int(pc), int(pr)

        facts = [f"self({sx},{sy}).", f"player({px},{py})."]
        facts += [f"wall({int(x)},{int(y)})." for (x, y) in self.walls]
        if self.prev_pos is not None:
            prr, pcc = self.prev_pos
            px_prev, py_prev = int(pcc), int(prr)
            facts.append(f"prev({px_prev},{py_prev}).")
        # emit locked cells if provided (convert row,col -> x=col,y=row)
        if self.lock_cells:
            for (lr, lc) in self.lock_cells:
                try:
                    lx, ly = int(lc), int(lr)
                    facts.append(f"locked({lx},{ly}).")
                except Exception:
                    continue
        # include rows/cols facts if provided (accept tuple (rows,cols))
        if self.rows_cols is not None:
            try:
                r, c = self.rows_cols
                r_i, c_i = int(r), int(c)
                facts.append(f"rows({r_i}).")
                facts.append(f"cols({c_i}).")
                # emit explicit numeric domain facts num(0). num(1). ... up to max(rows,cols)-1
                maxn = max(0, max(r_i, c_i) - 1)
                for i in range(0, maxn + 1):
                    facts.append(f"num({i}).")
            except Exception:
                # ignore if malformed
                pass
        bundle = [self._encoding, "% --- FACTS ---", "\n".join(facts), "% --- SHOW ---", "#show chosen_move/1."]
        if self.debug:
            print("--- BUNDLE ---")
            print("\n".join(bundle))
        return "\n\n".join(bundle)

    def __run_dlv(self, bundle_str: str, n_models: int = 1) -> Tuple[Optional[str], str]:
        """Scrive bundle su file temporaneo, chiama dlv2, ritorna (token, raw_stdout).
        token è il primo valore trovato dentro chosen_move(...)."""
        tmp = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".lp", delete=False, encoding="utf-8") as tf:
                tf.write(bundle_str)
                tmp = tf.name

            cmd = [self.dlv_path, f"-n={n_models}", tmp]

            if self.debug:
                print("DLV2 CMD:", " ".join(cmd))

            proc = subprocess.run(cmd, capture_output=True, text=True)
            out = proc.stdout or ""
            err = proc.stderr or ""

            if self.debug:
                print("DLV2 STDOUT:", out)
                if err.strip():
                    print("DLV2 STDERR:", err)

            # cerca chosen_move(...) nel stdout (case-insensitive)
            m = re.search(r"[cC]hosen_move\(([^)]+)\)", out)
            if not m:
                # fallback: controlla anche output in forma {Chosen_move(right)}
                m2 = re.search(r"\{\s*[cC]hosen_move\(([^)]+)\)\s*\}", out)
                if m2:
                    token = m2.group(1)
                else:
                    return None, out
            else:
                token = m.group(1)

            token = token.strip().strip('"').strip("'")
            # applica mappa numerica se presente
            if token in self.dir_map:
                return self.dir_map[token], out

            return token.lower(), out
        finally:
            try:
                if tmp and os.path.exists(tmp):
                    os.unlink(tmp)
            except Exception:
                pass

    def recallAsp(self) -> str:
        """Esegue il solver e restituisce una direzione valida; fallback 'up'."""
        bundle = self.__build_bundle()
        # Prova con max_models impostato
        token, raw = self.__run_dlv(bundle, n_models=self.max_models)
        if self.debug:
            print("PARSED TOKEN:", token)
        if token and token in ("up", "down", "left", "right"):
            return token

        # se token non valido, prova a cercare esplicitamente nelle righe di output (case-insensitive)
        found = re.search(r"(?i)chosen_move\((up|down|left|right)\)", raw)
        if found:
            return found.group(1).lower()

        # ultima risorsa: prova con n_models=0 (tutte le soluzioni)
        token2, raw2 = self.__run_dlv(bundle, n_models=0)
        if self.debug:
            print("SECOND PASS TOKEN:", token2)
        if token2 and token2 in ("up", "down", "left", "right"):
            return token2

        # fallback
        return "up"

    @staticmethod
    def getEncoding(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
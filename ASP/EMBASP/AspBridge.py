# AspBridge.py (DLV2)
# ------------------------------------------------------------
# Bridge per usare DLV2 con EmbASP (Python).
# - Carica un programma statico .asp (regole)
# - Aggiunge fatti dinamici (self/2, player/2, wall/2)
# - Esegue DLV2 e restituisce chosen_move(up|down|left|right)
#
# USO:
#   from ASP.EMBASP.AspBridge import AspBridge
#   asp = AspBridge(dlv2_path=r"ASP\DLV\dlv2.exe", static_program_path=r"ASP\mycode.asp")
#   move = asp.decide_move((sx,sy), (px,py), walls=[(x1,y1), (x2,y2)])
#   print(move)  # "up" | "down" | "left" | "right" | None
# ------------------------------------------------------------

from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.languages.asp.answer_sets import AnswerSets
from embasp.base.option_descriptor import OptionDescriptor

# >>> DLV2 <<<
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService


class AspBridge:
    def __init__(self, dlv2_path: str, static_program_path: str, silent: bool = True, max_models: int = 1):
        """
        :param dlv2_path: path all'eseguibile DLV2 (p.es. 'ASP/DLV/dlv2.exe' su Windows)
        :param static_program_path: path al file .asp con le regole statiche
        :param silent: se True aggiunge opzione '--silent'
        :param max_models: numero massimo di answer set (default 1)
        """
        self.dlv2_path = dlv2_path
        self.static_program_path = static_program_path
        self.silent = silent
        self.max_models = max(1, int(max_models))

    def _build_handler(self) -> DesktopHandler:
        service = DLV2DesktopService(self.dlv2_path)
        handler = DesktopHandler(service)

        # Opzioni: devono essere OptionDescriptor (non stringhe)
        # DLV2 accetta in genere '--silent' e '-n=<k>'
        if self.silent:
            handler.add_option(OptionDescriptor("--silent"))
        handler.add_option(OptionDescriptor(f"-n={self.max_models}"))

        return handler

    def decide_move(self, self_pos, player_pos, walls):
        """
        :param self_pos: (sx, sy)  -> interi
        :param player_pos: (px, py) -> interi
        :param walls: iterable di (x, y) -> interi
        :return: 'up' | 'down' | 'left' | 'right' | None
        """
        # Costruisci handler nuovo ad ogni chiamata per evitare stato "sporco"
        handler = self._build_handler()

        # 1) Programma statico da file
        static_prog = ASPInputProgram()
        static_prog.add_files_path(self.static_program_path)
        handler.add_program(static_prog)

        # 2) Fatti dinamici
        sx, sy = self_pos
        px, py = player_pos

        # Controllo "soft": assicuriamoci che siano interi (evita 5.0)
        try:
            sx, sy, px, py = int(sx), int(sy), int(px), int(py)
        except Exception:
            pass

        facts = []
        facts.append(f"self({sx},{sy}).\n")
        facts.append(f"player({px},{py}).\n")
        for (wx, wy) in walls:
            try:
                wx, wy = int(wx), int(wy)
            except Exception:
                pass
            facts.append(f"wall({wx},{wy}).\n")

        dyn_prog = ASPInputProgram()
        dyn_prog.add_program("".join(facts))
        handler.add_program(dyn_prog)

        # 3) Esecuzione sincrona
        output = handler.start_sync()

        # 4) Parsing robusto
        # a) se non è un AnswerSets, prova a cercare il testo 'chosen_move(...)'
        if not isinstance(output, AnswerSets):
            txt = (str(output) or "").lower()
            for d in ("up", "down", "left", "right"):
                if f"chosen_move({d})" in txt:
                    return d
            return None

        # b) se è AnswerSets, scorri gli atomi
        answer_sets = output.get_answer_sets() or []
        for ans in answer_sets:
            for atom in ans.get_atoms():
                s = str(atom).lower()
                if s.startswith("chosen_move(") and s.endswith(")"):
                    return s[12:-1]  # estrae up/down/left/right

        return None

# AspBridge.py
# ------------------------------------------------------------
# Bridge minimale per usare DLV (o DLV2) con EmbASP da Python.
# - Aggiunge un programma statico da file .asp
# - Costruisce i fatti dinamici (self, player, wall)
# - Esegue il solver e restituisce chosen_move(up|down|left|right)
#
# USO:
#   from ASP.EMBASP.AspBridge import AspBridge
#   asp = AspBridge(dlv_path="ASP/DLV/dlv.exe", static_program_path="ASP/mycode.asp")
#   move = asp.decide_move((sx,sy), (px,py), walls=[(x1,y1), (x2,y2)])
#   print(move)  # "up" | "down" | "left" | "right" | None
# ------------------------------------------------------------

from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.languages.asp.answer_sets import AnswerSets
from embasp.base.option_descriptor import OptionDescriptor

# Se usi DLV classico:
from embasp.specializations.dlv.desktop.dlv_desktop_service import DLVDesktopService
# Se usi DLV2, commenta la riga sopra e decommenta questa:
# from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService


class AspBridge:
    def __init__(self, dlv_path: str, static_program_path: str, use_dlv2: bool = False, silent: bool = True):
        """
        :param dlv_path: path all'eseguibile del solver (es. 'ASP/DLV/dlv.exe' su Windows)
        :param static_program_path: path al file .asp con le regole statiche
        :param use_dlv2: se True usa DLV2DesktopService, altrimenti DLVDesktopService
        :param silent: se True aggiunge opzione -silent
        """
        self.dlv_path = dlv_path
        self.static_program_path = static_program_path
        self.use_dlv2 = use_dlv2
        self.silent = silent

    def _build_handler(self) -> DesktopHandler:
        # Crea il service corretto in base al solver scelto
        if self.use_dlv2:
            # service = DLV2DesktopService(self.dlv_path)
            raise NotImplementedError("Imposta l'import di DLV2DesktopService e rimuovi questo raise se usi DLV2.")
        else:
            service = DLVDesktopService(self.dlv_path)

        handler = DesktopHandler(service)

        # Opzioni: devono essere OptionDescriptor, NON stringhe
        if self.silent:
            handler.add_option(OptionDescriptor("-silent"))
        handler.add_option(OptionDescriptor("-n=1"))  # una sola answer set basta

        return handler

    def decide_move(self, self_pos, player_pos, walls):
        """
        :param self_pos: tuple (sx, sy)
        :param player_pos: tuple (px, py)
        :param walls: iterable di (x, y) per i muri
        :return: 'up' | 'down' | 'left' | 'right' | None
        """
        handler = self._build_handler()

        # 1) Programma statico da file
        static_prog = ASPInputProgram()
        static_prog.add_files_path(self.static_program_path)
        handler.add_program(static_prog)

        # 2) Fatti dinamici
        dyn_prog = ASPInputProgram()
        sx, sy = self_pos
        px, py = player_pos

        facts = []
        facts.append(f"self({sx},{sy}).\n")
        facts.append(f"player({px},{py}).\n")
        for (wx, wy) in walls:
            facts.append(f"wall({wx},{wy}).\n")

        dyn_prog.add_program("".join(facts))
        handler.add_program(dyn_prog)

        # 3) Esegui sincrono
        output = handler.start_sync()

        # 4) Parsing robusto: cerca chosen_move(dir)
        # Se non arriva un AnswerSets (capita con errori), prova parsing testuale.
        if not isinstance(output, AnswerSets):
            txt = str(output).lower()
            for d in ("up", "down", "left", "right"):
                if f"chosen_move({d})" in txt:
                    return d
            return None

        # Answer sets OK: scorri gli atomi alla ricerca di chosen_move(...)
        answer_sets = output.get_answer_sets()
        if not answer_sets:
            return None

        for ans in answer_sets:
            for atom in ans.get_atoms():
                s = str(atom).lower()
                if s.startswith("chosen_move(") and s.endswith(")"):
                    return s[12:-1]  # estrae la direzione tra le parentesi

        return None

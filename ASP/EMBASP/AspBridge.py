# AspBridge.py (DLV2) — completo
# - Carica il .asp statico
# - Passa i fatti dinamici (self/2, player/2, wall/2)
# - Esegue DLV2 via EmbASP
# - Estrae chosen_move(up|down|left|right) dagli AnswerSets
# - Debug opzionale (stampa fatti e raw output)
# - Fallback Python se il solver non restituisce nulla

from typing import Iterable, Tuple, Optional

from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.languages.asp.answer_sets import AnswerSets
from embasp.base.option_descriptor import OptionDescriptor
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService


class AspBridge:
    def __init__(
        self,
        dlv2_path: str,
        static_program_path: str,
        silent: bool = True,
        max_models: int = 1,
        debug: bool = False,
        add_filter: bool = True,
    ):
        """
        :param dlv2_path: path all'eseguibile DLV2 (es. r'ASP\\DLV\\dlv2.exe')
        :param static_program_path: path al file .asp con le regole statiche
        :param silent: se True aggiunge --silent
        :param max_models: -n=k (quanti answer set cercare)
        :param debug: se True stampa fatti e raw output
        :param add_filter: se True aggiunge --filter=chosen_move/1 e --no-facts (pulizia stdout)
        """
        self.dlv2_path = dlv2_path
        self.static_program_path = static_program_path
        self.silent = bool(silent)
        self.max_models = max(1, int(max_models))
        self.debug = bool(debug)
        self.add_filter = bool(add_filter)

    def _build_handler(self) -> DesktopHandler:
        service = DLV2DesktopService(self.dlv2_path)
        handler = DesktopHandler(service)
        # Opzioni: devono essere OptionDescriptor (NON stringhe)
        if self.silent:
            handler.add_option(OptionDescriptor("--silent"))
        handler.add_option(OptionDescriptor(f"-n={self.max_models}"))
        if self.add_filter:
            handler.add_option(OptionDescriptor("--filter=chosen_move/1"))
            handler.add_option(OptionDescriptor("--no-facts"))
        return handler

    @staticmethod
    def _python_fallback_move(
        self_pos: Tuple[int, int], walls: Iterable[Tuple[int, int]]
    ) -> str:
        """Se il solver non restituisce nulla, scegli una mossa semplice evitando i muri."""
        sx, sy = self_pos
        W = set((int(x), int(y)) for (x, y) in walls)
        candidates = [
            ("up", (sx, sy - 1)),
            ("down", (sx, sy + 1)),
            ("left", (sx - 1, sy)),
            ("right", (sx + 1, sy)),
        ]
        for d, (nx, ny) in candidates:
            if (nx, ny) not in W:
                return d
        return "up"  # bloccato da muri su tutti i lati: scegli comunque una direzione

    def decide_move(
        self,
        self_pos: Tuple[int, int],
        player_pos: Tuple[int, int],
        walls: Iterable[Tuple[int, int]],
    ) -> Optional[str]:
        """
        :return: 'up' | 'down' | 'left' | 'right' (mai None grazie al fallback)
        """
        handler = self._build_handler()

        # Programma statico da file
        static_prog = ASPInputProgram()
        static_prog.add_files_path(self.static_program_path)
        handler.add_program(static_prog)

        # Fatti dinamici (forziamo int per evitare 5.0)
        sx, sy = map(int, self_pos)
        px, py = map(int, player_pos)

        facts = []
        facts.append(f"self({sx},{sy}).\n")
        facts.append(f"player({px},{py}).\n")
        for (wx, wy) in walls:
            facts.append(f"wall({int(wx)},{int(wy)}).\n")

        dyn_prog = ASPInputProgram()
        dyn_prog.add_program("".join(facts))
        handler.add_program(dyn_prog)

        if self.debug:
            print("=== FATTI INVIATI A DLV2 ===")
            print("".join(facts))

        # Esecuzione sincrona
        output = handler.start_sync()

        if self.debug:
            print("=== DLV2 RAW OUTPUT ===")
            print(str(output))

        # 1) Parsing via API
        if isinstance(output, AnswerSets):
            for ans in output.get_answer_sets() or []:
                for atom in ans.get_atoms():
                    s = str(atom).lower().strip()
                    if s.startswith("chosen_move(") and s.endswith(")"):
                        return s[12:-1]  # up/down/left/right

        # 2) Fallback: ricerca testuale nel raw output (es. in caso di errori di tipo)
        txt = (str(output) or "").lower()
        for d in ("up", "down", "left", "right"):
            if f"chosen_move({d})" in txt:
                return d

        # 3) Ultimo paracadute: fallback Python
        return self._python_fallback_move((sx, sy), walls)

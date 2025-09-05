# ASP/EMBASP/AspBridge.py
# ------------------------------------------------------------
# Bridge EMBASP per DLV2 (dlv2*.exe)
# - Carica il file .asp statico
# - Passa i fatti dinamici (self/2, player/2, wall/2)
# - Esegue DLV2 via EmbASP
# - Estrae chosen_move(up|down|left|right) dagli AnswerSets
# - Compatibile con parametri legacy: use_filter, force_inline_static (ignorato)
# ------------------------------------------------------------

from typing import Iterable, Tuple, Optional
from pathlib import Path

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
        add_filter: bool = False,
        use_filter: Optional[bool] = None,        # alias accettato
        force_inline_static: Optional[bool] = None,  # alias accettato (IGNORATO)
    ):
        """
        :param dlv2_path: percorso all'eseguibile DLV2 (es. r'ASP\\DLV\\dlv2.1.2.exe')
        :param static_program_path: percorso al file .asp con le regole
        :param silent: se True aggiunge --silent
        :param max_models: -n=k
        :param debug: se True stampa fatti e answer sets
        :param add_filter: se True usa --filter=chosen_move/1 (solo stdout)
        :param use_filter: alias di add_filter (retro-compatibilità)
        :param force_inline_static: accettato ma ignorato (retro-compatibilità)
        """
        self.dlv2_path = str(Path(dlv2_path).resolve())
        self.static_program_path = str(Path(static_program_path).resolve())
        self.silent = bool(silent)
        self.max_models = max(1, int(max_models))
        self.debug = bool(debug)
        # usa use_filter se passato, altrimenti add_filter
        self.add_filter = bool(add_filter) if use_filter is None else bool(use_filter)
        # force_inline_static intenzionalmente ignorato

        if not Path(self.dlv2_path).exists():
            raise FileNotFoundError(f"DLV2 non trovato: {self.dlv2_path}")
        if not Path(self.static_program_path).exists():
            raise FileNotFoundError(f"File ASP non trovato: {self.static_program_path}")

    # toggle opzionali
    def set_debug(self, enabled: bool = True) -> None:
        self.debug = bool(enabled)

    def set_silent(self, enabled: bool = True) -> None:
        self.silent = bool(enabled)

    def set_filter(self, enabled: bool = True) -> None:
        self.add_filter = bool(enabled)

    def set_max_models(self, k: int = 1) -> None:
        self.max_models = max(1, int(k))

    def _build_handler(self) -> DesktopHandler:
        service = DLV2DesktopService(self.dlv2_path)
        handler = DesktopHandler(service)
        # Opzioni come OptionDescriptor (NON stringhe)
        if self.silent:
            handler.add_option(OptionDescriptor("--silent"))
        handler.add_option(OptionDescriptor(f"-n={self.max_models}"))
        if self.add_filter:
            handler.add_option(OptionDescriptor("--filter=chosen_move/1"))
            handler.add_option(OptionDescriptor("--no-facts"))
        return handler

    def decide_move(
        self,
        self_pos: Tuple[int, int],
        player_pos: Tuple[int, int],
        walls: Iterable[Tuple[int, int]],
    ) -> Optional[str]:
        """
        Ritorna: 'up' | 'down' | 'left' | 'right' | None
        """
        handler = self._build_handler()

        # Programma statico
        static_prog = ASPInputProgram()
        static_prog.add_files_path(self.static_program_path)
        handler.add_program(static_prog)

        # Fatti dinamici (forza int)
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
            print("=== DLV2 PATH ===", self.dlv2_path)
            print("=== ASP FILE  ===", self.static_program_path)
            print("=== FACTS ===\n", "".join(facts))

        # Esecuzione
        output = handler.start_sync()

        # Parsing AnswerSets
        if isinstance(output, AnswerSets):
            answer_sets = output.get_answer_sets() or []
            if self.debug:
                for i, ans in enumerate(answer_sets, 1):
                    atoms = ", ".join(str(a) for a in ans.get_atoms())
                    print(f"AS #{i}: {atoms}")
            for ans in answer_sets:
                for atom in ans.get_atoms():
                    s = str(atom).strip().lower()
                    if s.startswith("chosen_move(") and s.endswith(")"):
                        return s[12:-1]

        if self.debug:
            print("=== NESSUNA chosen_move(...) negli AnswerSets ===")
            print("RAW:", str(output))
        return None

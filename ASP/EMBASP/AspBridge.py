# AspBridge.py
from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.languages.asp.answer_sets import AnswerSets

# Se usi DLV classico:
from embasp.specializations.dlv.desktop.dlv_desktop_service import DLVDesktopService
# Se invece usi DLV2, commenta la riga sopra e usa:
# from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

class AspBridge:
    def __init__(self, dlv_path: str, static_program_path: str):
        """
        dlv_path: path all'eseguibile DLV, es. 'ASP/DLV/dlv.exe' (Windows) o 'ASP/DLV/dlv' (Linux/macOS)
        static_program_path: file .asp con le regole statiche (es. 'ASP/mycode.asp')
        """
        self.dlv_path = dlv_path
        self.static_program_path = static_program_path

    def _build_handler(self):
        # Scegli UN solo service in base al solver che stai usando
        service = DLVDesktopService(self.dlv_path)
        # Oppure per DLV2:
        # service = DLV2DesktopService(self.dlv_path)

        handler = DesktopHandler(service)
        # Opzioni comuni
        handler.add_option("-silent")
        handler.add_option("-n=1")
        return handler

    def decide_move(self, self_pos, player_pos, walls):
        """
        Ritorna: 'up' | 'down' | 'left' | 'right' | None
        """
        handler = self._build_handler()

        # Programma statico da file
        static_prog = ASPInputProgram()
        static_prog.add_files_path(self.static_program_path)
        handler.add_program(static_prog)

        # Fatti dinamici
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

        # Esegui
        output = handler.start_sync()

        # Parse robusto
        if not isinstance(output, AnswerSets):
            txt = str(output).lower()
            for d in ("up","down","left","right"):
                if f"chosen_move({d})" in txt:
                    return d
            return None

        for ans in output.get_answer_sets():
            for atom in ans.get_atoms():
                s = str(atom).lower()
                if s.startswith("chosen_move(") and s.endswith(")"):
                    return s[12:-1]  # estrae up/down/left/right
        return None

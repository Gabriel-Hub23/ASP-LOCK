# AspBridge.py
from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.languages.asp.answer_sets import AnswerSets

class AspBridge:
    def __init__(self, dlv_path: str, static_program_path: str):
        """
        dlv_path: path all'eseguibile DLV (es. 'ASP/DLV/dlv.exe' su Windows)
        static_program_path: file .asp con le regole statiche (es. 'ASP/mycode.asp')
        """
        self.dlv_path = dlv_path
        self.static_program_path = static_program_path

    def decide_move(self, self_pos, player_pos, walls):
        """
        self_pos: tuple (sx, sy)
        player_pos: tuple (px, py)
        walls: iterable di (x,y) con i muri
        Ritorna una stringa tra: 'up','down','left','right' (se trovata), altrimenti None.
        """
        # 1) Crea un handler NUOVO ad ogni chiamata (eviti residui di programmi precedenti)
        handler = DesktopHandler(self.dlv_path)

        # 2) Aggiungi il programma statico (dal file)
        static_prog = ASPInputProgram()
        static_prog.add_files_path(self.static_program_path)
        handler.add_program(static_prog)  # <-- ATTENZIONE: add_program (singolare)

        # 3) Aggiungi i fatti dinamici
        dyn_prog = ASPInputProgram()
        sx, sy = self_pos
        px, py = player_pos

        # NB: ogni fatto termina con il punto e preferibilmente newline
        facts = []
        facts.append(f"self({sx},{sy}).\n")
        facts.append(f"player({px},{py}).\n")
        for (wx, wy) in walls:
            facts.append(f"wall({wx},{wy}).\n")

        dyn_prog.add_program("".join(facts))
        handler.add_program(dyn_prog)

        # 4) Opzioni consigliate
        handler.add_option("-silent")
        handler.add_option("-n=1")  # una sola answer set basta

        # 5) Esegui sincrono
        output = handler.start_sync()

        # 6) Estrai l'atom desiderato: chosen_move(up|down|left|right)
        if not isinstance(output, AnswerSets):
            # Se per qualche motivo non è AnswerSets, ripiega su to_string()
            txt = str(output).lower()
            for d in ("up","down","left","right"):
                if f"chosen_move({d})" in txt:
                    return d
            return None

        for ans in output.get_answer_sets():
            for atom in ans.get_atoms():
                atom_s = str(atom).lower()
                if atom_s.startswith("chosen_move(") and atom_s.endswith(")"):
                    return atom_s[12:-1]  # estrae la direzione
        return None

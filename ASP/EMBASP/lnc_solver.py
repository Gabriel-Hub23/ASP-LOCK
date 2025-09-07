# ASP/EMBASP/lnc_solver.py
# ------------------------------------------------------------
# Solver EmbASP per Lock'n'Chase
# - Stessa struttura del tuo esempio (startAsp / recallAsp / clear_ia)
# - Mapping predicati: self/2, player/2, wall/2, chosen_move/1
# - chosen_move(D) letto come SymbolicConstant e normalizzato in stringa
# - Nessuna modifica al programma ASP (.asp)
# ------------------------------------------------------------

from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.languages.asp.asp_mapper import ASPMapper
from embasp.languages.asp.answer_sets import AnswerSets
from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.predicate import Predicate
from embasp.languages.asp.symbolic_constant import SymbolicConstant
from embasp.base.option_descriptor import OptionDescriptor
import tempfile, subprocess, os
from embasp.languages.asp.asp_mapper import ASPMapper
import re




from ASP.EMBASP.predicates import *

# =============== SOLVER LOCK’N’CHASE ==================

class SolverLNC:
    """
    Uso tipico:
        ai = SolverLNC(
        dlv_path="ASP/DLV/dlv2.exe",
        encoding_path="ASP/CODE/lnc_ai.asp",   # <-- deve essere questo
        debug=True
)

        )
        ai.set_state(self_pos=(sx,sy), player_pos=(px,py), walls=[(x,y),...])
        ai.startAsp()
        move = ai.recallAsp()   # "up"/"down"/"left"/"right"
    """
    def __init__(self, dlv_path: str, encoding_path: str, debug: bool = True, max_models: int = 1):
        self.debug = bool(debug)
        self.max_models = int(max_models)
        self.dlv_path = dlv_path
        self.encoding_path = encoding_path

        self.dir_map={"0":"up","1":"right","2":"down","3":"left"}

        # Stato dinamico
        self.self_pos = (0, 0)
        self.player_pos = (0, 0)
        self.walls = []   # lista di tuple (x,y)

        # Handler DLV2
        self.__handler = DesktopHandler(DLV2DesktopService(self.dlv_path))
        self.__program = ASPInputProgram()
        self.__index = None  # facoltativo, per compat con remove_program_from_id

        # Registro le classi una sola volta
        mapper = ASPMapper.get_instance()
        mapper.register_class(Self)
        mapper.register_class(Player)
        mapper.register_class(Wall)
        mapper.register_class(ChosenMove)

        # Carica l’encoding
        self.__encoding = self.getEncoding(self.encoding_path)

    # -------- API compatibile col tuo stile --------

    def set_state(self, self_pos, player_pos, walls):
        """Imposta lo stato corrente (posizioni e muri)."""
        self.self_pos = tuple(self_pos)
        self.player_pos = tuple(player_pos)
        self.walls = list(walls) if walls is not None else []

    '''
    def startAsp(self):
        """Inizializza (handler pulito), costruisce programma, aggiunge #show e opzioni."""
        # Handler NUOVO ogni volta (niente residui di programmi/opzioni)
        self.__handler = DesktopHandler(DLV2DesktopService(self.dlv_path))

        # Programma principale: encoding + facts mappati
        self.__program = ASPInputProgram()
        self.__init_program()
        self.__handler.add_program(self.__program)


        # Opzioni minime (NO -filter, per non sopprimere debug)
        try:
            self.__handler.add_option(OptionDescriptor("-silent"))
            self.__handler.add_option(OptionDescriptor(f"-n=0"))
        except Exception:
            pass
        '''
    
    def startAsp(self):
        # handler nuovo pulito
        self.__handler = DesktopHandler(DLV2DesktopService(self.dlv_path))

        # prepara il programma (scrive il bundle temp e fa add_files_path)
        self.__init_program()
        self.__handler.add_program(self.__program)

        # opzioni minime
        try:
            self.__handler.add_option(OptionDescriptor("-silent"))
            self.__handler.add_option(OptionDescriptor(f"-n={self.max_models}"))  # per vedere tutti: -n=0
            # niente -filter, lasciamo visibile chosen_move via #show
        except Exception:
            pass


    def __native_get_move(self, n_models: int = 1):
        """Esegue DLV2 nativo su (encoding+facts+#show) e ritorna la PRIMA chosen_move trovata.
        Ritorna la stringa grezza dentro le parentesi (es. 'right' o '3').
        Se self.dir_map è definita, la usa per mappare: es. '1' -> 'right'."""
        # --- costruisci il bundle identico a quello passato a EmbASP ---
        mapper = ASPMapper.get_instance()
        sx, sy = self.self_pos
        px, py = self.player_pos

        facts_txt = [
            mapper.get_string(Self(sx, sy)) + ".",
            mapper.get_string(Player(px, py)) + ".",
        ] + [mapper.get_string(Wall(x, y)) + "." for (x, y) in self.walls]

        bundle = []
        bundle.append(self.__encoding)
        bundle.append("\n% --- FACTS ---")
        bundle.append("\n".join(facts_txt))
        bundle.append("\n% --- SHOW ---")
        bundle.append("#show chosen_move/1.\n")
        bundle_str = "\n".join(bundle)

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".lp", delete=False, encoding="utf-8") as tf:
                tf.write(bundle_str)
                tmp_path = tf.name

            cmd = [self.dlv_path, f"-n={n_models}", tmp_path]
            # usa -silent se vuoi output più pulito:
            # cmd.insert(1, "-silent")

            proc = subprocess.run(cmd, capture_output=True, text=True)
            out = proc.stdout or ""

            # cerca chosen_move(<token>)
            m = re.search(r"chosen_move\(([^)]+)\)", out)
            if not m:
                return None

            token = m.group(1)  # es. 'right' oppure '3'

            # normalizza: togli eventuali apici/spazi
            token = token.strip().strip('"').strip("'")

            # se hai una mappa numerica -> testuale, applicala
            if self.dir_map and token in self.dir_map:
                return self.dir_map[token]

            return token
        finally:
            try:
                if tmp_path:
                    os.unlink(tmp_path)
            except Exception:
                pass


    def recallAsp(self):
        """Esegue il solver e restituisce la direzione ('up','down','left','right')."""
        # Se in precedenza avevi salvato id programma, lo rimuovi (optional)
        if self.__index is not None:
            try:
                self.__handler.remove_program_from_id(self.__index)
            except Exception:
                pass

        answer_sets: AnswerSets = self.__handler.start_sync()

        oas = answer_sets.get_answer_sets()
        if not oas:
            # fallback: prendi la mossa direttamente da DLV2 nativo
            move_token = self.__native_get_move(n_models=1)  # prende la prima
            if self.debug:
                print("AS#0 → native chosen_move:", move_token)
            # se hai dir_map, __native_get_move l'ha già applicata; altrimenti puoi mapparla qui
            # Se è già una di up/down/left/right ok; se è un numero e non hai mappa, restituiscilo pure o metti un default
            if move_token in ("up", "down", "left", "right"):
                return move_token
            # prova una mappa di default se vuoi (EDITALA con la tua convenzione)
            


        # ===== DEBUG: stampa gli answer set in chiaro =====
        try:
            mapper = ASPMapper.get_instance()
            print("---------------=== ANSWER SETS (text) ===--------------")
            idx = 0
            for ans in answer_sets.get_answer_sets():
                idx += 1
                out = []
                for a in ans.get_atoms():
                    try:
                        # prova a serializzare l’atomo con il mapper (restituisce 'pred(args)')
                        s = mapper.get_string(a)
                    except Exception:
                        s = str(a)
                    out.append(s)
                print(f"AS#{idx}: {out}")
            if idx == 0:
                print("AS#0: <no answer sets>")
        except Exception as e:
            print("DEBUG TEXT DUMP ERROR:", e)
        # ================================================

        # ===== ESTRAZIONE MOSSA =====
        # a) tentativo “pulito” via mapper (SymbolicConstant)
        for ans in answer_sets.get_answer_sets():
            for a in ans.get_atoms():
                # importa ChosenMove se è in un altro modulo / stessa classe tua
                if a.__class__.__name__ == "ChosenMove":
                    val = None
                    try:
                        val = a.get_d()
                    except Exception:
                        val = None

                    # Normalizza SymbolicConstant -> stringa
                    direction = None
                    if val is not None:
                        for m in ("get_value", "get_symbol", "get_name"):
                            if hasattr(val, m):
                                try:
                                    direction = getattr(val, m)()
                                    break
                                except Exception:
                                    pass
                        if direction is None:
                            for attr in ("value", "symbol", "name"):
                                if hasattr(val, attr):
                                    direction = getattr(val, attr)
                                    break
                        if direction is None:
                            direction = str(val)

                    if direction in ("up", "down", "left", "right"):
                        return direction



        # Debug: stampa answer set
        if self.debug:
            print("=== ANSWER SETS (raw objects) ===")
            try:
                for i, ans in enumerate(answer_sets.get_answer_sets(), 1):
                    print(f"AS#{i}: {[str(a) for a in ans.get_atoms()]}")
            except Exception as e:
                print("DEBUG ANSWER PRINT ERROR:", e)

        # Estrai chosen_move/1
        move = self.__extract_move(answer_sets)
        if self.debug:
            print("Mossa scelta:", move)

        
        # dopo aver finito di usare answer_sets...
        try:
            if hasattr(self, "_tmp_bundle") and self._tmp_bundle:
                os.unlink(self._tmp_bundle.name)
                self._tmp_bundle = None
        except Exception:
            pass


        # Fallback a prova di bomba
        return move if move in ("up", "down", "left", "right") else "up"

    def clear_ia(self):
        """Svuota l'handler (come nel tuo esempio)."""
        try:
            self.__handler.remove_all()
        except Exception:
            pass

    # -------- Helpers interni --------
    def __init_program(self):
        """Crea un file temporaneo con encoding + fatti + #show e lo passa a DLV2 come file."""
        # Costruisci facts in testo (come già fai ora)
        mapper = ASPMapper.get_instance()
        sx, sy = self.self_pos
        px, py = self.player_pos

        facts_txt = [
            mapper.get_string(Self(sx, sy)) + ".",
            mapper.get_string(Player(px, py)) + ".",
        ] + [mapper.get_string(Wall(x, y)) + "." for (x, y) in self.walls]

        # Bundle = regole + fatti + show (senza toccare il tuo .asp)
        bundle = []
        bundle.append(self.__encoding)
        bundle.append("\n% --- FACTS ---")
        bundle.append("\n".join(facts_txt))
        bundle.append("\n% --- SHOW ---")
        bundle.append("#show chosen_move/1.\n")  # puoi aggiungere anche self/player/wall se vuoi vederli

        bundle_str = "\n".join(bundle)

        # Scrivi il bundle su file temp e passalo come file a EmbASP
        self._tmp_bundle = tempfile.NamedTemporaryFile("w", suffix=".lp", delete=False, encoding="utf-8")
        self._tmp_bundle.write(bundle_str)
        self._tmp_bundle.flush()
        self._tmp_bundle.close()

        # Pulisci e ricrea l'ASPInputProgram, poi passa il FILE, non la stringa
        self.__program = ASPInputProgram()
        self.__program.add_files_path(self._tmp_bundle.name)

        if self.debug:
            print("=== BUNDLE PATH ===", self._tmp_bundle.name)
            print("=== BUNDLE CONTENT ===\n", bundle_str)
    '''
    def __init_program(self):
        # Regole
        self.__program.add_program(self.__encoding)

        # Fatti dinamici come TESTO (bypass add_object_input)
        mapper = ASPMapper.get_instance()
        sx, sy = self.self_pos
        px, py = self.player_pos

        facts_txt = []
        facts_txt.append(mapper.get_string(Self(sx, sy)) + ".")
        facts_txt.append(mapper.get_string(Player(px, py)) + ".")
        for (x, y) in self.walls:
            facts_txt.append(mapper.get_string(Wall(x, y)) + ".")

        facts_block = "\n".join(facts_txt) + "\n"
        self.__program.add_program(facts_block)

        # DEBUG: stampa il blocco fatti che stai passando al solver
        if self.debug:
            print("----------------=== FACTS BLOCK ===-----------------")
            print(facts_block)
    '''

    def __extract_move(self, answer_sets: AnswerSets):
        """Estrae chosen_move/1 normalizzando SymbolicConstant -> stringa."""
        # 1) prova diretta: getter del mapper -> SymbolicConstant -> stringa
        for ans in answer_sets.get_answer_sets():
            for a in ans.get_atoms():
                if isinstance(a, ChosenMove):
                    direction = self.__normalize_symbol(a.get_d())
                    if direction in ("up", "down", "left", "right"):
                        return direction

        # 2) fallback: parsing da stringa
        import re
        for ans in answer_sets.get_answer_sets():
            for a in ans.get_atoms():
                s = str(a)
                m = re.search(r"chosen_move\((up|down|left|right)\)", s)
                if m:
                    return m.group(1)

        # 3) niente trovato
        return None
    

    def __native_diag(self):
        """Esegue DLV2 fuori da EmbASP con lo stesso programma (regole+fatti+#show) e stampa stdout/stderr."""
        try:
            # costruisci il bundle: encoding + facts (come già in __init_program) + #show
            mapper = ASPMapper.get_instance()
            sx, sy = self.self_pos
            px, py = self.player_pos

            facts_txt = [
                mapper.get_string(Self(sx, sy)) + ".",
                mapper.get_string(Player(px, py)) + ".",
            ] + [mapper.get_string(Wall(x, y)) + "." for (x, y) in self.walls]

            bundle = []
            bundle.append(self.__encoding)
            bundle.append("\n% --- FACTS ---")
            bundle.append("\n".join(facts_txt))
            bundle.append("\n% --- SHOW ---")
            bundle.append("#show self/2.\n#show player/2.\n#show wall/2.\n#show chosen_move/1.\n")
            bundle_str = "\n".join(bundle)

            # salva su file temporaneo
            with tempfile.NamedTemporaryFile("w", suffix=".lp", delete=False, encoding="utf-8") as tf:
                tf.write(bundle_str)
                tmp_path = tf.name

            # esegui dlv2 nativo (no -silent per vedere eventuali errori)
            cmd = [self.dlv_path, "-n=0", tmp_path]
            print("=== DLV2 native CMD ===", " ".join(cmd))
            out = subprocess.run(cmd, capture_output=True, text=True)
            print("=== DLV2 native STDOUT ===")
            print(out.stdout if out.stdout.strip() else "<vuoto>")
            print("=== DLV2 native STDERR ===")
            print(out.stderr if out.stderr.strip() else "<vuoto>")
        except Exception as e:
            print("NATIVE DIAG ERROR:", e)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    @staticmethod
    def __normalize_symbol(val):
        """Converte SymbolicConstant in 'up'/'down'/'left'/'right' se possibile."""
        if val is None:
            return None
        # prova metodi comuni
        for m in ("get_value", "get_symbol", "get_name"):
            if hasattr(val, m):
                try:
                    v = getattr(val, m)()
                    if isinstance(v, str):
                        return v
                except Exception:
                    pass
        # prova attributi comuni
        for attr in ("value", "symbol", "name"):
            if hasattr(val, attr):
                v = getattr(val, attr)
                if isinstance(v, str):
                    return v
        # fallback stringa
        return str(val)

    @staticmethod
    def getEncoding(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

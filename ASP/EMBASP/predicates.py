from embasp.languages.predicate import Predicate
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
from embasp.languages.asp.asp_input_program import ASPInputProgram
from embasp.languages.asp.asp_mapper import ASPMapper
from embasp.languages.asp.answer_sets import AnswerSets
from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.languages.predicate import Predicate
from embasp.languages.asp.symbolic_constant import SymbolicConstant
from embasp.languages.predicate import Predicate
from embasp.languages.asp.symbolic_constant import SymbolicConstant

class Self(Predicate):
    predicate_name = "self"
    def __init__(self, x=None, y=None):
        super().__init__([("x", int), ("y", int)])
        self.x = x
        self.y = y
    def get_x(self): return self.x
    def set_x(self, v): self.x = v
    def get_y(self): return self.y
    def set_y(self, v): self.y = v

class Player(Predicate):
    predicate_name = "player"
    def __init__(self, x=None, y=None):
        super().__init__([("x", int), ("y", int)])
        self.x = x
        self.y = y
    def get_x(self): return self.x
    def set_x(self, v): self.x = v
    def get_y(self): return self.y
    def set_y(self, v): self.y = v

class Wall(Predicate):
    predicate_name = "wall"
    def __init__(self, x=None, y=None):
        super().__init__([("x", int), ("y", int)])
        self.x = x
        self.y = y
    def get_x(self): return self.x
    def set_x(self, v): self.x = v
    def get_y(self): return self.y
    def set_y(self, v): self.y = v

class Prev(Predicate):
    predicate_name = "prev"
    def __init__(self, x=None, y=None):
        super().__init__([("x", int), ("y", int)])
        self.x = x
        self.y = y
    def get_x(self): return self.x
    def set_x(self, v): self.x = v
    def get_y(self): return self.y
    def set_y(self, v): self.y = v

class ChosenMove(Predicate):
    predicate_name = "chosen_move"
    def __init__(self, d=None):
        super().__init__([("d", SymbolicConstant)])
        self.d = d
    def get_d(self): return self.d
    def set_d(self, v): self.d = v

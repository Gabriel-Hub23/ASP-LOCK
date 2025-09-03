% --- INPUT ATTESI ---
% cell(X,Y).                % celle della griglia
% wall(X,Y).                % muri
% lock(X,Y).                % (opz.) celle bloccate
% pos_silly(SX,SY).         % posizione attuale del nemico

% --- Cella libera ---
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% --- Candidati: 4-adj (von Neumann) ---
cand(NX,SY) :- pos_silly(SX,SY), NX = SX + 1, free(NX,SY).
cand(NX,SY) :- pos_silly(SX,SY), NX = SX - 1, free(NX,SY).
cand(SX,NY) :- pos_silly(SX,SY), NY = SY + 1, free(SX,NY).
cand(SX,NY) :- pos_silly(SX,SY), NY = SY - 1, free(SX,NY).

% --- Mossa “stupida”: scegli esattamente UNA delle celle candidate ---
:- #count{X,Y : move(X,Y) } != 1.

% --- Fallback: se non ci sono candidati, resta fermo ---
somecand :- cand(_, _).
move(SX,SY) :- not somecand, pos_silly(SX,SY).

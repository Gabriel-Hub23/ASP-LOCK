% =========================================================
% Lock’n’Chase AI — stile slides (choice, vincoli, weak) — DLV2-safe
% INPUT:
%   self(SX,SY).
%   player(PX,PY).
%   wall(X,Y).
%   last_dir(D).      % opzionale: D ∈ {up,down,left,right}
% OUTPUT:
%   chosen_move(D).   % D ∈ {up,down,left,right}
% =========================================================

% --- Dominio direzioni e delta ---------------------------------------------
dir(up).    delta(up,    0, -1).
dir(down).  delta(down,  0,  1).
dir(left).  delta(left, -1,  0).
dir(right). delta(right, 1,  0).

% --- Celle candidate adiacenti alla posizione corrente ----------------------
cand(D, NX, NY) :-
  self(X, Y),
  delta(D, DX, DY),
  NX = X + DX, NY = Y + DY.

% --- Mosse valide: non muro -------------------------------------------------
next(D, NX, NY) :- cand(D, NX, NY), not wall(NX, NY).

% --- Esiste almeno una mossa valida? ---------------------------------------
has_next :- next(_,_,_).

% --- Scelta: esattamente UNA mossa se ci sono candidati --------------------
1 { chosen_move(D) : next(D,_,_) } 1 :- has_next.

% --- Fallback se non ci sono candidati (mai UNSAT) --------------------------
chosen_move(up) :- not has_next.

% ===========================================================================
%                         EURISTICHE (weak constraints)
%   Priorità: 2) evita cul-de-sac  >  1) avvicinati al player + dritto/U-turn
%              0) tie-break deterministico
% ===========================================================================

% ---- 1) Evita cul-de-sac (priorità più alta: livello 2) --------------------
% Celle libere ad 1 passo dalla cella di arrivo
step2(NX,NY,D2,X2,Y2) :-
  next(_, NX, NY), delta(D2,DX2,DY2),
  X2 = NX + DX2, Y2 = NY + DY2, not wall(X2,Y2).

% Grado di libertà della cella di arrivo
free_deg(NX,NY,K) :-
  next(_, NX, NY),
  K = #count { D2,X2,Y2 : step2(NX,NY,D2,X2,Y2) }.

% Penalizza entrare in celle con grado <= 1 (cul-de-sac), se esistono alternative
:~ chosen_move(D), next(D,NX,NY), free_deg(NX,NY,K), K <= 1, has_next. [1000@2, D,NX,NY]

% ---- 2) Avvicinati al player (seconda priorità: livello 1) -----------------
% Valore assoluto DLV2-safe
abs_val(A, A)  :- A >= 0.
abs_val(A, NA) :- A < 0, NA = -A.

% Distanza Manhattan della cella di arrivo dal player
dist(D, V) :-
  next(D, NX, NY), player(PX, PY),
  DX = NX - PX, DY = NY - PY,
  abs_val(DX, AX), abs_val(DY, AY),
  V = AX + AY.

% Minimizza distanza
:~ chosen_move(D), dist(D,V). [V@1, D]

% ---- 3) Preferisci andare "dritto" e evita l'U-turn (stessa priorità) ------
opposite(up,down). opposite(down,up). opposite(left,right). opposite(right,left).

% Se è nota l'ultima direzione:
% - girare (non dritto, non U-turn) = piccola penalità
:~ chosen_move(D), last_dir(L), D != L, not opposite(D,L). [1@1, D,L]
% - U-turn = penalità maggiore
:~ chosen_move(D), last_dir(L), opposite(D,L). [5@1, D,L]

% ---- 4) Tie-break deterministico (priorità più bassa: livello 0) ----------
pref(up,0). pref(right,1). pref(down,2). pref(left,3).
:~ chosen_move(D), pref(D,W). [W@0, D]

% ===========================================================================
% Mostra solo l'uscita (utile con IDE e parsing EmbASP)
#show chosen_move/1.

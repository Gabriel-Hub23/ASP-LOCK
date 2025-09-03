% =============================================
% Lock'n'Chase — AI del nemico (DLV2/IDLV, EmbASP)
% Input attesi dal bridge:
%   cell(X,Y).                     % celle della griglia
%   wall(X,Y).                     % muri/ostacoli
%   lock(X,Y).                     % porte chiuse / celle temporaneamente bloccate
%   pos_silly(SX,SY).              % posizione attuale del nemico
%   pos_player(PX,PY).             % posizione del giocatore
% Output:
%   move(NX,NY).                   % prossima cella del nemico
% =============================================

% --- Cella libera ---
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% --- Candidati: le 4 adiacenti (von Neumann) ---
cand(NX,SY) :- pos_silly(SX,SY), NX = SX + 1, free(NX,SY).
cand(NX,SY) :- pos_silly(SX,SY), NX = SX - 1, free(NX,SY).
cand(SX,NY) :- pos_silly(SX,SY), NY = SY + 1, free(SX,NY).
cand(SX,NY) :- pos_silly(SX,SY), NY = SY - 1, free(SX,NY).

% --- Distanza Manhattan verso il player ---
% |NX-PX|
absdx(NX,_,AX) :- pos_player(PX,_), NX >= PX, AX = NX - PX.
absdx(NX,_,AX) :- pos_player(PX,_), NX <  PX, AX = PX - NX.
% |NY-PY|
absdy(_,NY,AY) :- pos_player(_,PY), NY >= PY, AY = NY - PY.
absdy(_,NY,AY) :- pos_player(_,PY), NY <  PY, AY = PY - NY.

manhattan(NX,NY,M) :- cand(NX,NY), absdx(NX,NY,AX), absdy(NX,NY,AY), M = AX + AY.
score(NX,NY,M)     :- manhattan(NX,NY,M).

% --- Scelta della mossa: minimizza la distanza con tie-break deterministici ---
minS(S)      :- S = #min { V : score(X,Y,V) }.
best(NX,NY)  :- score(NX,NY,S), minS(S).
minX(X)      :- best(X,_),     X = #min { CX : best(CX,CY) }.
minY(Y)      :- best(X,Y),minX(X), Y = #min { CY : best(X,CY) }.
move(X,Y)    :- best(X,Y), minX(X), minY(Y).

% --- Fallback: se non c'è nessun candidato, resta fermo ---
cand_count(N) :- N = #count { X,Y : cand(X,Y) }.
no_cand       :- cand_count(N), N = 0.
move(SX,SY)   :- no_cand, pos_silly(SX,SY).
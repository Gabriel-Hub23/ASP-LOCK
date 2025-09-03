% =========================================================
% Dominio: lo fornisce il bridge con cell(X,Y)., wall(X,Y).
% =========================================================
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% Posizioni (dal gioco):
% pos_silly(SX,SY).  pos_player(PX,PY).
% (opzionale) pos_silly_prev(PSX,PSY).

% ---------------------------------------------------------
% Adiacenze (safe: X,Y già legati da free/2)
% ---------------------------------------------------------
adj(X,Y,X1,Y) :- free(X,Y), X1 = X + 1, free(X1,Y).
adj(X,Y,X1,Y) :- free(X,Y), X1 = X - 1, free(X1,Y).
adj(X,Y,X,Y1) :- free(X,Y), Y1 = Y + 1, free(X,Y1).
adj(X,Y,X,Y1) :- free(X,Y), Y1 = Y - 1, free(X,Y1).

% Candidati: le 4 celle raggiungibili dalla posizione del nemico
cand(NX,NY) :- pos_silly(SX,SY), adj(SX,SY,NX,NY).

% ---------------------------------------------------------
% Distanza di cammino (BFS dal player) – solo min dist
% ---------------------------------------------------------
dist(PX,PY,0) :- pos_player(PX,PY), free(PX,PY).
dist(X2,Y2,D+1) :- dist(X1,Y1,D), adj(X1,Y1,X2,Y2), free(X2,Y2), D>=0.

mindist(X,Y,MD) :- free(X,Y), MD = #min { D : dist(X,Y,D) }.
hasdist(X,Y)    :- mindist(X,Y,_).

% ---------------------------------------------------------
% Heuristics in score unico (tutte le regole SAFE)
% ---------------------------------------------------------

% Manhattan solo come fallback: LEGA X,Y con cand/2 PRIMA!
dx(X,Y,AX) :- cand(X,Y), pos_player(PX,PY), AX = X - PX.
dy(X,Y,AY) :- cand(X,Y), pos_player(PX,PY), AY = Y - PY.

abs(A,A) :- A>=0.
abs(A,B) :- A<0, B = -A.

absdx(X,Y,V) :- dx(X,Y,A), abs(A,V).
absdy(X,Y,V) :- dy(X,Y,A), abs(A,V).

manhattan(X,Y,M) :- absdx(X,Y,VX), absdy(X,Y,VY), M = VX + VY.

% Distanza reale prioritaria; se non raggiungibile, grosso malus + Manhattan
dscore(X,Y,S)  :- cand(X,Y), hasdist(X,Y), mindist(X,Y,D), S = 1000*D.
dscore(X,Y,S)  :- cand(X,Y), not hasdist(X,Y), manhattan(X,Y,M), S = 1000000 + 10*M.

% Grado (evita vicoli ciechi); lega X,Y con cand/2
deg(X,Y,N) :- cand(X,Y), N = #count { X2,Y2 : adj(X,Y,X2,Y2) }.
deg1(X,Y)  :- deg(X,Y,1).

p_dead(X,Y,50) :- deg1(X,Y).
p_dead(X,Y,0)  :- cand(X,Y), not deg1(X,Y).

p_deg(X,Y,P)   :- deg(X,Y,N), P = 2*(10 - N).

% Evita rimbalzo nella cella precedente
p_back(X,Y,30) :- cand(X,Y), pos_silly_prev(X,Y).
p_back(X,Y,0)  :- cand(X,Y), not pos_silly_prev(X,Y).

% Score totale del candidato
score(X,Y,S) :- cand(X,Y),
                dscore(X,Y,SD),
                p_dead(X,Y,PD),
                p_deg(X,Y,PG),
                p_back(X,Y,PB),
                S = SD + PD + PG + PB.

% ---------------------------------------------------------
% Selezione deterministica del MIN (niente choice-rule)
% ---------------------------------------------------------
minS(S)    :- S = #min { V : score(X,Y,V) }.
best(X,Y)  :- score(X,Y,S), minS(S).

minX(X)    :- X = #min { X1 : best(X1,Y1) }.
minY(Y)    :- best(X,Y), minX(X), Y = #min { Y1 : best(X,Y1) }.

move(X,Y)  :- best(X,Y), minX(X), minY(Y).

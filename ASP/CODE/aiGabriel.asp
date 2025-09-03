% =============================================
% Facts dal bridge:
%   cell(X,Y). wall(X,Y). lock(X,Y).
%   pos_silly(SX,SY). pos_player(PX,PY).
% =============================================

% Cella libera (X,Y legati da cell/2)
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% --- Candidati: SOLO le 4 celle attorno al nemico (SAFE) ---
cand(NX,SY) :- pos_silly(SX,SY), NX = SX + 1, free(NX,SY).
cand(NX,SY) :- pos_silly(SX,SY), NX = SX - 1, free(NX,SY).
cand(SX,NY) :- pos_silly(SX,SY), NY = SY + 1, free(SX,NY).
cand(SX,NY) :- pos_silly(SX,SY), NY = SY - 1, free(SX,NY).

% --- Manhattan (variabili già legate da cand/2 e pos_player/2) ---
dx(NX,NY,Dx) :- cand(NX,NY), pos_player(PX,PY), Dx = NX - PX.
dy(NX,NY,Dy) :- cand(NX,NY), pos_player(PX,PY), Dy = NY - PY.

absdx(NX,NY,AX) :- dx(NX,NY,Dx), Dx >= 0, AX = Dx.
absdx(NX,NY,AX) :- dx(NX,NY,Dx), Dx <  0, AX = -Dx.
absdy(NX,NY,AY) :- dy(NX,NY,Dy), Dy >= 0, AY = Dy.
absdy(NX,NY,AY) :- dy(NX,NY,Dy), Dy <  0, AY = -Dy.

manhattan(NX,NY,M) :- absdx(NX,NY,AX), absdy(NX,NY,AY), M = AX + AY.
score(NX,NY,M)     :- manhattan(NX,NY,M).

% --- Scelta minima con tie-break deterministico ---
minS(S)      :- S = #min { V : score(X,Y,V) }.
best(NX,NY)  :- score(NX,NY,S), minS(S).
minX(X)      :- best(X,_),    X = #min { CX : best(CX,CY) }.
minY(Y)      :- best(X,Y), minX(X), Y = #min { CY : best(X,CY) }.
move(X,Y)    :- best(X,Y), minX(X), minY(Y).

% --- Fallback: nessun candidato? resta fermo (SAFE) ---
cand_count(N) :- N = #count { X,Y : cand(X,Y) }.
no_cand       :- cand_count(N), N = 0.
move(SX,SY)   :- no_cand, pos_silly(SX,SY).

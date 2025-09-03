% ================================================
% Fatti passati dal bridge:
%   cell(X,Y). wall(X,Y). lock(X,Y).
%   pos_silly(SX,SY). pos_player(PX,PY).
% ================================================

% Celle libere: X,Y sono legate da cell/2
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% Adiacenze (SAFE: X,Y già legate da free/2)
adj(X,Y,NX,Y) :- free(X,Y), NX = X+1, free(NX,Y).
adj(X,Y,NX,Y) :- free(X,Y), NX = X-1, free(NX,Y).
adj(X,Y,X,NY) :- free(X,Y), NY = Y+1, free(X,NY).
adj(X,Y,X,NY) :- free(X,Y), NY = Y-1, free(X,NY).

% Candidati: mosse possibili dal nemico
cand(NX,NY) :- pos_silly(SX,SY), adj(SX,SY,NX,NY).

% Manhattan verso il player (SAFE: cand lega NX,NY; pos_player lega PX,PY)
dx(NX,NY,Dx) :- cand(NX,NY), pos_player(PX,PY), Dx = NX - PX.
dy(NX,NY,Dy) :- cand(NX,NY), pos_player(PX,PY), Dy = NY - PY.

% Valori assoluti calcolati SOLO da variabili già legate (niente abs/2 generica)
absdx(NX,NY,AX) :- dx(NX,NY,Dx), Dx >= 0, AX = Dx.
absdx(NX,NY,AX) :- dx(NX,NY,Dx), Dx <  0, AX = -Dx.

absdy(NX,NY,AY) :- dy(NX,NY,Dy), Dy >= 0, AY = Dy.
absdy(NX,NY,AY) :- dy(NX,NY,Dy), Dy <  0, AY = -Dy.

manhattan(NX,NY,M) :- absdx(NX,NY,AX), absdy(NX,NY,AY), M = AX + AY.

% Score = Manhattan; selezione minima con tie-break deterministico
score(NX,NY,M) :- manhattan(NX,NY,M).

minS(S)     :- S = #min { V : score(X,Y,V) }.
best(NX,NY) :- score(NX,NY,S), minS(S).

minX(X) :- best(X,_),    X = #min { CX : best(CX,CY) }.
minY(Y) :- best(X,Y), minX(X), Y = #min { CY : best(X,CY) }.

% Mossa finale unica (se ci sono candidati)
move(X,Y) :- best(X,Y), minX(X), minY(Y).

% --------- Fallback SAFE se non ci sono candidati ---------
cand_count(N) :- N = #count { X,Y : cand(X,Y) }.
no_cand       :- cand_count(N), N = 0.

% Se non puoi muovere, resta fermo (mossa valida e deterministica)
move(SX,SY) :- no_cand, pos_silly(SX,SY).

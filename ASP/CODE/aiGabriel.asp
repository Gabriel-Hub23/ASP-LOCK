% ================================================
% Fatti statici passati dal bridge:
%   cell(X,Y).         tutte le celle
%   wall(X,Y).         muri
%   lock(X,Y).         lucchetti
%   pos_silly(SX,SY).  posizione nemico
%   pos_player(PX,PY). posizione player
% ================================================

% Cella libera: X,Y già legati da cell/2
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% Adiacenze (X,Y liberi -> NX,NY legati)
adj(X,Y,NX,Y) :- free(X,Y), NX = X+1, free(NX,Y).
adj(X,Y,NX,Y) :- free(X,Y), NX = X-1, free(NX,Y).
adj(X,Y,X,NY) :- free(X,Y), NY = Y+1, free(X,NY).
adj(X,Y,X,NY) :- free(X,Y), NY = Y-1, free(X,NY).

% Candidati: posizioni adiacenti al nemico
cand(NX,NY) :- pos_silly(SX,SY), adj(SX,SY,NX,NY).

% Manhattan distance al player (variabili legate da cand/2 e pos_player/2)
dx(NX,NY,Dx) :- cand(NX,NY), pos_player(PX,PY), Dx = NX - PX.
dy(NX,NY,Dy) :- cand(NX,NY), pos_player(PX,PY), Dy = NY - PY.

abs(A,B) :- A>=0, B=A.
abs(A,B) :- A<0,  B=-A.

manhattan(NX,NY,M) :- dx(NX,NY,Dx), abs(Dx,AX),
                       dy(NX,NY,Dy), abs(Dy,AY),
                       M = AX + AY.

% Score = distanza Manhattan
score(NX,NY,M) :- manhattan(NX,NY,M).

% Selezione del minimo: 1 sola mossa
minS(S)    :- S = #min { V : score(X,Y,V) }.
best(NX,NY) :- score(NX,NY,S), minS(S).

% Tie-break deterministico per garantire UNA sola soluzione
minX(X) :- best(X,_), X = #min { CX : best(CX,CY) }.
minY(Y) :- best(X,Y), minX(X), Y = #min { CY : best(X,CY) }.

% Mossa finale unica
move(X,Y) :- best(X,Y), minX(X), minY(Y).

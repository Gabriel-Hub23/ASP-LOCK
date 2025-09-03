% ======================================================
% Dominio: fornito dal bridge come facts
%   cell(X,Y).       % tutte le celle della griglia
%   wall(X,Y).       % muri
%   lock(X,Y).       % lucchetti (se presenti)
%   pos_silly(SX,SY).
%   pos_player(PX,PY).
%   (opzionale) pos_silly_prev(X,Y).
% ======================================================

% Cella libera = cella che non è muro né lucchetto
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% ------------------------------------------------------
% Adiacenze (solo fra celle libere) – SAFE
% ------------------------------------------------------
adj(X,Y,X1,Y) :- free(X,Y), X1 = X+1, free(X1,Y).
adj(X,Y,X1,Y) :- free(X,Y), X1 = X-1, free(X1,Y).
adj(X,Y,X,Y1) :- free(X,Y), Y1 = Y+1, free(X,Y1).
adj(X,Y,X,Y1) :- free(X,Y), Y1 = Y-1, free(X,Y1).

% ------------------------------------------------------
% Candidati: le mosse disponibili dal nemico
% ------------------------------------------------------
cand(NX,NY) :- pos_silly(SX,SY), adj(SX,SY,NX,NY).

% ------------------------------------------------------
% Calcolo della distanza dal player (BFS semplice)
% ------------------------------------------------------
dist(PX,PY,0) :- pos_player(PX,PY), free(PX,PY).
dist(X2,Y2,D+1) :- dist(X1,Y1,D), adj(X1,Y1,X2,Y2), free(X2,Y2).

mindist(X,Y,D) :- free(X,Y), D = #min { K : dist(X,Y,K) }.

% ------------------------------------------------------
% Scelta della mossa: il candidato con distanza minima
% ------------------------------------------------------
best(NX,NY,D) :- cand(NX,NY), mindist(NX,NY,D), 
                 D = #min { V : cand(CX,CY), mindist(CX,CY,V) }.

% Tie-break deterministico: X più piccolo, poi Y
minX(X) :- best(X,_,_), X = #min { CX : best(CX,CY,D) }.
minY(Y) :- best(X,Y,_), minX(X), Y = #min { CY : best(X,CY,D) }.

% ------------------------------------------------------
% Mossa finale unica
% ------------------------------------------------------
move(X,Y) :- best(X,Y,_), minX(X), minY(Y).

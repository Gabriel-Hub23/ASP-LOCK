% ======================================================
% Dominio e celle libere (facts da bridge: cell/2, wall/2, lock/2, maxd/1)
% ======================================================
free(X,Y) :- cell(X,Y), not wall(X,Y), not lock(X,Y).

% Posizioni dal gioco:
% pos_silly(SX,SY).
% pos_player(PX,PY).
% (opzionale) pos_silly_prev(PSX,PSY).

% ------------------------------------------------------
% Adiacenze tra celle libere (SAFE)
% ------------------------------------------------------
adj(X,Y,X1,Y) :- free(X,Y), X1 = X+1, free(X1,Y).
adj(X,Y,X1,Y) :- free(X,Y), X1 = X-1, free(X1,Y).
adj(X,Y,X,Y1) :- free(X,Y), Y1 = Y+1, free(X,Y1).
adj(X,Y,X,Y1) :- free(X,Y), Y1 = Y-1, free(X,Y1).

% Candidati: mosse possibili dal nemico
cand(NX,NY) :- pos_silly(SX,SY), adj(SX,SY,NX,NY).

% ------------------------------------------------------
% Bounded BFS dal player (evita generazione infinita)
% ------------------------------------------------------
dist(PX,PY,0) :- pos_player(PX,PY), free(PX,PY).

dist(X2,Y2,D1) :-
    dist(X1,Y1,D), adj(X1,Y1,X2,Y2), free(X2,Y2),
    maxd(M), D < M, D1 = D + 1.

% minima distanza nota per cella libera
mindist(X,Y,MD) :- free(X,Y), MD = #min { K : dist(X,Y,K) }.

% ------------------------------------------------------
% Scelta: il candidato con mindist minima
% ------------------------------------------------------
best(NX,NY,D) :-
    cand(NX,NY), mindist(NX,NY,D),
    D = #min { V : cand(CX,CY), mindist(CX,CY,V) }.

% Tie-break deterministico (X poi Y)
minX(X) :- best(X,_,_), X = #min { CX : best(CX,CY,_) }.
minY(Y) :- best(X,Y,_), minX(X), Y = #min { CY : best(X,CY,_) }.

% Mossa finale unica
move(X,Y) :- best(X,Y,_), minX(X), minY(Y).

% ------------------------------------------------------
% Fallback: se il player non è raggiungibile (nessuna mindist),
% scegli comunque un candidato con tie-break (X,Y min).
% ------------------------------------------------------
fallback_cand :- not best(_,_,_), cand(_, _).

fminX(X) :- fallback_cand, X = #min { CX : cand(CX,CY) }.
fminY(Y) :- fallback_cand, fminX(X), Y = #min { CY : cand(X,CY) }.

move(X,Y) :- fallback_cand, fminX(X), fminY(Y).

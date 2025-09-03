% =========================================================
% Lock'n'Chase – Enemy Move (IDLV/DLV2)
% Obiettivo: scegliere la mossa che minimizza il # di passi
% (shortest-path) fino al player, evitando muri/lock,
% penalizzando vicoli ciechi e rimbalzi.
% Output: move(X,Y).
% =========================================================

% ---------- Bounds & celle libere ----------
in_bounds(X,Y) :- rows(R), cols(C), X>=0, Y>=0, X<R, Y<C.
free(X,Y)      :- in_bounds(X,Y), not wall(X,Y), not lock(X,Y).

% ---------- Posizioni corrente ----------
pos_silly(SX,SY).
pos_player(PX,PY).

% ---------- Candidati: le 4 adiacenti libere ----------
adj(X,Y,X+1,Y) :- free(X,Y), free(X+1,Y).
adj(X,Y,X-1,Y) :- free(X,Y), free(X-1,Y).
adj(X,Y,X,Y+1) :- free(X,Y), free(X,Y+1).
adj(X,Y,X,Y-1) :- free(X,Y), free(X,Y-1).

cand(NX,NY) :- pos_silly(SX,SY), adj(SX,SY,NX,NY).

% ---------- Unica mossa scelta tra i candidati ----------
{ move(NX,NY) : cand(NX,NY) } = 1.

% =========================================================
%  Calcolo distanza di cammino (shortest path) dal PLAYER
% =========================================================

% Propagazione BFS a livelli su grafo delle celle libere.
% Distanza 0 al player:
dist(PX,PY,0) :- pos_player(PX,PY), free(PX,PY).

% Espansione: se (X,Y) ha distanza D, ogni vicino libero ha distanza D+1,
% scegliendo la MINIMA distanza con vincoli di ottimalità:
dist(X2,Y2,D+1) :- dist(X1,Y1,D), adj(X1,Y1,X2,Y2), free(X2,Y2), D>=0.

% Teniamo solo la distanza minima per ogni cella:
% (classico trucco: se una cella ha due distanze diverse, eliminiamo quella maggiore)
:~ dist(X,Y,D1), dist(X,Y,D2), D1<D2. [1@100, X,Y,D2]

% Distanza del candidato scelto:
chosen_dist(D) :- move(X,Y), dist(X,Y,D).

% =========================================================
%  Heuristics & penalità
% =========================================================

% 1) Minimizza la distanza di cammino vera verso il player (peso alto).
:~ chosen_dist(D). [D@50]

% 2) Evita VICOLI CIECHI (celle con grado=1), per non intrappolarsi.
deg(X,Y,N) :- free(X,Y), N = #count { X2,Y2 : adj(X,Y,X2,Y2) }.
deg1(X,Y)  :- deg(X,Y,1).

:~ move(X,Y), deg1(X,Y). [2@5]

% 3) Evita l’OSCILLAZIONE indietro (se nota la cella precedente).
%    Se disponibile pos_silly_prev/2, penalizza tornare subito lì.
:~ move(X,Y), pos_silly_prev(X,Y). [3@5]

% 4) Micro tie-breaker: preferisci celle con grado più alto (più vie d'uscita).
%    Penalizza gradi bassi (scalata dolce).
:~ move(X,Y), deg(X,Y,N). [10-N@2]

% =========================================================
%  Fallback su Manhattan (se per qualche motivo il player non è raggiungibile
%  nella BFS – ad es. blocchi totali). In quel caso minimizziamo |DX|+|DY|.
% =========================================================

% Manhattan del candidato:
dx(X,Y,AX) :- pos_player(PX,PY), AX = X - PX, move(X,Y).
dy(X,Y,AY) :- pos_player(PX,PY), AY = Y - PY, move(X,Y).

% Valore assoluto (due casi):
abs(A, A) :- A>=0.
abs(A, B) :- A<0, B = -A.

absdx(V) :- dx(X,Y,A), abs(A,V).
absdy(V) :- dy(X,Y,A), abs(A,V).

manhattan(M) :- absdx(VX), absdy(VY), M = VX + VY.

% Attiva la penalità Manhattan SOLO se non abbiamo trovato chosen_dist/1.
no_dist :- not chosen_dist(_).

:~ no_dist, manhattan(M). [M@10]

% =========================================================
%  Sicurezza: se per assurdo non ci fossero candidati, niente mossa.
% =========================================================
% (In pratica il choice sopra non si attiva e non si produce move/2)

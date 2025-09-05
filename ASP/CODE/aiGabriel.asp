% ===== mycode.asp (DLV2-safe) =====
% Input:
%   self(SX,SY).
%   player(PX,PY).
%   wall(X,Y).

dir(up;down;left;right).

% Adiacenze SAFE (legate a self/2)
next(X,Y,up,   X, Y1) :- self(X,Y), Y1 = Y - 1.
next(X,Y,down, X, Y1) :- self(X,Y), Y1 = Y + 1.
next(X,Y,left, X1, Y) :- self(X,Y), X1 = X - 1.
next(X,Y,right,X1, Y) :- self(X,Y), X1 = X + 1.

% Celle target dalla posizione corrente
target(NX,NY,D) :- dir(D), next(X,Y,D,NX,NY).

% Mossa valida se non è muro
ok(D) :- target(NX,NY,D), not wall(NX,NY).

% Esiste mossa valida?
ok_exists :- ok(_).

% Scegli esattamente 1 tra le ok, se esistono
1 { take(D) : ok(D) } 1 :- ok_exists.

% Fallback se bloccato
take(up) :- not ok_exists.

% Output
chosen_move(D) :- take(D).

% Sanity: una sola mossa
:- #count{D: take(D)} != 1.
% ===== fine =====


% Minimizza distanza Manhattan dalla posizione del player
%dist(N) :- target(NX,NY,_), player(PX,PY), N = |PX - NX| + |PY - NY|.
%:~ take(D), target(NX,NY,D), player(PX,PY). [ |PX - NX| + |PY - NY| @1 ]

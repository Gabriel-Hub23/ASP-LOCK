% ===== mycode.asp (DLV2-safe, con fix) =====
% Input:
%   self(SX,SY).
%   player(PX,PY).
%   wall(X,Y).

dir(up;down;left;right).

% Adiacenze SAFE (legate a self/2)
next(X,Y,up,   X, Y1) | No :- self(X,Y), Y1 = Y - 1.
next(X,Y,down, X, Y1) | No :- self(X,Y), Y1 = Y + 1.
next(X,Y,left, X1, Y) | No :- self(X,Y), X1 = X - 1.
next(X,Y,right,X1, Y) | No :- self(X,Y), X1 = X + 1.


:- #count{Dir : next(X, Y, Dir, X1, X2)} != 1.

% Celle target
target(NX,NY,D) :- dir(D), next(X,Y,D,NX,NY).

% Mossa valida se non è muro
ok(D) :- target(NX,NY,D), not wall(NX,NY).


% Output “normale”
chosen_move(D) :- ok(D).

% === FIX: se metti chosen_move(D). a mano, creiamo anche take(D) ===
take(D) :- chosen_move(D).

% ===== fine =====

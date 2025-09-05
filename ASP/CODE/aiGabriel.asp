% ===== mycode.asp (DLV2-safe, con fix) =====
% Input:
%   self(SX,SY).
%   player(PX,PY).
%   wall(X,Y).


dir(up). dir(right). dir(down). dir(left). 

% Adiacenze SAFE (legate a self/2)
adj(I,J,D) :- self(X,Y), I=X,   J=Y-1, D=up.      %up
adj(I,J,D) :- self(X,J), I=X,   J=Y+1, D=down.      %down
adj(I,J,D) :- self(X,J), I=X-1, J=Y,   D=left.      %left
adj(I,J,D) :- self(X,J), I=X+1, J=Y,    D=right.        %right

% Mossa valida se non è muro
next(X,Y,D) :- adj(X,Y,D), not wall(X,Y).




% Output “normale”
chosen_move(D) :- next(X,Y,D).

% === FIX: se metti chosen_move(D). a mano, creiamo anche take(D) ===
take(D) :- chosen_move(D).

% ===== fine =====

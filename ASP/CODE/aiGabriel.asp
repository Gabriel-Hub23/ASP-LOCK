% ===== mycode.asp (DLV2-safe) =====
% Input atteso:
%   self(SX,SY).
%   player(PX,PY).
%   wall(X,Y).

% Direzioni
dir(up;down;left;right).

% Adiacenze: IMPORTANTISSIMO: rendiamo le variabili SAFE
% legandole a self(X,Y). Così X e Y sono ground e Y1/X1 derivano con l’aritmetica.
next(X,Y,up,   X, Y1) :- self(X,Y), Y1 = Y - 1.
next(X,Y,down, X, Y1) :- self(X,Y), Y1 = Y + 1.
next(X,Y,left, X1, Y) :- self(X,Y), X1 = X - 1.
next(X,Y,right,X1, Y) :- self(X,Y), X1 = X + 1.

% Cella di destinazione per ciascuna direzione partendo dalla posizione attuale
target(NX,NY,D) :- dir(D), next(X,Y,D,NX,NY).

% Mossa valida se la cella target non è un muro
ok(D) :- target(NX,NY,D), not wall(NX,NY).

% Esiste almeno una mossa ok?
ok_exists :- ok(_).

% Scegli esattamente UNA mossa tra quelle ok, se esistono
1 { take(D) : ok(D) } 1 :- ok_exists.

% Fallback: se nessuna mossa è ok (bloccato), scegli 'up'
take(up) :- not ok_exists.

% Output per Python
chosen_move(D) :- take(D).

% Sanity check: esattamente una mossa
:- #count{D: take(D)} != 1.
% ===== fine =====

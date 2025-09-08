dir(up). dir(right). dir(down). dir(left).

% Adiacenze SAFE (legate a self/2): da cella corrente -> cella destinazione
adj(I,J,up,I,J2)    :- self(X,Y), I = X,   J = Y,   J2 = Y-1.
adj(I,J,down,I,J2)  :- self(X,Y), I = X,   J = Y,   J2 = Y+1.
adj(I,J,left,I2,J)  :- self(X,Y), I = X,   J = Y,   I2 = X-1.
adj(I,J,right,I2,J) :- self(X,Y), I = X,   J = Y,   I2 = X+1.

% Next cell esplicita (include coordinate destinazione)
next_cell(I,J,D,I2,J2) :- adj(I,J,D,I2,J2), not wall(I2,J2).

% Scelta compatibile i-dlv (una mossa per volta)
chosen_move(D) | not_chosen(D) :- next_cell(I,J,D,I2,J2).
:- chosen_move(D1), chosen_move(D2), D1 != D2.

% --- BFS dal giocatore (calcolo distanze discrete fino a bound)
% Bound per la BFS (mapa 17x17 -> max dist <= 34, usiamo 40 per margine)
num(0..40).

% definizione dominio per rendere sicure le regole (usa num/1 già definito)
cell(X,Y) :- num(X), num(Y).

% definizione vicini generica (non attraversa muri) -- versione safe
neigh(X,Y,X,Y2) :- Y2 = Y-1, cell(X,Y), cell(X,Y2), not wall(X,Y2).
neigh(X,Y,X,Y2) :- Y2 = Y+1, cell(X,Y), cell(X,Y2), not wall(X,Y2).
neigh(X,Y,X2,Y) :- X2 = X-1, cell(X,Y), cell(X2,Y), not wall(X2,Y).
neigh(X,Y,X2,Y) :- X2 = X+1, cell(X,Y), cell(X2,Y), not wall(X2,Y).

% distanza 0 al player
dist(X,Y,0) :- player(X,Y).

% propagazione distanze (tutte le distanze fino al bound)
dist(X2,Y2,N1) :- dist(X1,Y1,N), num(N), N1 = N+1, N1 <= 40, neigh(X1,Y1,X2,Y2).

% Se una cella non ha dist associata entro bound è unreachable
reached(X,Y) :- dist(X,Y,_).
unreached(X,Y) :- next_cell(_,_,_,X,Y), not reached(X,Y).

% Weak constraint: minimizza la distanza della cella risultante dalla mossa scelta
% Peso = distanza (minimizzare), livello 1
:~ chosen_move(D), next_cell(I,J,D,X,Y), dist(X,Y,N). [N@1]
% Penalizza fortemente mosse verso celle irraggiungibili
:~ chosen_move(D), next_cell(I,J,D,X,Y), unreached(X,Y). [1000@1]
:- #count{D: chosen_move(D)} != 1.

% Compatibilità API
take(D) :- chosen_move(D).

% Debug: mostra gli atomi principali
#show self/2.
#show wall/2.
#show next_cell/5.
#show dist/3.
#show chosen_move/1.
#show take/1.

% ===== fine =====


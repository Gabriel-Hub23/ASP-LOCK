dir(up). dir(right). dir(down). dir(left).

% Adiacenze SAFE (legate a self/2): da cella corrente -> cella destinazione
adj(I,J,up,I,J2)    :- self(X,Y), I = X, J = Y, J2 = Y-1, not wall(I,J2), not locked(I,J2).
adj(I,J,down,I,J2)  :- self(X,Y), I = X, J = Y, J2 = Y+1, not wall(I,J2), not locked(I,J2).
adj(I,J,left,I2,J)  :- self(X,Y), I = X, J = Y, I2 = X-1, not wall(I2,Y), not locked(I2,Y).
adj(I,J,right,I2,J) :- self(X,Y), I = X, J = Y, I2 = X+1, not wall(I2,Y), not locked(I2,Y).

% Next cell esplicita (include coordinate destinazione)
next_cell(I,J,D,I2,J2) :- adj(I,J,D,I2,J2).  % not wall e not locked già in adj

% --- Scelta mossa (i-DLV): una e una sola mossa SE esistono opzioni ---
chosen_move(D) | not_chosen(D) :- next_cell(_,_,D,_,_).
has_option :- next_cell(_,_,_,_,_).
:- has_option, #count{D: chosen_move(D)} != 1.
:- chosen_move(D1), chosen_move(D2), D1 != D2.

% --- Dominio griglia ---
num(0..16).
cell(X,Y) :- num(X), num(Y).

% --- PATCH A: BFS dal player con dominio passi separato (fino a 40) ---
step(0..40).
neigh(X,Y,X, Y2) :- Y2 = Y-1, cell(X,Y), cell(X,Y2), not wall(X,Y2), not locked(X,Y2).
neigh(X,Y,X, Y2) :- Y2 = Y+1, cell(X,Y), cell(X,Y2), not wall(X,Y2), not locked(X,Y2).
neigh(X,Y,X2,Y) :- X2 = X-1, cell(X,Y), cell(X2,Y), not wall(X2,Y), not locked(X2,Y).
neigh(X,Y,X2,Y) :- X2 = X+1, cell(X,Y), cell(X2,Y), not wall(X2,Y), not locked(X2,Y).

% non muoversi su celle bloccate
:- chosen_move(D), next_cell(_,_,D,X,Y), locked(X,Y).

% distanza 0 al player
dist(X,Y,0) :- player(X,Y).

% propagazione distanze con bound 40
dist(X2,Y2,N1) :- dist(X1,Y1,N), step(N), N1 = N+1, N1 <= 40, neigh(X1,Y1,X2,Y2).

% celle raggiunte / non raggiunte
reached(X,Y)   :- dist(X,Y,_).
unreached(X,Y) :- next_cell(_,_,_,X,Y), not reached(X,Y).

% candidati e minimo (protetto)
cand(D,N) :- next_cell(_,_,D,X2,Y2), dist(X2,Y2,N).
have_cand :- cand(_, _).
min_step_cost(M) :- have_cand, M = #min{N : cand(D,N)}.

% --- Ottimizzazione ---
% Minimizza distanza (livello 2)
:~ chosen_move(D), next_cell(_,_,D,X,Y), dist(X,Y,N). [N@2]

% Evita mosse verso celle senza distanza (livello 3 > 2)
:~ chosen_move(D), next_cell(_,_,D,X,Y), unreached(X,Y). [10@3]

% PATCH C: scoraggia tornare alla cella precedente SOLO in pareggio sul minimo
:~ chosen_move(D), next_cell(_,_,D,X,Y), prev(X,Y),
   have_cand, min_step_cost(M), dist(X,Y,N), N = M. [1@2]

% PATCH D: preferisci mantenere la direzione precedente nei pareggi
dirvec(up,0,-1).  dirvec(down,0,1).  dirvec(left,-1,0).  dirvec(right,1,0).
prev_dir(Dp) :-
    prev(Ip,Jp), self(I,J),
    DX = I - Ip, DY = J - Jp,
    dirvec(Dp,DX,DY).
:~ chosen_move(D), have_cand, min_step_cost(M),
   next_cell(_,_,D,X,Y), dist(X,Y,N), N = M,
   prev_dir(Dp), D != Dp. [1@1]

% Compat API
take(D) :- chosen_move(D).

% Mangia il player se adiacente e raggiungibile (esiste la mossa verso la sua cella)
adj_player(X,Y) :- player(X,Y), next_cell(_,_,_,X,Y).
:- adj_player(X,Y), not chosen_move(D), next_cell(_,_,D,X,Y).

% Debug
#show self/2.
#show next_cell/5.
#show dist/3.
#show chosen_move/1.
#show take/1.
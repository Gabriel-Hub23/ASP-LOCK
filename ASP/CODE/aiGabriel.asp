
free(X,Y) :- cell(X,Y), not wall(X,Y).

move(X,Y) | NotMove(X,Y) :- free(X,Y).


:- #count{X,Y : move(X,Y) } != 1.


move(2,5).
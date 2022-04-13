mov     r0, #50                        @R0 est notre i
mov     r1, #0                         @R1 est notre somme
.LBB0_1:
cmp     r0, #1                         @condition d'arrêt
blt     .LBB0_3                        @arrêt
tst     r0, #1                         @si i impair
bne     .LBB0_2                        @si i pair on skip
add     r1, r1, r0                     @sinon on add a la somme
.LBB0_2:
sub     r0, r0, #1                     @on decr i
b       .LBB0_1                        @on recommence
.LBB0_3:
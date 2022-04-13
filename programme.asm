mov     r0, #50
b       .LBB0_1
.LBB0_1:
cmp     r0, #1
blt     .LBB0_6
b       .LBB0_2
.LBB0_2:
tst     r0, #1
beq     .LBB0_4
b       .LBB0_3
.LBB0_3:
add     r0, r0, r1
b       .LBB0_4
.LBB0_4:
b       .LBB0_5
.LBB0_5:
sub     r0, r0, #1
b       .LBB0_1
.LBB0_6:
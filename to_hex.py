#cond
EQ = 0b0000
NE = 0b0001
HS = 0b0010
LO = 0b0011
MI = 0b0100
PL = 0b0101
VS = 0b0110
VC = 0b0111
HI = 0b1000
LS = 0b1001
GE = 0b1010
LT = 0b1011
GT = 0b1100
LE = 0b1101
AL = 0b1110
AI = 0b1111 #always false (depends on impl.)

#calcul
ADD = 0b0100
SUB = 0b0010
AND = 0b0000
ORR = 0b1100
CMP = 0b1010

#type
branch = 0b10
calc   = 0b00
mem    = 0b01

def B(addr): # branch
    return 0b1010 << 24 + addr & 0xFFFFFF

#u -> signe
#w −> osef
#p -> osef aussi
def mem(p : bool, u : bool, w : bool, ldr : bool):# ldr / str
    return (0b010 << 25) + (p << 24) + (u << 23) + (w << 21) + (ldr << 20)

def accmem(rn, rt, imm): #ldr / str
    return (rn << 16) + (rt << 12) + (imm & 0xFFF)

def calc(ope, store : bool, use_reg : bool, rn, rd, immrm):
    return (use_reg << 25) + (ope << 21) + (store << 20) + (rn << 16) + (rd << 12) + (immrm & (0xF if use_reg else 0xFFF))

def condcond(cond):
    return (cond << 28)

#ADD RD,RS,RS
#ADD RD,RS,#12
#SUB
#ORR
#AND
#CMP

#LDR RD,[RA, #0]
#STR RD,[RA,#0]

#B #addr

#f = open("demofile.txt", "r")
#for ligne in f:
while 1:
    ligne = input()
    res = 0
    t = ligne.split(' ')
    args = t[1].split(',')
    t[0] += "   "
    if(t[0][:3] == "ADD"): res = condcond(AL) + calc(ADD, t[0][3] == "S", args[2][0] =='R',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
    if(t[0][:3] == "SUB"): res = condcond(AL) + calc(SUB, t[0][3] == "S", args[2][0] =='R',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
    if(t[0][:3] == "ORR"): res = condcond(AL) + calc(ORR, t[0][3] == "S", args[2][0] =='R',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
    if(t[0][:3] == "AND"): res = condcond(AL) + calc(AND, t[0][3] == "S", args[2][0] =='R',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
    if(t[0][:3] == "CMP"): res = condcond(AL) + calc(CMP, t[0][3] == "S", args[2][0] =='R',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
    #if(t[0][:3] == "LDR") res = mem()
    #if(t[0][:3] == "STR") res = mem()
    #if(t[0][0] == "B") 
    print(bytes(res))
import os
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

def get_cond(cond):
    if cond == "EQ":
        return EQ
    elif cond == "NE":
        return NE
    elif cond == "HS":
        return HS
    elif cond == "LO":
        return LO
    elif cond == "MI":
        return MI
    elif cond == "PL":
        return PL
    elif cond == "VS":
        return VS
    elif cond == "VC":
        return VC
    elif cond == "HI":
        return HI
    elif cond == "LS":
        return LS
    elif cond == "GE":
        return GE
    elif cond == "LT":
        return LT
    elif cond == "GT":
        return GT
    elif cond == "LE":
        return LE
    elif cond == "AL":
        return AL
    elif cond == "AI":
        return AI
    else:
        return None


def B(addr): # branch
    return (0b1010 << 24) + (addr & 0xFFFFFF)

#u -> signe
#w −> osef
#p -> osef aussi
def mem(p : bool, u : bool, w : bool, ldr : bool):# ldr / str
    return (0b010 << 25) + (p << 24) + (u << 23) + (w << 21) + (ldr << 20)

def accmem(rn, rt, imm): #ldr / str
    return (rn << 16) + (rt << 12) + (imm & 0xFFF)

def calc(ope, store : bool, use_imm : bool, rn, rd, immrm):
    return (use_imm << 25) + (ope << 21) + (store << 20) + (rn << 16) + (rd << 12) + (immrm & (0xFFF if use_imm else 0xF))

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

def rewrite():
    f = open("programme.asm", "r")
    out = open("programme_r.asm", "w")
    for ligne in f:
        if(ligne[0] == '.'):
            index = ligne.find(':')
            if index == -1:
                print("Syntax error in line " + ligne)
            out.write(ligne[:index+1]+"\n")
            continue
        ligne = ligne.upper()
        ligne = ligne.replace(", ", ",")
        ligne = ligne.replace(" ,", ",")
        t = ligne.split()
        args = t[1].split(',')
        if(t[0][:3] == "MOV"):
            ligne = "SUB"+t[0][3:]+" "+args[0]+"," +args[0]+","+args[0]+"\n"
            ligne += "ADD"+t[0][3:]+" "+args[0]+","+args[0]+","+args[1]+"\n"
            out.write(ligne)
        elif(t[0][:3] == "TST"):
            ligne = "ANDS R14,"+args[0]+","+args[1]+"\n"
            out.write(ligne)
        else:
            out.write(' '.join(t)+"\n")
    out.close()
    f.close()


def pre_compile():
    f = open("programme_r.asm", "r")
    out = open("memfile.pre", "w")
    adrs = {}
    pc = 0
    for ligne in f:
        if(ligne[0] == '.'):
            adrs[ligne[1:-2]] = pc
            continue
        res = 0
        t = ligne.split()
        args = t[1].split(',')
        t[0] += "   "
        if(t[0][:3] == "ADD"): res = condcond(AL) + calc(ADD, t[0][3] == "S", args[2][0] =='#',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
        if(t[0][:3] == "SUB"): res = condcond(AL) + calc(SUB, t[0][3] == "S", args[2][0] =='#',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
        if(t[0][:3] == "ORR"): res = condcond(AL) + calc(ORR, t[0][3] == "S", args[2][0] =='#',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
        if(t[0][:3] == "AND"): res = condcond(AL) + calc(AND, t[0][3] == "S", args[2][0] =='#',int(args[1][1]),int(args[0][1]),int(args[2][1:]))
        if(t[0][:3] == "CMP"): res = condcond(AL) + calc(CMP, 1, 1,int(args[0][1]),int(args[0][1]),int(args[1][1:]))
        if(t[0][:3] == "LDR"): res = 0
        if(t[0][:3] == "STR"): res = 0
        if(t[0][0] == "B"):
            condition = t[0][4:]+"AL"
            if(t[1][0] == '.'):
                if(t[1][1:] in adrs.keys()):
                    dist = (adrs[t[1][1:]] - pc)* 4
                    res = B(dist) + condcond(get_cond(condition[:2]))
                else:
                    out.write(ligne)
                    pc += 1
                    continue
            else:
                res = B(int(t[1][1:])) + condcond(get_cond(condition[:2]))
        out.write(str(res)+"\n")
        pc += 1
    out.close()
    f.close()
    return adrs


def compile_with_adrs(adrs):
    f = open("memfile.pre", "r")
    out = open("memfile_no.pre", "w")
    pc = 0
    for ligne in f:
        res = 0
        t = ligne.split()
        if(t[0][0] == "B"):
            condition = t[0][1:]+"AL"
            if(t[1][1:] in adrs.keys()):
                dist = (adrs[t[1][1:]] - pc)* 4
                if(dist > 4 or dist < -4):
                    res = B(dist) + condcond(get_cond(condition[:2]))
            else:
                print("Erreur Balise " + t[1][1:-1] + " non définie")
                print(adrs)
                exit(1)
        else:
            res = int(t[0])
        out.write("%08X\n" % res)
        pc += 1
    out.close()
    f.close()

def clean():
    f = open("memfile_no.pre", "r")
    out = open("memfile.dat", "w")
    for ligne in f:
        if ligne != "00000000\n": out.write(ligne)
    out.close()
    f.close()
    #os.remove("programme_r.asm")
    #os.remove("memfile.pre")
    #os.remove("memfile_no.pre")

if __name__ == "__main__":
    rewrite()
    adrs = pre_compile()
    print(adrs)
    compile_with_adrs(adrs)
    clean()
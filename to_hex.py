import os
TAILLE_INSTR = 1
#cond
conds = [
["EQ",0b0000],
["NE",0b0001],
["HS",0b0010],
["LO",0b0011],
["MI",0b0100],
["PL",0b0101],
["VS",0b0110],
["VC",0b0111],
["HI",0b1000],
["LS",0b1001],
["GE",0b1010],
["LT",0b1011],
["GT",0b1100],
["LE",0b1101],
["AL",0b1110],
["--",0b1111]]

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

findinlist = lambda x,y: [i for i,j in enumerate(y) if x in j]

def get_cond(cond):
    i_c = findinlist(cond, conds)
    if(len(i_c) == 0):
        print("Erreur condition non définie : " + cond)
        exit(1)
    return conds[i_c[0]][1]


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
        index = ligne.find('@')
        if index != -1:
            ligne = ligne[:index]
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
        if(t[0][:3] == "ADD"): res = condcond(0xE) + calc(ADD, t[0][3] == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
        elif(t[0][:3] == "SUB"): res = condcond(0xE) + calc(SUB, t[0][3] == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
        elif(t[0][:3] == "ORR"): res = condcond(0xE) + calc(ORR, t[0][3] == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
        elif(t[0][:3] == "AND"): res = condcond(0xE) + calc(AND, t[0][3] == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
        elif(t[0][:3] == "CMP"): res = condcond(0xE) + calc(CMP, 1, 1,int(args[0][1:]),int(args[0][1:]),int(args[1][1:]))
        elif(t[0][:3] == "LDR"): res = 0
        elif(t[0][:3] == "STR"): res = 0
        elif(t[0][0] == "B"):
            condition = t[0][4:]+"AL"
            if(t[1][0] == '.'):
                if(t[1][1:] in adrs.keys()):
                    dist = (pc - adrs[t[1][1:]])* TAILLE_INSTR
                    dist += (1<<23)
                    res = B(dist) + condcond(get_cond(condition[:2]))
                else:
                    out.write(ligne)
                    pc += 1
                    continue
            else:
                res = B(int(t[1][1:])) + condcond(get_cond(condition[:2]))
        else:
            print(t[0]+" ("+str(args)+") Non reconnu")
            continue
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
                dist = (adrs[t[1][1:]] - pc)* TAILLE_INSTR
                if(dist > TAILLE_INSTR or dist < -TAILLE_INSTR):
                    res = B(dist) + condcond(get_cond(condition[:2]))
            else:
                print("Erreur ligne :"+str(pc)+"\n    Balise '" + t[1][1:] + "' non définie")
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
    os.remove("programme_r.asm")
    os.remove("memfile.pre")
    os.remove("memfile_no.pre")

if __name__ == "__main__":
    rewrite()
    adrs = pre_compile()
    compile_with_adrs(adrs)
    clean()
    print("Compilation ok")
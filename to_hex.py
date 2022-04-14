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
["",0b1110],
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

def get_modifiers(modif):
    if(len(modif) == 0): return "",""
    if(len(modif) == 1): return modif[0], ""
    return modif[2:],modif[0:2]

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
        if(ligne == "\n"):
            continue
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
        if(t[0][:3] == "MOV"):
            modifiers = t[0][3:]
            savestr, condstr = get_modifiers(modifiers)
            args = t[1].split(',')
            ligne = "SUB"+condstr+" "+args[0]+"," +args[0]+","+args[0]+"\n"
            ligne += "ADD"+condstr+savestr+" "+args[0]+","+args[0]+","+args[1]+"\n"
            out.write(ligne)
            continue
        if(t[0][:3] == "TST"):
            args = t[1].split(',')
            ligne = "ANDS R14,"+args[0]+","+args[1]+"\n"
            out.write(ligne)
            continue
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
        if(len(t) == 0):
            continue
        t[0] += ""
        if(t[0][:3] == "NOP"): res = condcond(0xE)
        else:
            if(len(t) != 2):
                print("Erreur ligne :"+str(pc)+"\n    Syntax error '"+ligne[:-1]+"'")
                print("Evitez les espaces dans les arguments")
                exit(1)
            args = t[1].split(',')
            if(t[0][:3] == "ADD"): 
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + calc(ADD, savestr == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
            elif(t[0][:3] == "SUB"): 
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + calc(SUB, savestr == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
            elif(t[0][:3] == "ORR"): 
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + calc(ORR, savestr == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
            elif(t[0][:3] == "AND"): 
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + calc(AND, savestr == "S", args[2][0] =='#',int(args[1][1:]),int(args[0][1:]),int(args[2][1:]))
            elif(t[0][:3] == "CMP"): 
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + calc(CMP, 1, 1,int(args[0][1:]),int(args[0][1:]),int(args[1][1:]))
            elif(t[0][:3] == "LDR"): res = 0
            elif(t[0][:3] == "STR"): res = 0
            elif(t[0][0] == "B"):
                condition = t[0][1:3] if len(t[0]) > 2 else ""
                if(t[1][0] == '.'):
                    if(t[1][1:] in adrs.keys()):
                        dist = (pc - adrs[t[1][1:]])* TAILLE_INSTR
                        dist += (1<<23)
                        res = B(dist) + condcond(get_cond(condition))
                    else:
                        out.write(ligne)
                        pc += 1
                        continue
                else:
                    res = B(int(t[1][1:])) + condcond(get_cond(condition))
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
                    res = condcond(get_cond("--"))
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
        if ligne != "F0000000\n": out.write(ligne)
        #out.write(ligne)
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
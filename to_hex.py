import os
import sys

TAILLE_INSTR = 4
REWRITE_MOV_AS_SUB_ADD = False
# rewrite MOV Rn,#N as
# SUB Rn,Rn,Rn
# ADD Rn,Rn,#N
SEPARATOR = '\n'  # Instructions separator

# cond
conds = [
    ["EQ", 0b0000],
    ["NE", 0b0001],
    ["HS", 0b0010],
    ["LO", 0b0011],
    ["MI", 0b0100],
    ["PL", 0b0101],
    ["VS", 0b0110],
    ["VC", 0b0111],
    ["HI", 0b1000],
    ["LS", 0b1001],
    ["GE", 0b1010],
    ["LT", 0b1011],
    ["GT", 0b1100],
    ["LE", 0b1101],
    ["", 0b1110],
    ["--", 0b1111]]

# calcul
ADD = 0b0100
SUB = 0b0010
AND = 0b0000
ORR = 0b1100
CMP = 0b1010
MOV = 0b1101

# type
branch = 0b10
calc = 0b00
mem = 0b01

findinlist = lambda x, y: [i for i, j in enumerate(y) if x in j]


def get_cond(cond):
    i_c = findinlist(cond, conds)
    if len(i_c) == 0:
        print("Erreur condition non définie : " + cond)
        exit(1)
    return conds[i_c[0]][1]


def B(addr):  # branch
    return (0b1010 << 24) + (addr & 0xFFFFFF)


# u -> signe
# w −> osef
# p -> osef aussi

def ldr_str(p: bool, u: bool, w: bool, ldr: bool):  # ldr / str
    return (0b010 << 25) + (p << 24) + (u << 23) + (w << 21) + (ldr << 20)


def accmem(rn, rt, imm):  # ldr / str
    return (rn << 16) + (rt << 12) + (imm & 0xFFF)


def arithmetic(ope, store: bool, use_imm: bool, rn, rd, immrm):
    return (use_imm << 25) + (ope << 21) + (store << 20) + (rn << 16) + (rd << 12) + (
            immrm & (0xFFF if use_imm else 0xF))


def condcond(cond):
    return cond << 28


def get_modifiers(modif):
    if len(modif) == 0:
        return "", ""
    if len(modif) == 1:
        return modif[0], ""
    return modif[2:], modif[0:2]


def rewrite(filename):
    f = open(filename, "r")
    out = []
    for ligne in f:
        if ligne == "\n":
            continue
        if ligne[0] == '.':
            index = ligne.find(':')
            if index == -1:
                print("Syntax error in line " + ligne)
            out.append(ligne[:index + 1].upper())
            continue
        index = ligne.find('@')
        if index != -1:
            ligne = ligne[:index]
        ligne = ligne.upper()
        ligne = ligne.replace(", ", ",")
        ligne = ligne.replace(" ,", ",")
        t = ligne.split()
        if REWRITE_MOV_AS_SUB_ADD and t[0][:3] == "MOV":
            modifiers = t[0][3:]
            savestr, condstr = get_modifiers(modifiers)
            args = t[1].split(',')
            ligne = "SUB" + condstr + " " + args[0] + "," + args[0] + "," + args[0]
            ligne += "ADD" + condstr + savestr + " " + args[0] + "," + args[0] + "," + args[1]
            out.append(ligne)
            continue
        out.append(' '.join(t))
    f.close()
    return out


def pre_assemble(instructions):
    out = []
    addresses = {}
    pc = 0
    for ligne in instructions:
        if ligne[0] == '.':
            addresses[ligne[1:-1]] = pc
            continue
        res = 0
        t = ligne.split()
        if len(t) == 0:
            continue
        t[0] += ""
        if t[0][:3] in ["NOP", "LDR", "STR"]:
            res = condcond(0xE)
        else:
            if len(t) != 2:
                print("Erreur ligne :" + str(pc) + "\n    Syntax error '" + ligne + "'")
                print("Evitez les espaces dans les arguments")
                exit(1)
            args = t[1].split(',')
            if t[0][:3] == "ADD":
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + arithmetic(ADD, savestr == "S", args[2][0] == '#',
                                                               int(args[1][1:]),
                                                               int(args[0][1:]),
                                                               int(args[2][1:]))
            elif t[0][:3] == "MOV":
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + arithmetic(MOV, savestr == "S", args[1][0] == '#', 0,
                                                               int(args[0][1:]),
                                                               int(args[1][1:]))
            elif t[0][:3] == "SUB":
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + arithmetic(SUB, savestr == "S", args[2][0] == '#',
                                                               int(args[1][1:]),
                                                               int(args[0][1:]),
                                                               int(args[2][1:]))
            elif t[0][:3] == "ORR":
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + arithmetic(ORR, savestr == "S", args[2][0] == '#',
                                                               int(args[1][1:]),
                                                               int(args[0][1:]),
                                                               int(args[2][1:]))
            elif t[0][:3] == "AND":
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + arithmetic(AND, savestr == "S", args[2][0] == '#',
                                                               int(args[1][1:]),
                                                               int(args[0][1:]),
                                                               int(args[2][1:]))
            elif t[0][:3] == "CMP":
                modifiers = t[0][3:]
                savestr, condstr = get_modifiers(modifiers)
                res = condcond(get_cond(condstr)) + arithmetic(CMP, True, args[1][0] == '#',
                                                               int(args[0][1:]),
                                                               int(args[0][1:]),
                                                               int(args[1][1:]))
            elif t[0][0] == "B":
                condition = t[0][1:3] if len(t[0]) > 2 else ""
                if t[1][0] == '.':
                    if t[1][1:] in addresses.keys():  # backwards branch
                        dist = (pc - addresses[t[1][1:]]) * TAILLE_INSTR
                        dist = 0xFFFFFF - dist + 1
                        res = B(dist) + condcond(get_cond(condition))
                    else:
                        out.append(ligne)
                        pc += 1
                        continue
                else:
                    res = B(int(t[1][1:])) + condcond(get_cond(condition))
            else:
                print(t[0] + " (" + str(args) + ") Non reconnu")
                continue
        out.append(str(res))
        pc += 1
    return addresses, out


def assemble_with_adrs(address, instructions):
    out = []
    pc = 0
    for ligne in instructions:
        res = 0
        t = ligne.split()
        if t[0][0] == "B":
            condition = t[0][1:] + "AL"
            if t[1][1:] in address.keys():  # forward branch
                dist = (address[t[1][1:]] - pc) * TAILLE_INSTR
                if dist >= TAILLE_INSTR or dist <= -TAILLE_INSTR:
                    res = B(dist) + condcond(get_cond(condition[:2]))
                else:
                    res = condcond(get_cond("--"))
            else:
                print("Erreur ligne :" + str(pc) + "\n    Balise '" + t[1][1:] + "' non définie")
                print(address)
                exit(1)
        else:
            res = int(t[0])
        out.append("%08X" % res)
        pc += 1
    return out


if __name__ == "__main__":
    instrs = rewrite(sys.argv[1])
    adrs, instrs = pre_assemble(instrs)
    instrs = assemble_with_adrs(adrs, instrs)
    for ligne in instrs:
        if ligne != "F0000000\n":
            print(ligne, end=SEPARATOR)

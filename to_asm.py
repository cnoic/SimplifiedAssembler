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

calcs = [
["ADD",0b0100],
["SUB",0b0010],
["AND",0b0000],
["ORR",0b1100],
["CMP",0b1010]]

types = [
["B",0b10],
["calc",0b00],
["mem",0b01]]

findinlist = lambda x,y: [i for i,j in enumerate(y) if x in j]

hex_string_to_int = lambda x: int(x,16)


f = open("memfile.dat", "r")
for ligne in f:
    val = hex_string_to_int(ligne[:-1])
    cond = findinlist(hex_string_to_int(ligne[0]),conds)
    if len(cond) == 0:
        print("Error: no cond found")
        exit(1)
    cond = conds[cond[0]][0]

    ope = findinlist((val >> 26) & 0b11,types)
    if len(ope) == 0:
        print("Error: no type found")
        exit(1)
    ope = types[ope[0]][0]

    calc = ""
    if ope == "calc":
        calc = findinlist((val >> 21) & 0xF,calcs)
        if len(calc) == 0:
            print("Error: no calc found")
            exit(1)
        calc = calcs[calc[0]][0]
    rn = (val >> 16) & 0xF
    rm = val & 0x7FF
    rd = (val >> 12) & 0xF

    if ope == "B":
        sign = "-" if (val >> 23) & 0x1 else ""
        print("B"+cond+"   #"+sign+str(val & 0x7FFFFF))
    elif ope == "mem":
        print("mem",cond," ",calc," ",rn," ",rm)
    elif ope == "calc":
        save = "S" if (val >> 20) & 1 else " "
        imm = (val >> 25) & 1
        sign = "-" if imm and (val >> 11) & 1 else ""
        if imm:
            print(calc+cond+save+"  R"+str(rd)+",R"+str(rn)+",#"+str(rm))
        else:
            print(calc+cond+save+"  R"+str(rd)+",R"+str(rn)+",R"+str(rm&0xF))
    else:
        print("Error: no type found")
        exit(1)
f.close()





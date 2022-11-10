#!/usr/binary/python3
import sys
filename = sys.argv[1]
hexa = []
binary = []

#read file
with open(filename, 'rb') as byte_file:

    while True:
      byte = byte_file.read(1) #read 1 byte = 8 bits
      if len(byte) == 0:
        break

      else:
        if len(hex(ord(byte))) == 3: #length
          hexa.append("0x0" + str(hex(ord(byte))[-1]))
        else:
          hexa.append(str(hex(ord(byte))))

      binary.append("0b" + '0' * (10 - len(bin(ord(byte)))) + str(bin(ord(byte))[2:]))
byte_file.close()

#sorted lists (hexa and binary)
count = 3 #count
sorted_hexa = []
sorted_binary = []
while (count < len(hexa)):
  sorted_hexa.append(hexa[count])
  sorted_binary.append(binary[count])
  if (count % 4 == 0):
    count += 7
    continue
  count -= 1
  
#inst lists (hexa and bin)
inst_hexa = []
inst_binary = []
for i in range(len(sorted_hexa)):
  if (i % 4 == 0):
    inst_hexa.append(sorted_hexa[i][2:])
    inst_binary.append(sorted_binary[i][2:])
  else:
    inst_hexa[i // 4] += sorted_hexa[i][2:]
    inst_binary[i // 4] += sorted_binary[i][2:]

#define
def register(rs): #register name
  output = 0
  exp = 1
  for i in range(len(rs)):
    output += (int(rs[len(rs) - 1 - i]) * exp)
    exp *= 2
  return "x" + str(output)

def shamt_int_imm(imm):
    output = 0
    exp = 1
    for i in range(len(imm)):
        output += (int(imm[len(imm)-1-i]) * exp)
        exp *= 2
    return str(output)

def s_int_imm(imm): #imm of S type
  output = 0
  exp = 1
  if int(imm[0]) == 1:
    output = -(2**(len(imm) - 1))
    for i in range(len(imm) - 1):
      output += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2

  else:
    for i in range(len(imm) - 1):
      output += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  return str(output)

def u_int_imm(imm): #imm of U type
  output = 0
  exp = 2**12
  if int(imm[0]) == 1:
    output = -(2**(len(imm) - 1 + 12))
    for i in range(len(imm) - 1):
      output += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2

  else:
    for i in range(len(imm) - 1) :
      output += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  return str(output)

def b_int_imm(imm): #imm of B type
  output = 0
  exp = 2
  if int(imm[0]) == 1:
    output = -(2**(len(imm) - 1 + 1))
    for i in range(len(imm) - 1):
      output += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2

  else:
    for i in range(len(imm) - 1) :
      output += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  return str(output)

#Print format
def type_U_print(imm, rd): #for U type
  print(register(rd) + ", " + u_int_imm(imm))

def type_J_print(imm, rd): #for J type
  print(register(rd) + ", " + b_int_imm(imm))

def type_I_print(imm, rs1, rd): #for I type
  print(register(rd) + ", " + register(rs1) + ", " + s_int_imm(imm))

def shamt_type_print(imm, rs1, rd):
    print(register(rd) + ", " + register(rs1) + ", " + shamt_int_imm(imm))

def type_B_print(imm, rs2, rs1): #for B type
  print(register(rs1) + ", " + register(rs2) + ", " + b_int_imm(imm))

def type_S_print(imm, rs2, rs1): #for S type
  print(register(rs2) + ", " + s_int_imm(imm) + "(" + register(rs1) + ")")

def type_R_print(rs2, rs1, rd): #for R type
  print(register(rd) + ", " + register(rs1) + ", " + register(rs2))

#types
type_U = ["0110111", "0010111"]
type_J = ["1101111"]
type_I = ["1100111", "0000011", "0010011"]
type_B = ["1100011"]
type_S = ["0100011"]
type_R = ["0110011"]

#for any print
for i in range(len(inst_hexa)):
  print(f"inst {i}: {inst_hexa[i]} ", end='')
  opcode = inst_binary[i][25:32] #opcodes are all same
  
  
  if opcode in type_U: #U type style
    imm = inst_binary[i][:20]
    rd = inst_binary[i][20:25]

    if opcode == "0110111": #0110111
      print("lui ", end='')
      type_U_print(imm, rd)

    else: #0010111
      print("auipc ", end='')
      type_U_print(imm, rd)

  elif opcode in type_J: #J type style
    imm = inst_binary[i][0] + inst_binary[i][12:20] + inst_binary[i][11] + inst_binary[i][
      1:11]
    rd = inst_binary[i][20:25]

    print("jal ", end='') #1101111
    type_J_print(imm, rd)

  elif opcode in type_I: #I type style
    imm = inst_binary[i][:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]
    rd = inst_binary[i][20:25]

    if opcode == "1100111": #1100111
      if funct3 == "000":
        print("jalr ", end='')
        type_S_print(imm, rd, rs1)

      else:
        print("unknown instruction")

    elif opcode == "0000011": #0000011
      if funct3 == "000":
        print("lb ", end='')
        type_S_print(imm, rd, rs1)
    
      #different funct3
      elif funct3 == "001":
        print("lh ", end='')
        type_S_print(imm, rd, rs1)

      elif funct3 == "010":
        print("lw ", end='')
        type_S_print(imm, rd, rs1)

      elif funct3 == "100":
        print("lbu ", end='')
        type_S_print(imm, rd, rs1)

      elif funct3 == "101":
        print("lhu ", end='')
        type_S_print(imm, rd, rs1)

      else:
        print("unknown instruction")

    else:
      if funct3 == "000":
        print("addi ", end='')
        type_I_print(imm, rs1, rd)

      elif funct3 == "010":
        print("slti ", end='')
        type_I_print(imm, rs1, rd)

      elif funct3 == "011":
        print("sltiu ", end='')
        type_I_print(imm, rs1, rd)

      elif funct3 == "100":
        print("xori ", end='')
        type_I_print(imm,rs1,rd)

      elif funct3 == "110":
        print("ori ", end='')
        type_I_print(imm,rs1,rd)

      elif funct3 == "111":
        print("andi ", end='')
        type_I_print(imm,rs1,rd)

      elif funct3 == "001":
        shamt = imm[7:]
        if imm[:7] == "0000000":
          print("slli ", end='')
          shamt_type_print(shamt, rs1, rd)

        else:
          print("unknown instruction")

      elif funct3 == "101":
        shamt = imm[7:]
        if imm[:7] == "0000000":
          print("srli ", end='')
          shamt_type_print(shamt, rs1, rd)

        elif imm[:7] == "0100000":
          print("srai ", end='')
          shamt_type_print(shamt, rs1, rd)

        else:
          print("unknown instruction")

      else:
        print("unknown instruction")

  elif opcode in type_B: #B type style
    imm = inst_binary[i][0] + inst_binary[i][24] + inst_binary[i][1:7] + inst_binary[i][
      20:24]
    rs2 = inst_binary[i][7:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]

#1100011
    if funct3 == "000":
      print("beq ", end='')
      type_B_print(imm,rs2,rs1)

    elif funct3 == "001":
      print("bne ",end='')
      type_B_print(imm,rs2,rs1)

    elif funct3 == "100":
      print("blt ",end='')
      type_B_print(imm,rs2,rs1)

    elif funct3 == "101":
      print("bge ",end='')
      type_B_print(imm,rs2,rs1)

    elif funct3 == "110":
      print("bltu ",end='')
      type_B_print(imm,rs2,rs1)

    elif funct3 == "111":
      print("bgeu ",end='')
      type_B_print(imm,rs2,rs1)

    else:
      print("unknown instruction")

  elif opcode in type_S: #S type style
    imm = inst_binary[i][:7] + inst_binary[i][20:25]
    rs2 = inst_binary[i][7:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]

#0100011
    if funct3 == "000":
      print("sb ",end='')
      type_S_print(imm,rs2,rs1)

    elif funct3 == "001":
      print("sh ",end='')
      type_S_print(imm,rs2,rs1)

    elif funct3 == "010":
      print("sw ",end='')
      type_S_print(imm,rs2,rs1)

    else:
      print("unknown instruction")

  elif opcode in type_R: #R type style
    funct7 = inst_binary[i][:7]
    rs2 = inst_binary[i][7:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]
    rd = inst_binary[i][20:25]
    
#0110011

    #funct7
    if funct7 == "0000000":
      if funct3 == "000":
        print("add ", end='')
        type_R_print(rs2,rs1,rd)

      #funct3
      elif funct3 == "001":
        print("sll ",end='')
        type_R_print(rs2,rs1,rd)

      elif funct3 == "010":
        print("slt ",end='')
        type_R_print(rs2,rs1,rd)

      elif funct3 == "011":
        print("sltu ",end='')
        type_R_print(rs2,rs1,rd)

      elif funct3 == "100":
        print("xor ",end='')
        type_R_print(rs2,rs1,rd)

      elif funct3 == "101":
        print("srl ",end='')
        type_R_print(rs2,rs1,rd)

      elif funct3 == "110":
        print("or ",end='')
        type_R_print(rs2,rs1,rd)

      elif funct3 == "111":
        print("and ",end='')
        type_R_print(rs2,rs1,rd)

      else:
        print("unknown instruction")

    elif funct7 == "0100000":
      if funct3 == "000":
        print("sub ",end='')
        type_R_print(rs2,rs1,rd)

      elif funct3 == "101":
        print("sra ",end='')
        type_R_print(rs2,rs1,rd)

      else:
        print("unknown instruction")

    else:
      print("unknown instruction")

  else: #error
    print("unknown instruction")

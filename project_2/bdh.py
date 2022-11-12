#!/usr/bin/python3
import sys

fname = sys.argv[1]
N = int(sys.argv[2])
FH = open(fname, 'rb')
list_hexa = []
list_bin = []
temp1 = 0
while temp1 < 4*N:
  s = FH.read(1)
  if len(s) == 0:
    print("No more instructions")
    break

  else:
    if len(hex(ord(s))) == 3:
      list_hexa.append("0x0" + str(hex(ord(s))[-1]))
    else:
      list_hexa.append(str(hex(ord(s))))
  list_bin.append("0b" + '0' * (10 - len(bin(ord(s)))) + str(bin(ord(s))[2:]))
  temp1 += 1
FH.close()

k = 3
sorted_list_hexa = []
sorted_list_bin = []
while (k < len(list_hexa)):
  sorted_list_hexa.append(list_hexa[k])
  sorted_list_bin.append(list_bin[k])
  if (k % 4 == 0):
    k += 7
    continue
  k -= 1

inst_hexa = []
inst_bin = []
for i in range(len(sorted_list_hexa)):
  if (i % 4 == 0):
    inst_hexa.append(sorted_list_hexa[i][2:])
    inst_bin.append(sorted_list_bin[i][2:])
  else:
    inst_hexa[i // 4] += sorted_list_hexa[i][2:]
    inst_bin[i // 4] += sorted_list_bin[i][2:]


def name_regs(rs):
  result = 0
  exp = 1
  for i in range(len(rs)):
    result += (int(rs[len(rs) - 1 - i]) * exp)
    exp *= 2
  return result


def shamt_int_imm(imm):
  result = 0
  exp = 1
  for i in range(len(imm)):
    result += (int(imm[len(imm) - 1 - i]) * exp)
    exp *= 2
  return result


def final(x):
  return x % (2**32)


def s_int_imm(imm):
  result = 0
  exp = 1
  if int(imm[0]) == 1:
    result = -(2**(len(imm) - 1))
    for i in range(len(imm) - 1):
      result += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  else:
    for i in range(len(imm) - 1):
      result += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  return result


def u_int_imm(imm):
  result = 0
  exp = 2**12
  if int(imm[0]) == 1:
    result = -(2**(len(imm) - 1 + 12))
    for i in range(len(imm) - 1):
      result += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  else:
    for i in range(len(imm) - 1):
      result += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  return result


def b_int_imm(imm):
  result = 0
  exp = 2
  if int(imm[0]) == 1:
    result = -(2**(len(imm) - 1 + 1))
    for i in range(len(imm) - 1):
      result += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  else:
    for i in range(len(imm) - 1):
      result += (int(imm[len(imm) - 1 - i]) * exp)
      exp *= 2
  return result


def s2u(x):
  if x >= 0:
    return x
  else:
    return x + 2**32


U_type = ["0110111", "0010111"]
J_type = ["1101111"]
I_type = ["1100111", "0000011", "0010011"]
B_type = ["1100011"]
S_type = ["0100011"]
R_type = ["0110011"]


def dec2hex(x):
  if x < 0:
    x += 2**32
  if len(str(hex(x))) >= 10:
    return str(hex(x % (2**32)))
  else:
    return "0x" + "0" * (10 - len(str(hex(x)))) + str(hex(x))[2:]


x = [0 for i in range(0, 32)]

for i in range(len(inst_hexa)):
  opcode = inst_bin[i][25:32]
  if opcode in U_type:
    imm = inst_bin[i][:20]
    rd = inst_bin[i][20:25]

    if opcode == "0110111":
      #lui
      x[name_regs(rd)] = final(u_int_imm(imm))

  elif opcode in I_type:
    imm = inst_bin[i][:12]
    rs1 = inst_bin[i][12:17]
    funct3 = inst_bin[i][17:20]
    rd = inst_bin[i][20:25]

    if funct3 == "000":
      #addi
      x[name_regs(rd)] = final((x[name_regs(rs1)] + s_int_imm(imm)))

    elif funct3 == "010":
      #slti
      if x[name_regs(rs1)] >= 2**31:
        temp = x[name_regs(rs1)] - 2**32
      else:
        temp = x[name_regs(rs1)]
      if temp < (s_int_imm(imm)):
        x[name_regs(rd)] = 1
      else:
        x[name_regs(rd)] = 0

    elif funct3 == "011":
      #sltui
      if (x[name_regs(rs1)] < (s_int_imm(imm))):
        x[name_regs(rd)] = 1
      else:
        x[name_regs(rd)] = 0

    elif funct3 == "100":
      #xori
      x[name_regs(rd)] = int((s_int_imm(imm)) ^ (x[name_regs(rs1)]))

    elif funct3 == "110":
      #ori
      x[name_regs(rd)] = int((s_int_imm(imm)) | (x[name_regs(rs1)]))

    elif funct3 == "111":
      #andi
      x[name_regs(rd)] = final(int((s_int_imm(imm)) & (x[name_regs(rs1)])))

    elif funct3 == "001":
      shamt = imm[7:]
      if imm[:7] == "0000000":
        #slli
        x[name_regs(rd)] = final(
          int((x[name_regs(rs1)]) << shamt_int_imm(shamt)))

    elif funct3 == "101":
      shamt = imm[7:]
      if imm[:7] == "0000000":
        #srli
        x[name_regs(rd)] = final(
          int((x[name_regs(rs1)]) >> shamt_int_imm(shamt)))

      elif imm[:7] == "0100000":
        #srai
        x[name_regs(rd)] = 0
        if x[name_regs(rs1)] >= 2**31:
          for i in range(shamt_int_imm(shamt)):
            x[name_regs(rd)] += 2**(31 - i)
        x[name_regs(rd)] += int(
          (x[name_regs(rs1)]) >> (shamt_int_imm(shamt)))

  elif opcode in R_type:
    funct7 = inst_bin[i][:7]
    rs2 = inst_bin[i][7:12]
    rs1 = inst_bin[i][12:17]
    funct3 = inst_bin[i][17:20]
    rd = inst_bin[i][20:25]

    if funct7 == "0000000":
      if funct3 == "000":
        #add
        x[name_regs(rd)] = final(x[name_regs(rs1)] + x[name_regs(rs2)])

      elif funct3 == "001":
        #sll
        x[name_regs(rd)] = final(x[name_regs(rs1)] << x[name_regs(rs2)])

      elif funct3 == "010":
        #slt
        if (x[name_regs(rs1)] >= 2**31):
          temp1 = x[name_regs(rs1)] - 2**32
        else:
          temp1 = x[name_regs(rs1)]

        if (x[name_regs(rs2)] >= 2**31):
          temp2 = x[name_regs(rs2)] - 2**32
        else:
          temp2 = x[name_regs(rs2)]

        if (temp1 < temp2):
          x[name_regs(rd)] = 1
        else:
          x[name_regs(rd)] = 0

      elif funct3 == "011":
        #sltu
        if (s2u(x[name_regs(rs1)]) < s2u(x[name_regs(rs2)])):
          x[name_regs(rd)] = 1
        else:
          x[name_regs(rd)] = 0

      elif funct3 == "100":
        #xor
        x[name_regs(rd)] = final((x[name_regs(rs1)]) ^ (x[name_regs(rs2)]))

      elif funct3 == "101":
        #srl
        x[name_regs(rd)] = final((x[name_regs(rs1)]) >> x[name_regs(rs2)])

      elif funct3 == "110":
        #or
        x[name_regs(rd)] = final((x[name_regs(rs1)]) | (x[name_regs(rs2)]))

      elif funct3 == "111":
        #and
        x[name_regs(rd)] = final((x[name_regs(rs1)]) & (x[name_regs(rs2)]))

    elif funct7 == "0100000":
      if funct3 == "000":
        #sub
        x[name_regs(rd)] = final(x[name_regs(rs1)] - x[name_regs(rs2)])

      elif funct3 == "101":
        #sra
        x[name_regs(rd)] = 0
        if (x[name_regs(rs1)] >= 2**31):
          for i in range(x[name_regs(rs2)]):
            x[name_regs(rd)] += 2**(31 - i)
        x[name_regs(rd)] += final((x[name_regs(rs1)]) >> x[name_regs(rs2)])

for i in range(0, 32):
  print(f"x{i}: {dec2hex(x[i])}")

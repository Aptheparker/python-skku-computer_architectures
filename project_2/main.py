#!/usr/binary/python3
import sys

filename = sys.argv[1]
N = int(sys.argv[2])
hexa = []
binary = []

counter = 0

#read file
with open(filename, 'rb') as byte_file:

    for i in range(4*N):
      byte = byte_file.read(1) #read 1 byte = 8 bits
      if len(byte) == 0:
        break

      else:
        if len(hex(ord(byte))) == 3: #length
          hexa.append("0x0" + str(hex(ord(byte))[-1]))
        else:
          hexa.append(str(hex(ord(byte))))

      binary.append("0b" + '0' * (10 - len(bin(ord(byte)))) + str(bin(ord(byte))[2:]))
      counter += 1
    
byte_file.close()

if counter < 4*N:
  print('No more instructions')

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
  return output

registers = [] #all registers
for i in range(32):
  registers.append(register('00000'))

def final(x):
  return x % (2**32)

def sign2unsign(x):
  if x >= 0:
    return x
  else:
    return x + 2**32

#decimal to hexa
def dec2hex(input):
  if input < 0:
    input += 2**32
  if len(str(hex(input))) >= 10:
    return str(hex(input % (2**32)))
  else:
    return "0x" + "0" * (10 - len(str(hex(input)))) + str(hex(input))[2:]

def shamt_int_imm(imm):
  output = 0
  exp = 1
  for i in range(len(imm)):
    output += (int(imm[len(imm) - 1 - i]) * exp)
    exp *= 2
  return output

def sign_int_imm(imm): # signed
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
  return output

def u_int_imm(imm): #unsigned
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
  return output

#types
type_U = ["0110111", "0010111"]
type_I = ["1100111", "0000011", "0010011"]
type_R = ["0110011"]

for i in range(len(inst_hexa)):
  opcode = inst_binary[i][25:32]
  if opcode in type_U:
    imm = inst_binary[i][:20]
    rd = inst_binary[i][20:25]

    if opcode == "0110111":
      #lui
      registers[register(rd)] = final(u_int_imm(imm))

  elif opcode in type_I:
    imm = inst_binary[i][:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]
    rd = inst_binary[i][20:25]

    if funct3 == "000":
      #addi
      registers[register(rd)] = final((registers[register(rs1)] + sign_int_imm(imm)))

    elif funct3 == "010":
      #slti
      if registers[register(rs1)] >= 2**31:
        temp = registers[register(rs1)] - 2**32
      else:
        temp = registers[register(rs1)]
      if temp < (sign_int_imm(imm)):
        registers[register(rd)] = 1
      else:
        registers[register(rd)] = 0

    elif funct3 == "011":
      #sltui
      if (registers[register(rs1)] < (sign_int_imm(imm))):
        registers[register(rd)] = 1
      else:
        registers[register(rd)] = 0

    elif funct3 == "100":
      #xori
      registers[register(rd)] = int((sign_int_imm(imm)) ^ (registers[register(rs1)]))

    elif funct3 == "110":
      #ori
      registers[register(rd)] = int((sign_int_imm(imm)) | (registers[register(rs1)]))

    elif funct3 == "111":
      #andi
      registers[register(rd)] = final(int((sign_int_imm(imm)) & (registers[register(rs1)])))

    elif funct3 == "001":
      shamt = imm[7:]
      if imm[:7] == "0000000":
        #slli
        registers[register(rd)] = final(
          int((registers[register(rs1)]) << shamt_int_imm(shamt)))

    elif funct3 == "101":
      shamt = imm[7:]
      if imm[:7] == "0000000":
        #srli
        registers[register(rd)] = final(
          int((registers[register(rs1)]) >> shamt_int_imm(shamt)))

      elif imm[:7] == "0100000":
        #srai
        registers[register(rd)] = 0
        if registers[register(rs1)] >= 2**31:
          for i in range(shamt_int_imm(shamt)):
            registers[register(rd)] += 2**(31 - i)
        registers[register(rd)] += int(
          (registers[register(rs1)]) >> (shamt_int_imm(shamt)))

  elif opcode in type_R:
    funct7 = inst_binary[i][:7]
    rs2 = inst_binary[i][7:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]
    rd = inst_binary[i][20:25]

    if funct7 == "0000000":
      if funct3 == "000":
        #add
        registers[register(rd)] = final(registers[register(rs1)] + registers[register(rs2)])

      elif funct3 == "001":
        #sll
        registers[register(rd)] = final(registers[register(rs1)] << registers[register(rs2)])

      elif funct3 == "010":
        #slt
        if (registers[register(rs1)] >= 2**31):
          temp1 = registers[register(rs1)] - 2**32
        else:
          temp1 = registers[register(rs1)]

        if (registers[register(rs2)] >= 2**31):
          temp2 = registers[register(rs2)] - 2**32
        else:
          temp2 = registers[register(rs2)]

        if (temp1 < temp2):
          registers[register(rd)] = 1
        else:
          registers[register(rd)] = 0

      elif funct3 == "011":
        #sltu
        if (sign2unsign(registers[register(rs1)]) < sign2unsign(registers[register(rs2)])):
          registers[register(rd)] = 1
        else:
          registers[register(rd)] = 0

      elif funct3 == "100":
        #xor
        registers[register(rd)] = final((registers[register(rs1)]) ^ (registers[register(rs2)]))

      elif funct3 == "101":
        #srl
        registers[register(rd)] = final((registers[register(rs1)]) >> registers[register(rs2)])

      elif funct3 == "110":
        #or
        registers[register(rd)] = final((registers[register(rs1)]) | (registers[register(rs2)]))

      elif funct3 == "111":
        #and
        registers[register(rd)] = final((registers[register(rs1)]) & (registers[register(rs2)]))

    elif funct7 == "0100000":
      if funct3 == "000":
        #sub
        registers[register(rd)] = final(registers[register(rs1)] - registers[register(rs2)])

      elif funct3 == "101":
        #sra
        registers[register(rd)] = 0
        if (registers[register(rs1)] >= 2**31):
          for i in range(registers[register(rs2)]):
            registers[register(rd)] += 2**(31 - i)
        registers[register(rd)] += final((registers[register(rs1)]) >> registers[register(rs2)])

for i in range(32):
  print(f"x{i}: {dec2hex(registers[i])} ", end='\n')
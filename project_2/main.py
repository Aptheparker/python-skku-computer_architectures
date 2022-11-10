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

def unsigned(n):
  return n & 0xffffffff


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

def shamt_int_imm(imm):
    output = 0
    exp = 1
    for i in range(len(imm)):
        output += (int(imm[len(imm)-1-i]) * exp)
        exp *= 2
    return output

def u_int_imm(imm):
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

#for any print
for i in range(len(inst_hexa)):
  opcode = inst_binary[i][25:32] #opcodes are all same
  
#U type  
  if opcode in type_U:
    imm = inst_binary[i][:20]
    rd = inst_binary[i][20:25]

    if opcode == "0110111": #lui
      registers[register(rd)] = shamt_int_imm(imm)<<12

#I type
  elif opcode in type_I:
    imm = inst_binary[i][:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]
    rd = inst_binary[i][20:25]

    if funct3 == "000": #addi
      registers[register(rd)] = registers[register(rs1)] + shamt_int_imm(imm)

    elif funct3 == "010": #slti
      registers[register(rd)] = registers[register(rs1)] < shamt_int_imm(imm)

    elif funct3 == "011": #sltiu
      registers[register(rd)] = registers[register(rs1)] < u_int_imm(imm)

    elif funct3 == "100": #xori
      registers[register(rd)] = registers[register(rs1)] ^ shamt_int_imm(imm)

    elif funct3 == "110": #ori
      registers[register(rd)] = registers[register(rs1)] | shamt_int_imm(imm)

    elif funct3 == "111": #andi
      registers[register(rd)] = registers[register(rs1)] & shamt_int_imm(imm)

    elif funct3 == "001":

      if imm[:7] == "0000000": #slli
        registers[register(rd)] = registers[register(rs1)] << shamt_int_imm(imm)

      else:
        print("unknown instruction")

    elif funct3 == "101":

      shamt = imm[7:]

      if imm[:7] == "0000000": #srli
        registers[register(rd)] = registers[register(rs1)] >> shamt_int_imm(shamt)

      elif imm[:7] == "0100000": #srai
        registers[register(rd)] = registers[register(rs1)] >> shamt_int_imm(imm)

      else:
        print("unknown instruction")

    else:
      print("unknown instruction")

  elif opcode in type_R: #R type
    funct7 = inst_binary[i][:7]
    rs2 = inst_binary[i][7:12]
    rs1 = inst_binary[i][12:17]
    funct3 = inst_binary[i][17:20]
    rd = inst_binary[i][20:25]

    if funct7 == "0000000": #add
      if funct3 == "000":
        registers[register(rd)] = registers[register(rs1)] + registers[register(rs2)]

      elif funct3 == "001":
        print("sll ",end='')

      elif funct3 == "010": #slt
        registers[register(rd)] = registers[register(rs1)] < shamt_int_imm(imm)

      elif funct3 == "011":
        print("sltu ",end='')

      elif funct3 == "100":
        print("xor ",end='')

      elif funct3 == "101":
        print("srl ",end='')

      elif funct3 == "110":
        print("or ",end='')

      elif funct3 == "111":
        print("and ",end='')

      else:
        print("unknown instruction")

    elif funct7 == "0100000":
      if funct3 == "000":
        print("sub ",end='')

      elif funct3 == "101":
        print("sra ",end='')

      else:
        print("unknown instruction")

    else:
      print("unknown instruction")

  else:
    print("unknown instruction")

for i in range(32):
  print(f"x{i}: {hex(registers[i])} ", end='\n')
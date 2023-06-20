import struct
import os
from tkinter import filedialog as fd
import random
seeds = []
files = []
extensions = []
#Unpack NSPK 4.0 and 5.0
file = fd.askopenfilename()

f = open(file, "r+b")
f2 = open(file+"decrypted", "w+b")
#Check for encryption. If it's encrypted, decode the file.
ENCCHK = f.read(4)
if ENCCHK[0] == 0x45 and ENCCHK [3] == 0x52:
    f.seek(0x10)
    seed = f.read(4)
    random.seed(seed)
    SUB = random.randint(25, 80)
    A = f.read(os.path.getsize(file)-0x14)
    print(SUB)
    for i in A:
        i-=SUB
        if i < 0:
            i+=256
        f2.write(struct.pack('<B',i))
    f2.flush()
    f.close()
    f = open(file+"decrypted", "r+b")
    f.seek(0)
f2.close()

#Check what mode this file is in
VER = f.read(4).decode('UTF-8')
print(VER)
if VER == "NSP0":
    print("This NSPK is in mode 0, skip the path info!")
    #File Count
    FCNT = struct.unpack("<I", f.read(4))[0]
    #Header Size
    HDSI = struct.unpack("<I", f.read(4))[0]
    #File Name Length
    FNLN = struct.unpack("<I", f.read(4))[0]
    #File Extension Count
    FXCT = struct.unpack("<B", f.read(1))[0]
    #File Extension Length
    FXLN = struct.unpack("<B", f.read(1))[0]
    folder = fd.askdirectory()
#Get the random encryption seeds
for i in range(FXCT):
    seed = str(f.read(4).decode('UTF-8'))
    seeds.append(seed)
#Decrypt the file extension table
for i in range(FXCT):
    EDEC = ""
    ext = str(f.read(FXLN).decode('UTF-8'))
    if ext[len(ext)-1].encode('UTF-8') == b'\x00':
        ext = ext[0:len(ext)-1]
    random.seed(seeds[i])
    DIFF = random.randint(2,10)
    for i in range(len(ext)):
        CHR = chr(str(ext[i-len(ext)+1]).encode('UTF-8')[0]-DIFF)
        EDEC=EDEC+CHR
    extensions.append(EDEC)
    print(EDEC)
LEN = 0
#Decrypt the file table while reading it
for i in range(FCNT):
    LEN = 0
    NDEC = ''
    seed = str(f.read(4).decode('UTF-8'))
    name = str(f.read(FNLN).decode('UTF-8'))
    for i in range(len(name)+1):
        try:
            if name[i].encode('UTF-8') == b'\x00':
                LEN = i
                break
        except:
            LEN = len(name)
    name = name[0:LEN]
    random.seed(seed)
    DIFF = random.randint(2,10)
    for i in range(len(name)):
        CHR = chr(str(name[i-len(name)+1]).encode('UTF-8')[0]-DIFF)
        NDEC=NDEC+CHR
    print(NDEC)
    startoffset = struct.unpack("<I", f.read(4))[0]+HDSI
    SIZE = struct.unpack("<I", f.read(4))[0]
    EXT = struct.unpack("<B", f.read(1))[0]
    stuff = NDEC, startoffset, SIZE, EXT
    files.append(stuff)
for i in files:
    fn = i[0]
    so = i[1]
    si = i[2]
    ex = i[3]
    if ex != 0:
        try:
            name = fn+"."+extensions[ex-1]
        except:
            "error!"
            name = fn
    else:
        name = fn
    op = open(folder+"/"+name, "w+b")
    f.seek(so)
    print(hex(so))
    seed = f.read(4).decode("UTF-8")
    
    DTA = f.read(si-4)
    random.seed(seed)
    ADD = random.randint(2, 10)
    DAT1 = ""
    for i in DTA:
        DAT1 = i-ADD
        if DAT1 < 0:
            DAT1 = DAT1 + 256
        op.write(struct.pack("<B",DAT1))
        op.flush()
op.close()
f.close()
#os.remove(file+"decrypted")

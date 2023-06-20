import struct
import os
from tkinter import filedialog as fd
import random
#For file extensions. Used to cut down the header size even more without the use of compression.
types = []
#Used later to hold the filename followed up with the extension and the extension ID.
#Might still need a bit of work though...
files2 = []
folder = fd.askdirectory()
packname = folder.split("/")
packname = packname[len(packname)-1]
files = os.listdir(folder)
longest = ""
mode = 0
modes = False
if len(folder) <= 255 and modes == True:
    fldlen = struct.pack("<B",len(folder))
    mode = 1
if len(folder) > 255 and modes == True:
    fldlen = struct.pack("<H",len(folder))
    mode = 2
#Prepare the folder string to be written to the file
feld = ""
for i in range(int((len(folder))/2)):
    A = folder[i*2]
    B = folder[i*2+1]
    feld = feld+str(B+A)
print(feld)
fld = folder.encode('UTF-8')
#Create some variables that get used later on
ID = 0
LONG = 0
ID1 = 0
T = False
#ty is the filename, Type is the extension, L is just the length of the extension.
for ty in files:
    try:
        Type = ty.split(".")[1]
        ty = ty.split(".")[0]
        L = len(Type)
        if L >= LONG:
            LONG = L
        if Type not in types:
            
            types.append(Type)
            ID += 1
            dat = ty, Type, ID
            print(ty, Type, ID)
        else:
            while T == False:
                if Type == types[ID1]:
                    T = True
                ID1+=1
            print(ty, Type, ID1+1)
            dat = ty, Type, ID1+1
            
        
    except:
        "No EXT to split out of filename! Give it an ID of 0!"
        dat = ty, "", 0
        print(dat[0], "NO_EXT", dat[2])
    files2.append(dat)
    ID1 = 0
for _ in files:
    _ = str(_.split(".")[0])
    if len(_) > len(longest):
        longest = _
scale = len(longest)
#"Padding" isn't actually padding.
padding = struct.pack("<I", scale)
scale2 = scale+0x9
print(scale2)
listd = []
f = open(packname+".nsp","w+b")
#For Files Only Mode (PM00). No path in the header, all files unpack to whatever path you choose.
if mode == 0:
    f.write(b'NSP0')
#For Original Path Mode (PM08). Makes it so the package unpacks to the original location it was created from.
if mode == 1:
    f.write(b'NSP1')
#For 16-Bit Path Mode (PM16). Sets some values to be 16-Bit.
if mode == 2:
    f.write(b'NSP2')
if mode >= 1:
    f.write(fldlen), f.write(fld)
fcount = struct.pack("<I", len(files))
typecnt = struct.pack("<B", len(types))
extlen = struct.pack("<B", LONG)
#Set the mode. If it's in 16-Bit path mode, it adds one byte to the header.
if mode == 0:
    hsize = struct.pack("<I", len(files)*scale2+0x10+(((len(types)*2)*LONG))+2)
if mode == 1:
    hsize = struct.pack("<I", len(files)*scale2+0x10+len(folder)+((len(types)*LONG))+3)
if mode == 2:
    hsize = struct.pack("<I", len(files)*scale2+0x10+len(folder)+((len(types)*LONG))+4)
f.write(fcount), f.write(hsize), f.write(padding), f.write(typecnt), f.write(extlen)
f.flush()
efiles = []
offset = 0
for Type in types:
    ext = ""
    seed = str(hash(str(random.choice(types))+str(random.randint(0, 25000))))[1:5]
    random.seed(seed)
    ADD = random.randint(-3,3)
    for i in range(len(Type)):
        DAT1 = str(Type[i-1]).encode('UTF-8')[0]
        DAT2 = chr(DAT1+ADD)
        ext=ext+DAT2
    
    efile = ext.encode('UTF-8')
    efiledec = seed.encode('UTF-8')
    while len(efile) != LONG:
        efile = efile+b'\x00'
    
    ETEST = ""
    random.seed(seed)
    ADD = random.randint(-3,3)
    for i in range(len(ext)):
        DAT1 = str(ext[i-len(ext)+1]).encode('UTF-8')[0]
        DAT2 = chr(DAT1-ADD)
        ETEST=ETEST+DAT2
    f.write(efiledec)
    efiles.append(efile)
    print(ETEST)
for efile in efiles:
    f.write(efile)
for file in files2:
    bfile = file[0].encode('UTF-8')
    while len(bfile) != scale:
        bfile = bfile+b'\x00'
    EXT = struct.pack("<B",file[2])
    if EXT[0] != 0:
        flength=os.path.getsize(folder+"/"+file[0]+"."+file[1])
        infos = [folder+"/"+file[0]+"."+file[1], bfile, offset, flength]
    if EXT[0] == 0:
        flength=os.path.getsize(folder+"/"+file[0])
        infos = [folder+"/"+file[0], bfile, offset, flength]
    listd.append(infos) 
    f.write(bfile)
    f.write(struct.pack("<I", offset))
    f.write(struct.pack("<I", flength))
    f.write(EXT)
    offset+=flength
f.flush()
for info in listd:
    g = open(info[0], "r+b")
    f.write(g.read(info[3]))
    g.close()
g.close()
f.close()

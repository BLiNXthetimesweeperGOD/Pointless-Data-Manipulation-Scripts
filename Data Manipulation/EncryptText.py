#String scrambler + "encryption" (can be reversed)
import random
import struct

#A function that generates a random seed using a list
def generate_seed():
    #The seed generation list (done this way to ensure it's all a string and doesn't contain any non-ascii characters)
    sRand = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "_", " ", "=", "+", "*", "/", 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g', 'H', 'h', 'I', 'i', 'J', 'j', 'K', 'k', 'L', 'l', 'M', 'm', 'N', 'n', 'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u', 'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z']
    #The seed size list. Whichever value gets chosen will be the length of the final seed.
    sizes = [16,32,48,64]
    #Choose a length from the sizes list for the seed
    seedLength = random.choice(sizes)
    files = 0 #Leftover from my old script. Might get used eventually for when support for binary files gets added.
    #Create the seed variable
    seed1 = str(random.choice(sRand))
    #Generate a seed that's at the size of seedLength
    for i in range(seedLength-1):
        seed1 = seed1+str(random.choice(sRand))
    return seed1, seedLength

#A function that shifts bits by the amount you tell it to
def encrypt(message, shift):
    # Convert the message to binary
    binary = "".join(format(ord(c), "08b") for c in message)
    # Shift the bits by the given amount
    shifted = binary[shift:] + binary[:shift]
    # Convert the shifted binary back to characters
    encrypted = "".join(chr(int(shifted[i:i+8], 2)) for i in range(0, len(shifted), 8))
    # Return the encrypted message
    return encrypted

#A function that shifts bits by the amount you tell it to (in the opposite direction of the previous one)
def decrypt(message, shift):
    # Convert the message to binary
    binary = "".join(format(ord(c), "08b") for c in message)
    # Shift the bits to the right by the given amount
    shifted = binary[-shift:] + binary[:-shift]
    # Convert the shifted binary back to characters
    decrypted = "".join(chr(int(shifted[i:i+8], 2)) for i in range(0, len(shifted), 8))
    # Return the decrypted message
    return decrypted

#Shuffles/scrambles text
def shuffle_text(text):
    #Initialize an empty string and two empty lists
    newstring = ""
    shiftlist = []
    letterlist = []
    #Shuffle the text
    for i in range(len(text)):
        #Make sure no repeated characters get added by checking if what we have is in the shiftlist list
        while True:
            #Choose a random value within the length of the text string
            shift = random.randint(0, len(text)-1)
            #Break the loop if the value is not in the shiftlist list
            if shift not in shiftlist:
                break
        #L = Letter. It grabs a letter using shift as the index.
        L = text[shift]
        #Add the letter to newstring, effectively shuffling the text string
        newstring = newstring+L
        #Now add these to the shiftlist and letterlist lists for later (used to de-scramble the text/data)
        shiftlist.append(shift)
        letterlist.append(L)
    #Return the shuffled string and the two lists
    return newstring, shiftlist, letterlist

#Reverses the shuffling/scrambling done by the previous function
def deshuffle_text(newstring, shiftlist, letterlist):
    #Initialize an empty string and a variable to keep track of the sequence
    restored = ""
    seq = 0
    #De-shuffle the text using the lists we generated
    for i in range(len(newstring)):
        #Find the index of seq in the shiftlist list
        index = shiftlist.index(seq)
        #Get the corresponding letter from the letterlist list
        L = letterlist[index]
        #Add the letter to restored, effectively deshuffling the string
        restored = restored+L
        #Increment the seq variable by 1 to get the next letter in the letter list
        seq+=1
    #Return the restored string
    return restored

#Generate a seed of a randomly chosen length
seed = generate_seed()

#Create some variables for the file using the output from generate_seed
seed1 = seed[0]
seedLength = seed[1]

#Use our generated seed as the random seed
random.seed(seed1)

#The test string
TEST = str("""Hello there!
If you decoded this, you figured out my really simple 'encryption' algorithm.
It's really just shuffling the letters, but I still put a bit of time into it...
Anyways, have fun telling people that you decrypted some pointlessly encrypted text.
Also, just to pad out the file a bit and throw people off:
3209492350312805923805831058310581390589310901gfrdgsafdsgawrtgiwfgvhagihngnriagngfnisdaningianenhgaitgniankjgnjksdagkbhwkfgnkdsbgkasbkgsdkgadsh
BLiNX 3
Hello there!!!!
Wii U
Yes, this string is really long just to make it extra difficult to decode.
No, there's nothing secret hidden in it.
Seriously, why would I hide something personal in a file that's meant to be treated more like a puzzle?
That'd just be really weird and out of place here.
Ok, this is the last line.""")

#Shuffle the text
shuffled = shuffle_text(TEST)

#Create variables using the output from shuffle_text
newstring = shuffled[0]
shiftlist = shuffled[1]
letterlist= shuffled[2]

#Generate a random shift value for the bit shift functions to use
randomshift = random.randint(1, 7)

#Open a new "scrambled.SCB" file to write data to
f = open("scrambled.SCB", 'w+b')

#Start writing the data to scrambled.SCB
f.write(b'ENC\x00'+struct.pack("<I", seedLength)+b'\x00\x00\x00\x00'+struct.pack("<I", len(TEST))+seed1.encode("UTF-8"))

#Go through and write the numbers used to de-scramble the scrambled string into the scrambled.SCB file (in the order that they're placed in the list)
for number in shiftlist:
    f.write(struct.pack("<I", number))

#Write the random bit shift amount value right before the string, as that's what's been bit shifted
#(and because it'll confuse people that actually take this seriously)
f.write(struct.pack("<I", randomshift))

#Encrypt the message by shifting the bits by our randomly chosen amount
encryptedshift = encrypt(newstring, randomshift)

#Write the now bit shifted text into the scrambled.SCB file
for letter in encryptedshift:
    f.write(letter.encode("UTF-8"))

#Flush f and close the file
f.flush()
f.close()

#Restore the encrypted data to make sure the script worked correctly
decryptedshift = decrypt(encryptedshift, randomshift)
restored = deshuffle_text(decryptedshift,shiftlist,letterlist)

#Print the restored output
print(restored)

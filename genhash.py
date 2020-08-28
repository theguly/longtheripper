import hashlib,binascii
import random
import string

chars           = string.ascii_letters
word_count      = 400
word_len        = 30
suffix_count    = 50
suffix_len      = 3
prefix_count    = 50
prefix_len      = 3
cracked_count   = 3
uncracked_count = 3
wordlist        = []
suffix          = []
prefix          = []
plaintext       = []
hashes          = []

def generate(count,length):
    ret = []
    for x in range(count):
        ret.append(''.join(random.choice(chars) for x in range(length)))
    return ret

def writefile(l,fname):
    with open(fname, 'w') as f:
        for item in l:
            f.write("%s\n" % item)
    f.close()

print("i'm overwriting plaintext, hashes, wordlist, prefix, suffix. hit enter to continue.")
input()

# stop editing
# stop editing
# stop editing

suffix   = generate(suffix_count,suffix_len)
prefix   = generate(prefix_count,prefix_len)
wordlist = generate(word_count,word_len)

writefile(suffix,'suffix')
writefile(prefix,'prefix')
writefile(wordlist,'wordlist')

# generate hashes file
for i in range(cracked_count):
    s = suffix[random.randint(0,len(suffix)-1)]
    p = prefix[random.randint(0,len(prefix)-1)]
    w = wordlist[random.randint(0,len(wordlist)-1)]

    plaintext.append(p+w+s)

for i in range(uncracked_count):
    length = prefix_len+word_len+suffix_len
    uncracked = generate(1,length)[0]
    while uncracked in wordlist:
        uncracked = generate(1,length)[0]
    plaintext.append(uncracked)


random.shuffle(plaintext)
writefile(plaintext,'plaintext')

for i in range(len(plaintext)):
    plain = plaintext[i]

    ntlm = binascii.hexlify(hashlib.new('md4', plain.encode('utf-16le')).digest()).decode("utf-8")
    # have some entry with just hash and some with user:hash
    if i % 2:
        u = generate(1,6)[0]
        ntlm = u+':'+ntlm

    hashes.append(ntlm)
writefile(hashes,'hashes')

print("done")

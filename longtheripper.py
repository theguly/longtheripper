#!/usr/bin/python3.8
import multiprocessing as mp
import hashlib,binascii
from time import time,sleep
import argparse
from sys import exit,stderr

# author:  Sandro 'guly' Zaccarini
# version: 0.1

# based on my tests, there is no value in adding more than 2+2.
CONSUMERS   = 2
PRODUCERS   = 2
STATS       = 3
DEBUG       = False

hashes      = []
userhash    = {}
wordlist    = ['']
prefix      = ['']
suffix      = ['']
p_producers = []
p_consumers = []
p_stats     = []

def debug(x):
    if DEBUG:
        print(x,flush=True)

def prep_stats():
    t1 = time()
    data = {
        'recovered': int(q_recovered.qsize()),
        'hashes': hash_num,
        'checked': int(q_done.qsize()),
        'total': total,
        'percentage': int(q_done.qsize()*100/total),
        'rate': int(q_done.qsize()/((t1-t0)*1000)),
        'pad': " "
    }
    return data

def doexit(msg):
    # sentinel
    for i in range(CONSUMERS):
        debug("sending sentinel")
        q.put(None)

    data = prep_stats()
    print("\nRecovered {recovered}/{hashes} checked {checked}/{total} ({percentage}%) rate: {rate}kH/s{pad:11}".format(**data),flush=True)
    print(msg,flush=True)

    # kindly ask everyone to die
    for s in p_stats:
        debug("killing stats")
        s.kill()
        debug("killed")
    for p in p_producers:
        debug("killing producer")
        p.kill()
        debug("killed")
    for c in p_consumers:
        debug("killing consumer")
        c.kill()
        debug("killed")

    exit()

def stats():
    while True:
        data = prep_stats()
        print("recovered {recovered}/{hashes} checked {checked}/{total} ({percentage}%) rate: {rate}kH/s{pad:11}\r".format(**data),flush=True)

        sleep(STATS)

        if q_done.qsize() >= total:
            doexit('all done')
        elif q_recovered.qsize() >= hash_num:
            doexit("\nall hashes recovered!!!1!1")


def printhelp(err):
    print('Error: {}\n'.format(err),flush=True)
    parser.print_help(stderr)
    exit(1)

def loadfile(fname,mylist):
    with open (fname,'r') as f:
        for line in f:
            mylist.append(line.strip())

def checkhash(item):
    passwd,ntlm = item
    if ntlm in hashes:
        q_recovered.put(item)
        if ntlm in userhash:
            print("\nplaintext recovered for {}:{} => {}".format(userhash[ntlm],ntlm,passwd),flush=True)
        else:
            print("\nplaintext recovered for {} => {}".format(ntlm,passwd),flush=True)

def consumer(q,q_done):
    name = mp.current_process().name
    while True:
        item = q.get()
        if item is None: # detect sentinel
            q.task_done()
            break
        checkhash(item)
        q_done.put("x")
        q.task_done()
    debug("=========consumer {} done".format(name))

def producer(q,mywords):
    name = mp.current_process().name
    for word in words:
        for suf in suffix:
            for pre in prefix:
                passwd = pre+word+suf
                ntlm = binascii.hexlify(hashlib.new('md4', passwd.encode('utf-16le')).digest()).decode("utf-8")
                toput = [passwd,ntlm]
                q.put(toput)
    q.close()
    debug("=========producer {} done".format(name))

def doparse():
    parser.add_argument('-S','--suffix', dest='suffix', action='store', help='suffix string')
    parser.add_argument('-s','--suffix_file', dest='suffix_file', action='store', help='file containing suffix')

    parser.add_argument('-P','--prefix', dest='prefix', action='store', help='prefix string')
    parser.add_argument('-p','--prefix_file', dest='prefix_file', action='store', help='file containing prefix')

    parser.add_argument('-N','--ntlm', dest='ntlm', action='store', help='single ntlm to crack')
    parser.add_argument('-n','--ntlm_file', dest='ntlm_file', action='store', help='file containing list of ntlm to crack')

    parser.add_argument('-W','--word', dest='word', action='store', help='single word to check')
    parser.add_argument('-w','--wordlist', dest='word_file', action='store', help='wordlist')

    args = parser.parse_args()

    if not args.word_file is None:
        loadfile(args.word_file,wordlist)
    if not args.word is None:
        wordlist.append(args.word)
    if len(wordlist) < 1:
        printhelp('missing both word and wordlist')

    if not args.ntlm_file is None:
        loadfile(args.ntlm_file,hashes)
    if not args.ntlm is None:
        hashes.append(args.ntlm)
    if len(hashes) < 1:
        printhelp('missing both hash and hashfile')
    for line in hashes:
        if ':' in line:
            u,h = line.split(':')
            userhash[h]=u
            hashes.remove(line)
            hashes.append(h)

    if not args.suffix_file is None:
        loadfile(args.suffix_file,suffix)
    if not args.suffix is None:
        suffix.append(args.suffix)
    if not args.prefix_file is None:
        loadfile(args.prefix_file,prefix)
    if not args.prefix is None:
        prefix.append(args.prefix)
    return args

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Long the Ripper.\n")
    args = doparse()

    total = len(wordlist)*len(prefix)*len(suffix)
    hash_num = len(hashes)
    t0 = time()
    print("wordlist length: {}".format(total),flush=True)
    print("hashes to crack: {}".format(hash_num),flush=True)

    q           = mp.JoinableQueue(total)
    q_done      = mp.JoinableQueue(total)
    q_recovered = mp.JoinableQueue(hash_num)

    words_per_producer = int(len(wordlist)/PRODUCERS)
    for x in range(PRODUCERS):
        words = []
        if len(wordlist) > words_per_producer*2:
            for y in range(words_per_producer):
                words.append(wordlist.pop(0))
        else:
            words = wordlist
            wordlist = []

        p = mp.Process(target=producer, name='Producer'+str(x),args=(q,words,))
        p.start()
        p_producers.append(p)

    for x in range(CONSUMERS):
        p = mp.Process(target=consumer, name='Consumer'+str(x),args=(q,q_done,))
        p.start()
        p_consumers.append(p)

    p = mp.Process(target=stats, name='stats')
    p.start()
    p_stats.append(p)
    p.join()

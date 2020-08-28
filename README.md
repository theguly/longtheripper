# Long the Ripper

## Introduction

Last week I had a quick chat with a friend about a known limit of both [John the Ripper](https://www.openwall.com/john/) and [hashcat[(https://hashcat.net/hashcat/).

This is a known issue so far: [mubix](https://room362.com/post/2017/05-06-2017-password-magic-numbers/) talked about it in mid 2017 and also [notsosecure](https://www.notsosecure.com/maximum-password-length-reached/) did some further reasearch.

I did not tested latest JtR, but doing some quick test with hashcat this looks like a non-issue nowdays because v5.1.0 can crack a password of ~60chars both using wordlist and rules.  
Given that I often need simple multiprocessing operation on my script and I that never really focused on this issue on python, I tought it was a good idea to spend some time with [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) [0] [1].  

I see you if you're like "WTF are you trying to crack such passwords?!", so let me try to show you a use case.

Based on my experience, it's not uncommon to find Service Account's password to be someway predictable.  
For example, the password is made out of a known prefix: service name or service username, server name where given service runs, and a variable suffix, for example:
`SVCMAIL-SRVEXCHANGE01-June2020`

If you are lucky enough to find some Service password saved in plaintext in some configuration files or whatever, and you are able to see a pattern, you could be able to bruteforce even such long passwords.

So, if prerequisites are respected, you will have a short list of prefix (service name or username, like SRVMAIL) and a short list of words (server name, like SRVEXCHANGE), and a long-as-you-like list of suffix.

This shouldn't give a huge wordlist and that's why LtR doesn't have a session support.

## The tool

[Long the Ripper](https://github.com/theguly/longtheripper/) mimics basic functionality of any wordlist generator: she takes a prefix, a suffix, a wordlist, generates a NTLM hash and matches against given hash list.

I tested LtR mainly on two boxes: a modern laptop with 8cores and a pretty dated server with 56cores.  

The script is made out of three main routines:
* a producer, who is in charge of feeding a queue that holds any computed word based on input
* a consumer, who of course consumes the queue by generating NTLM of computed word and try to match against given hashes
* a stats one, who prints out some statistics and checks if all hashes has been recovered or if there are no more word to compute

Observation on both boxes took me to hardcode the number of thread to 2+2 and to remove the --thread argument.  
Any other value will slow down the check rate. I'm of course open to hear your voice if you observe a different behaviour, anyway you can easily change the two constants on top of longtheripper.py script.


## Usage

Usage is pretty standard:
> usage: longtheripper.py [-h] [-S SUFFIX] [-s SUFFIX_FILE] [-P PREFIX] [-p PREFIX_FILE] [-N NTLM] [-n NTLM_FILE] [-W WORD] [-w WORD_FILE]
> 
> Long the Ripper.
> 
> optional arguments:
>   -h, --help            show this help message and exit
>   -S SUFFIX, --suffix SUFFIX
>                         suffix string
>   -s SUFFIX_FILE, --suffix_file SUFFIX_FILE
>                         file containing suffix
>   -P PREFIX, --prefix PREFIX
>                         prefix string
>   -p PREFIX_FILE, --prefix_file PREFIX_FILE
>                         file containing prefix
>   -N NTLM, --ntlm NTLM  single ntlm to crack
>   -n NTLM_FILE, --ntlm_file NTLM_FILE
>                         file containing list of ntlm to crack
>   -W WORD, --word WORD  single word to check
>   -w WORD_FILE, --wordlist WORD_FILE
>                         wordlist

You can input prefix, suffix, and wordlist both from file and as argument in command line.  
Multiple input using argument is not supported and I think will never be (PRs are welcome)

Of course also a list of NTLM hashes can be given as argument or in a file.  
The format can be both just a hash or a pair like username:hash, take files generated with (genhash.py)[genhash.py] as reference.

Any input is optional but wordlist and NTLM.


## genhash.py

Cloning github repo you can also find a a small script that I used to test Long the Ripper, genhash.py.

The script creates random wordlist, prefix, suffix, and calculate some hashes based on both valid and invalid word.  
I think it could be handy to have it for some quick test.

The script is very small and have some hardcoded configuration, edit as you need.

## Stats

On a i5 8thgen I had ~120kH/s. Very far from hashcat on a low-end GPU, but I'm fine with it.


## TODO

Every software can be improoved, and LtR make no expection.  
1. I think I won't work on this because, as I said, looks like hashcat can handle long password, but I think I'll try to support more encryptions if I see myself in the need (PR are welcome)
2. As already said, multiple input using argument is not supported and I think will never be (PRs are welcome)
3. There is no way to pause/resume a session. I don't think I'll need this soon, but I see some value here (PRs are welcome)
4. I see value also in supporting basic rules, but you could chain tools like [mentalist](https://github.com/sc0tfree/mentalist/) to achieve it by feeding with a proper wordlist (PRs are welcome)


[0]: OK, I started having a quarrel with Queue when talking with some [friends](https://github.com/alberanid) they gave me a good advice: use multiprocessing both for more performances and less headache.  
[1]: Yes I know, but I'm not going to learn Go soon.

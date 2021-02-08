#!/usr/bin/python3
####################################
####################################
# Contrary to what the name implies,
# this script does not use 'dd' but 
# simply reads and writes chunks of 
# binary data. Every 'CheckInterval'
# forks itself and runs a leveladj 
# type block and adjusts the gain. 
# the actual time interval will be 
# sample rate / BUFSIZE * CheckInterval
# this version of the script uses the 
# cx card 'level' paramter to adjust gain
# the cx card has a lot of inherent noise
# so i consider this to be only experimental
# the use of an external amp and gain 
# control will probably provide better 
# results, unless you have one of the 
# 1 in 100 cards that have low noise. 
######################################
######################################
### !!! NOTE !!! if using this script
### in conjonction with an external
### amplifier, you must set the external 
### amplifier gain so leveladj is 0 at
### the strongest portion of the disc



import time
import os
import sys
import datetime
def read_in_chunks(file_object):
    global BUFSIZE
    while True:
        data = file_object.read(BUFSIZE)
        if not data:
            break
        yield data
def child(data):
    syssyfsfile = open(r"/sys/module/cxadc/parameters/level","r")    
    GainLevel = int(syssyfsfile.read())
    syssyfsfile.close()
    NumSampOver = 0
    NumSampGood = 0
    OneOfBuff = 0
    HighestSamp = 0
    LowestSamp = 215 
    GainAction = "Maintaining Gain: "
    for OneOfBuff in data:
        #if NumSampOver < BUFSIZE / 50000:
        if NumSampOver < BUFSIZE / 200000:
            if OneOfBuff == 0 or OneOfBuff == 255:
                #clipped
                NumSampOver = 99999  # hard clip,
                break
            if OneOfBuff < 8 or OneOfBuff >248:
                NumSampOver += 1
            if OneOfBuff >= 225 or OneOfBuff <= 25:  #is this right?
                NumSampGood += 1
            if OneOfBuff > HighestSamp:
                HighestSamp = OneOfBuff
            if OneOfBuff < LowestSamp:
                LowestSamp = OneOfBuff
        else:
            NumSampOver = 99999
            break
    if NumSampOver == 99999:  
        GainLevel -= 2 
        if GainLevel < 0 :
            GainLevel = 0
        GainAction = "Lowering Gain: Coarse " + str(GainLevel) + " "
    elif NumSampOver >= 20:  
        GainLevel -= 1
        if GainLevel < 0 :
            GainLevel < 0
        GainAction = "Lowering Gain: Fine " + str(GainLevel) + " "
    elif NumSampGood == 0:
        GainLevel += 2
        if GainLevel > 31 :
            GainLevel = 31
        GainAction = "Raising Gain: Coarse "  + str(GainLevel) + " "
    elif NumSampGood <= 2000:
        GainLevel += 1
        if GainLevel > 31 : 
            GainLevel = 31 
        GainAction = "Raising Gain: Fine "  + str(GainLevel) + " "

    syssyfsfile = open(r"/sys/module/cxadc/parameters/level","w")    
    syssyfsfile.write(str(GainLevel))
    syssyfsfile.close()
    now = datetime.datetime.now()
    print (now,":",GainAction,"Low:",LowestSamp," High:",HighestSamp," Clipped:",NumSampOver,"                  ",end='\r')
    os._exit(0)
##########################################################################################################

name_in  = "/dev/cxadc0"
name_out = sys.argv[1]
CheckInterval = 150 #checking interval 125 = ~7sec@40msps
CountVar = 0
BUFSIZE   = 2097152

in_fh = open(name_in, "rb")
out_fh = open(name_out, "wb")
for piece in read_in_chunks(in_fh):
    out_fh.write(piece)
    CountVar +=1
    if CountVar > CheckInterval: 
        CountVar = 0
        newpid = os.fork()
        if newpid == 0:
            child(piece)
    
in_fh.close()
out_fh.close()
print ("Fin")

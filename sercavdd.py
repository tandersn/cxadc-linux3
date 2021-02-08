#!/usr/bin/python3
#requires pip install pyserial
import time
import serial
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
    global ser
    LengthOfAdjustment = .25
    LengthOfAdjustmentBIG = .5
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
        ser.setDTR(False)    
        time.sleep(LengthOfAdjustmentBIG)
        ser.setDTR(True)
        GainAction = "Lowering Gain: Coarse "
    elif NumSampOver >= 20:  
        ser.setDTR(False)    
        time.sleep(LengthOfAdjustment)
        ser.setDTR(True)
        GainAction = "Lowering Gain: Fine "
    elif NumSampGood == 0:
        ser.setRTS(False)
        time.sleep(LengthOfAdjustmentBIG)
        ser.setRTS(True)
        GainAction = "Raising Gain: Coarse "
    elif NumSampGood <= 2000:
        ser.setRTS(False)    
        time.sleep(LengthOfAdjustment)
        ser.setRTS(True)
        GainAction = "Raising Gain: Fine "
    now = datetime.datetime.now()
    print (now,":",GainAction,"Low:",LowestSamp," High:",HighestSamp," Clipped:",NumSampOver,"                  ",end='\r')
    os._exit(0)
##########################################################################################################

name_in  = "/dev/cxadc0"
#name_in  = "/laserdisc/development/pipe"
name_out = sys.argv[1]
CheckInterval = 150 #checking interval 125 = ~7sec@40msps
CountVar = 0
BUFSIZE   = 2097152
print ("initialize serial")  
ser = serial.Serial("/dev/ttyUSB0", 2400)
#ser.close
#ser.open() 
ser.setRTS(True)
ser.setDTR(True)

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
    
in_fh.close
out_fh.close
ser.close
print ("Fin")

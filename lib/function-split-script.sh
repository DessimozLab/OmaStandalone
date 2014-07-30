#!/bin/bash

# We have 245524 OMA groups to annotate, and 60 processors to do it on.
# Each processor can take 245524/60 = 4092 OMAs

for ((v=1; v<245524; v+=4092)) do
        
    echo "
    
    t := $v:
    lastGroup := $v + 4092 - 1:
    
    ReadProgram ('/home/skuncan/OMA-standalone/CODE/FunctionPrediction.drw'):
    done" | /home/darwin/v2/source/linux64/darwin -l /home/darwin/v2/source/lib/ &
    
done

#for ((v=1; v<=245524; v+=4092)) do
#    echo $v
#    num=`expr $v + 4092 - 1`
#    echo $num
#done
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#n_step_mult=1
#n_two_mult=1/2
#result=1
#n=1
#while(result>=0.001):
#    n_step_mult*=n
#    n_two_mult*=2
#    n+=1
#    result=n_two_mult/n_step_mult
#print(n)
#

import random

def getRandomInt():
    return random.randint(1,12)

run_times=10000
bingo=0
for r in range(run_times):
    first_num=getRandomInt()
    second_num=getRandomInt()
    if(first_num<second_num):
        bingo+=1
print(round(bingo/run_times,3))

        

import re
def check(a):
    n=[100,10**9,11235813213445,14*4**41]
    score=0.0
    for i in range(0,4):
        a[i]=a[i].split()
        if len(a[i])!=4:
            continue
        valid=1
        sum=0
        for j in a[i]:
            if not re.match('^[0-9]*$',j):
                valid=0
                break
            sum+=int(j)*int(j)
        if valid:
            score+=25//(abs(sum-n[i])+1)
    return score
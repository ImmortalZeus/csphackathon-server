def check(a):
    ans=["103","76","58","241"]
    res=0
    for i in range(0,4):
        if a[i]!=ans[i]:
            return 0
    return 100
def check(a):
    ans=["2","8","55","455898627","901606477","851155325"]
    score=[10,10,30,20,20,10]
    res=0
    for i in range(0,6):
        if a[i]==ans[i]:
            res+=score[i]
    return res
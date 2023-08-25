def check(a):
    res=0
    ans=["7","10","20","30"]
    for i in range(0,4):
        if a[i]==ans[i]:
            res+=25
    return res
def check(a):
    ans=["24","41150","332748115"]
    score=[30,30,40]
    res=0
    for i in range(0,3):
        if a[i]==ans[i]:
            res+=score[i]
    return res
def check(a):
    ans=["91.76","26.26","60.61","73.79","24.00","81.33","99.91"]
    score=[15,10,10,20,10,20,15]
    res=0
    for i in range(0,7):
        if a[i]==ans[i]:
            res+=score[i]
    return res
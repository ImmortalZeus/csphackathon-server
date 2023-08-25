def check(a):
    ans=["483722112","937299663","445504451","902124899","162044692"]
    res=0
    for i in range(0,5):
        if a[i]==ans[i]:
            res+=20
    return res
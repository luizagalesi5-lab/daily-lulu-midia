import numpy as np, cv2, sys
from numba import njit

@njit(cache=True)
def acha_seam(E):
    H,W=E.shape; M=E.copy(); B=np.zeros((H,W),np.int32)
    for i in range(1,H):
        for j in range(W):
            a=max(j-1,0); b=min(j+1,W-1); k=a; v=M[i-1,a]
            for t in range(a+1,b+1):
                if M[i-1,t]<v: v=M[i-1,t]; k=t
            M[i,j]+=v; B[i,j]=k
    s=np.zeros(H,np.int32); s[H-1]=np.argmin(M[H-1])
    for i in range(H-2,-1,-1): s[i]=B[i+1,s[i+1]]
    return s

def energia(img,prot):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
    e=np.abs(cv2.Sobel(g,cv2.CV_32F,1,0))+np.abs(cv2.Sobel(g,cv2.CV_32F,0,1))
    return e+prot

def insere(img,prot,n):
    # acha n seams numa cópia (removendo), depois duplica na original
    work=img.copy(); p=prot.copy(); H,W=img.shape[:2]
    idx=np.tile(np.arange(W),(H,1)); seams=[]
    for _ in range(n):
        s=acha_seam(energia(work,p))
        seams.append(idx[np.arange(H),s].copy())
        m=np.ones(work.shape[:2],bool); m[np.arange(H),s]=False
        work=work[m].reshape(H,-1,3); p=p[m].reshape(H,-1); idx=idx[m].reshape(H,-1)
    out=img; pr=prot
    cols=np.array(seams)  # n x H original coords
    for r in range(H): cols[:,r].sort()
    res=np.zeros((H,W+n,3),np.uint8); rp=np.zeros((H,W+n),np.float32)
    for r in range(H):
        c=cols[:,r]; row=img[r]; out_row=[]; prev=0
        parts=[];pp=[]
        for x in c:
            parts.append(row[prev:x+1]); pp.append(prot[r,prev:x+1])
            nx=min(x+1,W-1); parts.append(((row[x].astype(int)+row[nx])//2).astype(np.uint8)[None]); pp.append(prot[r,x:x+1]+1e5)
            prev=x+1
        parts.append(row[prev:]); pp.append(prot[r,prev:])
        res[r]=np.concatenate(parts); rp[r]=np.concatenate(pp)
    return res,rp

def alarga(img,alvo_w,pmask):
    prot=pmask.astype(np.float32)*1e6
    while img.shape[1]<alvo_w:
        n=min(alvo_w-img.shape[1], img.shape[1]//6)
        img,prot=insere(img,prot,n)
    return img

> 
# byte-exact extent of the JSON blob
def extent(center):
    s=center
    while s>0 and (32<=hb[s-1]<127 or hb[s-1] in (9,10,13)): s-=1
    e=center
    n=len(hb)
    while e<n and (32<=hb[e]<127 or hb[e] in (9,10,13)): e+=1
    return s,e
s,e = extent(0x09fff000)
print(f"JSON blob: heap+0x{s:08x}..0x{e:08x} = {(e-s)/1e6:.2f}MB")
print("HEAD:", hb[s:s+160].decode('utf-8','replace').replace("\n"," "))
print("TAIL:", hb[e-160:e].decode('utf-8','replace').replace("\n"," "))
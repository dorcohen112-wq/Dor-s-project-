import json, re, requests
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"he-IL,he;q=0.9"}
def show(o,p="",depth=0):
    if depth>5: return
    if isinstance(o,dict):
        for k,v in list(o.items())[:40]:
            if isinstance(v,dict): print(p+k,"{}"); show(v,p+"  ",depth+1)
            elif isinstance(v,list): print(p+k,f"[{len(v)}]"); (show(v[0],p+"  ",depth+1) if v and isinstance(v[0],dict) else None)
            else: print(p+k,"=",str(v)[:90])
for url in ["https://www.drushim.co.il/jobs/search/%D7%9E%D7%94%D7%A0%D7%93%D7%A1%20%D7%97%D7%95%D7%9E%D7%A8%D7%94/",
            "https://www.drushim.co.il/jobs/search/hardware/?ssaen=1"]:
    r=requests.get(url,headers=H,timeout=30); print("URL",url,r.status_code,len(r.text))
    m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',r.text,re.S)
    if not m: print("no NEXT_DATA; scripts:", re.findall(r'src="([^"]+)"',r.text)[:5]); print(r.text[:500]); continue
    d=json.loads(m.group(1)); show(d.get("props",{}).get("pageProps",{}))
    print("buildId", d.get("buildId"), "page", d.get("page"))

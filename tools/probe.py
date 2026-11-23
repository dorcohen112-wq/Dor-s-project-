import json, requests, sys
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept":"application/json, text/plain, */*","Referer":"https://www.drushim.co.il/"}
for url in ["https://www.drushim.co.il/api/jobs/search?searchterm=%D7%9E%D7%94%D7%A0%D7%93%D7%A1%20%D7%97%D7%95%D7%9E%D7%A8%D7%94&ssaen=3&page=0&isAA=true",
            "https://www.drushim.co.il/api/jobs/search?searchterm=hardware&page=0"]:
    try:
        r=requests.get(url,headers=H,timeout=30); print(url, r.status_code, r.headers.get("content-type"))
        t=r.text; print(t[:300].replace("\n"," "))
        try:
            d=r.json(); print("KEYS", list(d)[:20] if isinstance(d,dict) else type(d))
            lst = d.get("ResultList") if isinstance(d,dict) else d
            if lst:
                def show(o,p="",depth=0):
                    if depth>3: return
                    if isinstance(o,dict):
                        for k,v in o.items():
                            if isinstance(v,(dict,list)): print(p+k, type(v).__name__); show(v if isinstance(v,dict) else (v[0] if v else {}),p+"  ",depth+1)
                            else: print(p+k,"=",str(v)[:90])
                show(lst[0])
            print("OTHER", {k:(v if not isinstance(v,(list,dict)) else type(v).__name__) for k,v in d.items()} if isinstance(d,dict) else "")
        except Exception as e: print("not json", e)
    except Exception as e: print(url, "ERR", e)

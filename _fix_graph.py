import sys, urllib.request, json
sys.path.insert(0, ".")
from clients.supply_client import SupplyClient
c = SupplyClient()
for n in ['天齐锂业','华友钴业','当升科技','恩捷股份','天赐材料','宁德时代','比亚迪']:
    c.add_company(n)
for s,t,rt,yr,r in [('当升科技','宁德时代','客户',2024,30),('恩捷股份','宁德时代','客户',2024,16),('天赐材料','宁德时代','客户',2024,20),('华友钴业','宁德时代','客户',2024,7.2),('当升科技','比亚迪','客户',2024,15),('恩捷股份','比亚迪','客户',2024,10)]:
    c.push_relation(s,t,rt,yr,r)
# Verify
r = urllib.request.urlopen("http://localhost:8765/api/graph-view", timeout=5)
print(f"graph-view: {r.status} ({len(r.read())} bytes)")

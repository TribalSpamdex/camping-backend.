import osmium, json, sys, datetime
class Extract(osmium.SimpleHandler):
 def __init__(self): super().__init__(); self.rows={}
 def add(self, typ, id, tags, lat, lon):
  t=dict(tags); camping=t.get('tourism') in ('camp_site','caravan_site'); parking=t.get('amenity')=='parking' and (t.get('motorhome') in ('yes','designated') or t.get('overnight')=='yes');
  if not (camping or parking) or t.get('access') in ('private','no') or t.get('motor_vehicle')=='no' or t.get('overnight')=='no' or t.get('motorhome')=='no': return
  if not (49<=lat<=61 and -9<=lon<=3): return
  keys=['name','name:en','tourism','amenity','motorhome','overnight','camping:overnight','access','motor_vehicle','fee','charge','fee:amount','toilets','shower','showers','drinking_water','website','contact:website','maxheight','maxstay']
  self.rows[(typ,id)]={'type':typ,'id':id,'lat':round(lat,6),'lon':round(lon,6),'tags':{k:t[k] for k in keys if k in t}}
 def node(self,n):
  if n.location.valid(): self.add('node',n.id,n.tags,n.location.lat,n.location.lon)
 def area(self,a):
  try:
   import shapely.wkb
   p=shapely.wkb.loads(osmium.geom.WKBFactory().create_multipolygon(a),hex=True).representative_point(); self.add('way' if a.from_way() else 'relation',a.orig_id(),a.tags,p.y,p.x)
  except (RuntimeError,ValueError): pass
h=Extract(); h.apply_file(sys.argv[1],locations=True,idx='flex_mem'); rows=list(h.rows.values()); assert len(rows)>500, 'Unexpectedly small UK extract'; json.dump({'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elements':rows},open(sys.argv[2],'w'),separators=(',',':'))

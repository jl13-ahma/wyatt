#!/usr/bin/env python3
"""R4 native CAD, closed meshes, assembly/hardware/air/service-gauge QA."""
from pathlib import Path
from collections import Counter
import json,struct,hashlib
import cadquery as cq
R=Path(__file__).resolve().parent

def load(n):
 v=cq.importers.importStep(str(R/'STP'/(n+'.stp'))).vals();return v[0] if len(v)==1 else cq.Compound.makeCompound(v)
def box(w,h,d,x=0,y=0,z=0):return cq.Workplane('XY').box(w,h,d,centered=(True,True,False)).translate((x,y,z)).val()
def stats(v):
 b=v.BoundingBox();return {'valid':v.isValid(),'solids':len(v.Solids()),'volume_mm3':v.Volume(),'bbox_mm':[b.xlen,b.ylen,b.zlen]}
p=json.loads((R/'parameters.json').read_text());CX,CY=p['sensor_centre_xy'];D=32.8
data={'revision':'R4','step_files':{},'stl_files':{},'clearance_checks_mm3':{},'limitations':['Geometry only; actual sensor/connector/cone/foam/thermal/tip tests remain.']}
for path in sorted((R/'STP').glob('*.stp')):
 if 'PLANFORM_ONLY' in path.name:data['planform_reference']={'surface_only':True,'module_height_verified':False};continue
 v=load(path.stem);m=stats(v);assert m['valid'] and m['solids']>0 and m['volume_mm3']>0,path.name;data['step_files'][path.name]=m
names={'body':'01_Horizontal_Cabinet','left_cover':'02_Left_Wing_Rear_Cover','right_cover':'03_Right_Wing_Rear_Cover','retainer':'04_Official_Cassette_Retainer','plinth':'06_Low_Concealed_Desk_Plinth','cap':'07_Internal_Sensor_Service_Cap','carrier':'08_SEN0428_Internal_Edge_Carrier','retention':'09_SEN0428_Rear_Retention_Frame'}
parts={k:load(n) for k,n in names.items()}
s=R/'Official-originals';parts['official_top']=cq.importers.importStep(str(s/'ESP32-S31-Korvo-1_Case_top_20260603.STEP')).val().rotate((0,0,0),(0,1,0),180).translate((53.25,-42,1.3));parts['official_bottom']=cq.importers.importStep(str(s/'ESP32-S31-Korvo-1_Case_btm_20260603.STEP')).val().translate((53.25,-42,19.1))
g=load('05_Flush_Speaker_Grille_PRINT_TWO');parts['grille_L']=g.translate((-94,0,0));parts['grille_R']=g.translate((94,0,0));parts['leather']=load('REFERENCE_Cognac_TOP_SIDE_Wrap_NOT_FOR_PRINT')
def check(n,a,b):
 v=a.intersect(b).Volume();data['clearance_checks_mm3'][n]=v;assert v<.01,(n,v)
for an,a in parts.items():
 for bn,b in parts.items():
  if an<bn:check(an+'__'+bn,a,b)
# Head envelopes include maximum cover heads and flush countersunk prototypes.
heads={}
for x in (-113,-76,76,113):
 for y in (-49,49):heads[f'wing_{x}_{y}']=cq.Solid.makeCylinder(3,2.8,cq.Vector(x,y,35.2),cq.Vector(0,0,1))
for x in (-58.6,58.6):
 for y in (-50.5,50.5):heads[f'retainer_{x}_{y}']=cq.Solid.makeCylinder(3,2.8,cq.Vector(x,y,28.4),cq.Vector(0,0,1))
for x in (CX-16,CX+16):heads[f'cap_{x}']=cq.Solid.makeCone(1,2,1,cq.Vector(x,CY-6,33.9),cq.Vector(0,0,1))
for x in (CX-9.1,CX+9.1):heads[f'carrier_{x}']=cq.Solid.makeCylinder(2,1.6,cq.Vector(x,CY,9.6),cq.Vector(0,0,1))
for x in (-70,70):heads[f'plinth_{x}']=cq.Solid.makeCone(2.5,1.4,1.1,cq.Vector(x,-59.6,18),cq.Vector(0,1,0))
for hn,h in heads.items():
 for pn,v in parts.items():check('head_'+hn+'__'+pn,h,v)
for x in (-94,94):
 driver=cq.Solid.makeCylinder(21,20,cq.Vector(x,0,5),cq.Vector(0,0,1))
 for pn,v in parts.items():check(f'driver{x}__'+pn,driver,v)
harness=load('REFERENCE_Internal_Sensor_Harness_NOT_FOR_PRINT')
for pn,v in parts.items():check('harness__'+pn,harness,v)
# Cap gasket needs a fully backed land, including every ear and wire roof.
gasket=load('REFERENCE_Silicone_Gasket_NOT_FOR_PRINT');missing=gasket.translate((0,0,-.3)).cut(parts['body']).Volume();assert missing<.01,('cap_land',missing)
data['cap_gasket_unsupported_mm3']=missing
roof=box(2.8,5,1.4,CX+13.5,CY,31.4);missing=roof.cut(parts['body']).Volume();assert missing<.01,('feedthrough_roof',missing);data['wire_roof_missing_mm3']=missing
# The soft under-grille divider is supported and touches the solid band, notholes.
gg=load('REFERENCE_Grille_Foam_Frame_And_Divider_NOT_FOR_PRINT')
data['front_gasket_unsupported_mm3']={}
for x in (-94,94):
 missing=gg.translate((x,0,.3)).cut(parts['body']).Volume();data['front_gasket_unsupported_mm3'][str(x)]=missing;assert missing<.01,('front_gasket_body',x,missing)
 missing=gg.translate((0,0,-.3)).cut(g).Volume();assert missing<.01,('front_gasket_grille',missing)
# Discrete aligned holes prove ambient openings through grille and baffle.
for y in (-38.4,-35.2,-32,-28.8):
 for dx in (-6.4,0,6.4):
  air=cq.Solid.makeCylinder(.4,4.5,cq.Vector(CX+dx,y,-.2),cq.Vector(0,0,1))
  for pn in ('body','grille_L','leather'):check(f'sensor_air_{dx}_{y}__'+pn,air,parts[pn])
# Enclosed bottom duct and plinth tunnel form a connected forward-exiting path.
for an,air in {'bottom':box(9,11.4,4,CX,-52.3,8.5),'plinth_forward':box(15,1.7,18,CX,-57.4,-3.5)}.items():
 for pn in ('body','plinth','leather'):check('air_'+an+'__'+pn,air,parts[pn])
# Service gauges demonstrate open lanes, not a guarantee for an occupied plug.
for sign in (-1,1):
 side=box(12,80,31,sign*63.1,0,4)
 top=box(90,4.0,30,0,sign*51.6,4)
 for pn in ('body','retainer','left_cover','right_cover','official_top','official_bottom'):
  check('service_side'+str(sign)+'__'+pn,side,parts[pn]);check('service_topbottom'+str(sign)+'__'+pn,top,parts[pn])
# Continuous structural backing under the TOP leather band (not a void bridge).
toproof=box(216,2.0,32,0,55.2,.3);missing=toproof.cut(parts['body']).Volume();assert missing<.01,('toproof',missing);data['top_wrap_support_missing_mm3']=missing
for path in sorted((R/'STL').glob('*.stl')):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n;edges=Counter();vol=0;deg=0
 for i in range(n):
  q=struct.unpack_from('<12f',raw,84+i*50)[3:];vs=[q[k:k+3] for k in (0,3,6)];a,b,c=vs
  cross=((b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]),(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]),(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
  if sum(v*v for v in cross)<1e-18:deg+=1
  vol+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
  pts=[tuple(round(v,5) for v in vv) for vv in vs]
  for j,k in ((0,1),(1,2),(2,0)):edges[tuple(sorted((pts[j],pts[k])))]+=1
 closed=all(v==2 for v in edges.values());assert closed and deg==0 and vol>0,(path.name,closed,deg,vol)
 data['stl_files'][path.name]={'triangles':n,'closed_manifold':closed,'degenerate_triangles':deg,'signed_volume_mm3':vol}
geo=json.loads((R/'geometry-validation.json').read_text());data['printed_assembly_bbox_mm']=geo['printed_assembly_bbox_mm'];data['with_leather_reference_bbox_mm']=geo['with_leather_reference_bbox_mm'];data['clearance_check_count']=len(data['clearance_checks_mm3'])
custom=sum(v.Volume() for k,v in parts.items() if k not in ('official_top','official_bottom','leather'))
data['solid_volume_cm3']={'main_cabinet':parts['body'].Volume()/1000,'plinth':parts['plinth'].Volume()/1000,'custom_total':custom/1000,'meaning':'CAD100%solid volume, not filament usage, infill estimate or weighed mass.'}
(R/'package-validation.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'checks':data['clearance_check_count'],'step_solids':len(data['step_files']),'stls':len(data['stl_files']),'volume_cm3':data['solid_volume_cm3']}),flush=True)

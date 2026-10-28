#!/usr/bin/env python3
"""WYATT R4 single horizontal cabinet. CadQuery2.8, mm, CC BY-SA4.0.
Official Espressif inner-case source unchanged. Real sensor/port/speaker fit is
not inferred from images: only PCB14x17 and supplied driver42/20/17 are verified.
"""
from pathlib import Path
import json, math
import cadquery as cq
ROOT=Path(__file__).resolve().parent;STP=ROOT/'STP';STL=ROOT/'STL'
P={'revision':'R4','body_width':240.,'body_height':112.8,'body_front_to_back':35.2,'wing_outer_wall':3.,'speaker_ring_wall':3.,'sensor_cell_wall':2.5,
 'front_baffle':3.2,'speaker_seat_z':5.0,'body_rear_seal_plane':32.8,'rear_cover_thickness':2.4,
 'case_width':110.9,'case_height':97.8,'case_assembly_depth':23.6,'case_clearance_each_side':.45,
 'case_front_offset':1.3,'case_jacket_border':6.5,'case_retainer_z':26.,
 'speaker_centres_x':[-94.,94.],'speaker_bore_diameter':43.,'speaker_measured_rim':42.,
 'speaker_listing_depths':[20.,17.],'speaker_design_depth':20.,'speaker_front_aperture':36.,
 'grille_width':44.,'grille_height':86.,'grille_recess_width':44.4,'grille_recess_height':86.4,'grille_recess_depth':1.8,
 'sensor_centre_xy':[-94.,-37.],'sensor_cell_xy':[22.8,20.4],
 'sensor_pcb_verified_xy':[14.,17.],'sensor_stack_height_verified':False,
 'plinth_width':230.,'plinth_height':3.2,'plinth_depth':60.,'plinth_front_z':-3.,
 'leather_thickness':.7,'adhesive_thickness':.15,'pilot_diameter':2.2,'pilot_depth':8.,
 'usable_print_bed_min_width_with_5mm_brim':250.}
W,H,D=P['body_width'],P['body_height'],32.8;SX=[-94.,94.];CX,CY=-94.,-37.
IW,IH=111.8,98.7;JW,JH=124.8,111.7
RS=[(x,y) for x in (-58.6,58.6) for y in (-50.5,50.5)]
LCS=[(x,y) for x in (-113.,-76.) for y in (-49.,49.)]
RCS=[(x,y) for x in (76.,113.) for y in (-49.,49.)]
CAP_SCREWS=[(CX-16,CY-6),(CX+16,CY-6)]
CAP_Z=D+.3;CAP_T=1.8
report={'revision':'R4','units':'mm','parameters':P,'parts':{},'limitations':[
 'CAD-ready print prototype, not physically validated.',
 'PCB thickness/blank-edge contact/component/header envelope unverified; coupon first.',
 'Source case openings do not prove spare room beside occupied PCB/USB connectors.',
 'Installed temperature bias, acoustic response and tip stability require physical tests.']}
def box(w,h,d,x=0,y=0,z=0):return cq.Workplane('XY').box(w,h,d,centered=(True,True,False)).translate((x,y,z))
def rounded(w,h,d,r,x=0,y=0,z=0):return box(w,h,d).edges('|Z').fillet(r).translate((x,y,z))
def cyl(d,h,x=0,y=0,z=0):return cq.Workplane('XY').circle(d/2).extrude(h).translate((x,y,z))
def sh(v):return v.val() if isinstance(v,cq.Workplane) else v
def metrics(v):
 v=sh(v);b=v.BoundingBox();return {'valid':v.isValid(),'solids':len(v.Solids()),'volume_mm3':v.Volume(),'bbox_mm':[b.xlen,b.ylen,b.zlen]}
def save(n,v,pv=None):
 v=sh(v);assert v.isValid() and len(v.Solids())>0 and v.Volume()>0,n
 cq.exporters.export(v,str(STP/(n+'.stp')),exportType='STEP')
 pv=sh(pv) if pv is not None else v.translate((0,0,-v.BoundingBox().zmin))
 cq.exporters.export(pv,str(STL/(n+'.stl')),exportType='STL',tolerance=.05,angularTolerance=.12)
 check=cq.importers.importStep(str(STP/(n+'.stp'))).val();assert check.isValid(),n
 report['parts'][n]={'assembled':metrics(v),'print':metrics(pv),'reimport':metrics(check)}
 print(n,metrics(v)['bbox_mm'],flush=True);return v

def cap_outline(depth,z,clearance=0):
 s=rounded(26.8+2*clearance,23.2+2*clearance,depth,1.5,CX,CY,z)
 for x,y in CAP_SCREWS:s=s.union(cyl(6+2*clearance,depth,x,y,z))
 return s

# One continuous rounded block, not separate display and speaker boxes.
body=rounded(W,H,D,8)
body=body.cut(box(IW,IH,D+2,z=-1))
# Rear central relief lets the separate official-case retainer sit atZ26.
# Open top/bottom here avoids thin unprintable strips and keeps service access.
body=body.cut(box(JW+.4,H-5,D-26+.2,z=26))
# Hollow outer wings:3mm perimeter walls,3.2front baffle. Keep centralframe.
void=rounded(W-6,H-6,D-3.2+.2,5,z=3.2).cut(box(JW,H+2,D+2,z=3.1))
body=body.cut(void)
# Dedicated3mm ring walls support each driver instead of solid wing infill.
for x in SX:body=body.union(cyl(49,D-3.2,x,0,3.2))
for x in SX:
 body=body.cut(cyl(43,D-5+.2,x,0,5))
 body=body.cut(cyl(36,5.4,x,0,-.2))
 body=body.cut(rounded(44.4,86.4,2.0,4.2,x,0,-.2))
# Rear-open side service lanes reach the ACTUAL source case side walls. Cables
# enter from the rear; connector/bend fit is tested with the real plugged board.
for sign in (-1,1):
 body=body.cut(box(15.8,86,D-3.5+.2,x=sign*63.1,z=3.5)) # X55.2..71
 # Original top/bottom port windows remain open to rear, never buried by wings.
 body=body.cut(box(IW-20,4.55,D-3.5+.2,y=sign*51.625,z=3.5))
 # Speaker lead egress sits behind the20mm driver, into the service lane.
 body=body.cut(box(9,5,6,x=sign*74.5,y=14,z=27))
# Front corner stops bear only on the official shell, not the PCB.
for signx in (-1,1):
 for signy in (-1,1):
  stop=box(8,8,1.2,x=signx*(IW/2+2.5),y=signy*(IH/2+2.5))
  body=body.union(stop.intersect(rounded(W,H,1.2,8)))
for x,y in RS:body=body.cut(cyl(2.2,8.2,x,y,18))
# Cover bosses connect back into existing outer webs after pocket subtraction.
for x,y in LCS+RCS:
 body=body.union(cyl(7,D-3.2,x,y,3.2))
 body=body.union(box(3,6,D-3.2,x,y+(3 if y>0 else -3),3.2))
 body=body.cut(cyl(2.2,8.2,x,y,D-8))
# Integrated lower-left ambient cell, independent of both speaker/PCB airspace.
# Separate2.5mm cell walls and enclosed bottomduct survive the wing hollowing.
body=body.union(box(27.8,25.4,D-3.2,CX,CY,3.2))
for x,y in CAP_SCREWS:body=body.union(cyl(9,D-3.2,x,y,3.2))
body=body.union(box(6,10,8.1,CX+13.5,CY,24.7))
body=body.union(box(15,9.7,10,CX,-51.55,5.5))
body=body.union(box(2,6,D-3.2,CX-16,-51,3.2))
body=body.cut(box(22.8,20.4,D-3.2+.2,CX,CY,3.2))
frontslots=[-38.4,-35.2,-32.,-28.8]
for y in frontslots:body=body.cut(box(17.6,1.2,3.6,CX,y,-.2))
body=body.cut(box(10,10.4,5,CX,-52.2,8))
for dx in (-10,10):
 for dy in (-8.8,8.8):body=body.union(box(2,2,1.8,CX+dx,CY+dy,3.2))
# Closed5x4.2 feedthrough along X: intact1.4mm rear roof under the full gasket.
body=body.cut(box(4.2,5,4.2,CX+13.5,CY,27.2)) # Xcellright..+4.2
# Warm-side cable chase starts beyond the seal and heads into the open rear lane.
body=body.cut(box(17.0,5,5.8,CX+23.9,CY,27.2))
for x,y in CAP_SCREWS:body=body.cut(cyl(1.6,7.2,x,y,D-7.2))
# Hidden plinth screws enter from below at positions outside the cassette.
for x in (-70,70):
 body=body.union(cq.Solid.makeCylinder(4,8.5,cq.Vector(x,-H/2,18),cq.Vector(0,1,0)))
 hole=cq.Solid.makeCylinder(1.1,8.2,cq.Vector(x,-H/2-.1,18),cq.Vector(0,1,0))
 body=body.cut(hole)
body=save('01_Horizontal_Cabinet',body)

# Two flush rear wing plates; the centre and side service lanes stay accessible.
covers=[]
for sign,n,points in ((-1,'02_Left_Wing_Rear_Cover',LCS),(1,'03_Right_Wing_Rear_Cover',RCS)):
 plate=rounded(W-3.6,H-3.6,2.4,6.2,z=D).intersect(box(46.8,H+2,3,x=sign*94.8,z=D-.1))
 for x,y in points:plate=plate.cut(cyl(2.8,3,x,y,D-.2))
 if sign==-1:plate=plate.cut(cap_outline(3,D-.2,.2))
 # Speaker vents, contained entirely within each chamber's rear region.
 for dx in (-10,-5,0,5,10):plate=plate.cut(box(2.1,13,3,x=sign*94+dx,y=0,z=D-.2))
 covers.append(save(n,plate))
leftcover,rightcover=covers
retainer=rounded(JW,107.4,2.4,8,z=26).cut(box(IW-3,IH-3,3,z=25.8))
# Broad rear notches preserve actual side/top/bottom service access.
for sign in (-1,1):
 retainer=retainer.cut(box(12,86,3,x=sign*JW/2,z=25.8))
 retainer=retainer.cut(box(IW-20,8,3,y=sign*53,z=25.8))
for x,y in RS:retainer=retainer.cut(cyl(2.8,3,x,y,25.8))
retainer=save('04_Official_Cassette_Retainer',retainer)
# Flush perforated rectangular panels hide the round drivers and lower sensor.
# Matching rows above the left ambient slots keep those slots open through panel.
grille=rounded(44,86,1.5,4,z=0)
for ix in range(-6,7):
 for iy in range(-12,13):
  if iy!=-8:grille=grille.cut(cyl(2.1,2,ix*3.2,iy*3.2,-.1))
grille=save('05_Flush_Speaker_Grille_PRINT_TWO',grille)
# Soft contact frame/divider separates the shallow front grille gap.
frontgasket=rounded(44,86,.3,4,z=1.5).cut(rounded(40.8,82.8,.7,2.4,z=1.3))
frontgasket=frontgasket.union(box(40.8,2,.3,y=-25.6,z=1.5))
cq.exporters.export(frontgasket.val(),str(STP/'REFERENCE_Grille_Foam_Frame_And_Divider_NOT_FOR_PRINT.stp'),exportType='STEP')
# Low within-width plinth. Main body bears on it; no giant projecting stand.
foot=box(230,3.2,6,y=-58,z=-3)
for fx in (-80,80):foot=foot.union(box(50,3.2,60,x=fx,y=-58,z=-3))
foot=foot.edges('|Y').fillet(2.5)
foot=foot.cut(box(16,2.6,19,CX,-57.2,-4))
for x in (-70,70):
 foot=foot.cut(cq.Solid.makeCylinder(1.4,3.6,cq.Vector(x,-59.8,18),cq.Vector(0,1,0)))
 foot=foot.cut(cq.Solid.makeCone(2.75,1.4,1.35,cq.Vector(x,-59.6,18),cq.Vector(0,1,0)))
fp=foot.rotate((0,0,0),(1,0,0),90);fp=fp.translate((0,0,-fp.val().BoundingBox().zmin))
foot=save('06_Low_Concealed_Desk_Plinth',foot,fp)
# Sensor carrier/rearframe use only verified outline; nominal2.2thicknessslot.
carrier=box(22,20,1.2,CX,CY,5).cut(box(12.4,15.4,2,CX,CY,4.8))
carrier=carrier.union(box(22,20,2.2,CX,CY,6.2).cut(box(14.4,17.4,2.6,CX,CY,6)))
for dx in (-9.1,9.1):carrier=carrier.cut(cyl(1.6,3.6,CX+dx,CY,4.9))
carrier=save('08_SEN0428_Internal_Edge_Carrier',carrier)
clamp=box(22,20,1.2,CX,CY,8.4).cut(box(12.4,15.4,1.6,CX,CY,8.2))
for dx in (-9.1,9.1):clamp=clamp.cut(cyl(2.2,1.6,CX+dx,CY,8.2))
clamp=save('09_SEN0428_Rear_Retention_Frame',clamp)
cap=cap_outline(1.8,CAP_Z)
for dx in (-9.5,9.5):
 for dy in (-8.3,8.3):
  post=cq.Workplane('XY').workplane(offset=9.8).rect(2.2,2.2).workplane(offset=CAP_Z-9.8).rect(3.2,3.2).loft().translate((CX+dx,CY+dy,0))
  cap=cap.union(post)
for x,y in CAP_SCREWS:
 cap=cap.cut(cyl(2.2,2.2,x,y,CAP_Z-.2))
 cap=cap.cut(cq.Solid.makeCone(1.1,2.2,1.1,cq.Vector(x,y,CAP_Z+.7),cq.Vector(0,0,1)))
cp=cap.rotate((0,0,0),(1,0,0),180);cp=cp.translate((0,0,-cp.val().BoundingBox().zmin))
cap=save('07_Internal_Sensor_Service_Cap',cap,cp)

# Reproducible low-cost coupons precede the large240mm print.
frame=rounded(IW+8,IH+8,3,5).cut(box(IW,IH,4,z=-.2));save('TEST_01_Official_Case_Clearance_Frame',frame)
rings=[]
for i,d in enumerate((42.4,42.8,43.2)):
 ring=cyl(49,3,i*52).cut(cyl(d,4,i*52,z=-.2));rings.append(ring.val())
save('TEST_02_Speaker_Diameter_Rings_1_2_3',cq.Compound.makeCompound(rings))
seat=rounded(50,92,5,5).cut(cyl(36,6,z=-.2)).cut(rounded(44.4,86.4,2.0,4.2,z=-.2));save('TEST_03_Flush_Grille_And_Speaker_Seat',seat)
leathertest=box(55,30,4)
for i,d in enumerate((.75,.95,1.15)):leathertest=leathertest.cut(box(12,23,d,(i-1)*17,0,4-d))
for i,d in enumerate((2,2.2,2.4)):leathertest=leathertest.cut(cyl(d,5,(i-1)*17,-12,-.2))
save('TEST_04_Leather_And_Screw_Pilots',leathertest)
coupon=cq.Workplane(obj=body).intersect(box(42,39.4,33,CX,-36.7,-.1));save('TEST_05_Integrated_Sensor_Cell',coupon)
portcoupon=cq.Workplane(obj=body).intersect(box(154,H,D+.2,z=-.1));save('TEST_06_Cassette_Port_Lane_Coupon',portcoupon)
# Perimeter gasket and closed-channel split foam seal are stock references only.
gasket=cap_outline(.3,D).cut(box(22.8,20.4,1,CX,CY,D-.2))
for x,y in CAP_SCREWS:gasket=gasket.cut(cyl(2.2,1,x,y,D-.2))
cq.exporters.export(gasket.val(),str(STP/'REFERENCE_Silicone_Gasket_NOT_FOR_PRINT.stp'),exportType='STEP')
route=[(CX,CY,17),(CX+7,CY,29.3),(-67,CY,29.3)]
segments=[]
for a,b in zip(route,route[1:]):
 va,vb=cq.Vector(*a),cq.Vector(*b);delta=vb-va;segments.append(cq.Solid.makeCylinder(1.75,delta.Length,va,delta.normalized()))
for pt in route[1:-1]:segments.append(cq.Solid.makeSphere(1.75,cq.Vector(*pt)))
harness=cq.Compound.makeCompound(segments)
seal=box(2.8,5,4.2,CX+13.5,CY,27.2).cut(harness)
cq.exporters.export(seal.val(),str(STP/'REFERENCE_Split_Wire_Seal_NOT_FOR_PRINT.stp'),exportType='STEP')
cq.exporters.export(harness,str(STP/'REFERENCE_Internal_Sensor_Harness_NOT_FOR_PRINT.stp'),exportType='STEP')
pcb=cq.Face.makeFromWires(cq.Workplane('XY').rect(14,17).val()).translate((CX,CY,6.2))
cq.exporters.export(pcb,str(STP/'REFERENCE_SEN0428_PLANFORM_ONLY.stp'),exportType='STEP')
# One cognac wrap overTOP+SIDES, not two outlined stacked boxes. No bottom wrap
# over air inlet/plinth. It is materialreference, not printed volume.
LT=.85
leather=rounded(W+2*LT,H+2*LT,D,8+LT,z=0).cut(rounded(W,H,D+2,8,z=-1))
leather=leather.union(rounded(W,H,LT,8,z=-LT).cut(rounded(W-8,H-8,LT+2,4,z=-LT-1)))
leather=leather.cut(box(W+10,20,D+3,y=-60,z=-1))
cq.exporters.export(leather.val(),str(STP/'REFERENCE_Cognac_TOP_SIDE_Wrap_NOT_FOR_PRINT.stp'),exportType='STEP')
# Unchanged official part placements, now centred atY0.
src=ROOT/'Official-originals'
top=cq.importers.importStep(str(src/'ESP32-S31-Korvo-1_Case_top_20260603.STEP')).val().rotate((0,0,0),(0,1,0),180).translate((53.25,-42,1.3))
bottom=cq.importers.importStep(str(src/'ESP32-S31-Korvo-1_Case_btm_20260603.STEP')).val().translate((53.25,-42,19.1))
components={'cabinet':body,'left_rear':leftcover,'right_rear':rightcover,'cassette_retainer':retainer,'plinth':foot,
 'official_top':top,'official_bottom':bottom,'grille_L':grille.translate((-94,0,0)),'grille_R':grille.translate((94,0,0)),
 'sensor_cap':cap,'sensor_carrier':carrier,'sensor_retention':clamp,'leather_REFERENCE':leather.val()}
a=cq.Assembly(name='WYATT_R4_Horizontal_Print_Prototype')
for n,v in components.items():a.add(v,name=n,color=cq.Color(.53,.29,.15) if n=='leather_REFERENCE' else cq.Color(.16,.20,.21))
a.add(pcb,name='sensor_PLANFORM_ONLY',color=cq.Color(.18,.54,.43));a.add(harness,name='sensor_harness_REFERENCE',color=cq.Color(.8,.5,.12))
a.add(gasket.val(),name='soft_gasket_REFERENCE',color=cq.Color(.4,.45,.45))
a.export(str(STP/'00_Horizontal_Assembly_REFERENCE.stp'),exportType='STEP')
report['printed_assembly_bbox_mm']=metrics(cq.Compound.makeCompound([v for n,v in components.items() if n!='leather_REFERENCE']))['bbox_mm']
report['with_leather_reference_bbox_mm']=metrics(cq.Compound.makeCompound(list(components.values())))['bbox_mm']
report['sensor']={'centre_xy_mm':[CX,CY],'cell_xy_mm':[22.8,20.4],'seal_plane_z':D,'cap_front_rear_z':[CAP_Z,CAP_Z+1.8],
 'cap_screws_xy':CAP_SCREWS,'closed_feedthrough_bounds_mm':{'x':[CX+11.4,CX+15.6],'y':[CY-2.5,CY+2.5],'z':[27.2,31.4]},
 'closed_feedthrough_roof_z_mm':[31.4,32.8],'plug_centre_xy':[CX+13.5,CY],'plug_length_x_mm':2.8,
 'front_slot_centres_y':frontslots,'bottom_inlet_z_mm':[8,13],'plinth_tunnel_bounds_mm':{'x':[CX-8,CX+8],'y':[-58.5,-55.9],'z':[-4,15]},
 'plinth_tunnel_floor_mm':1.1,'PCB_height_and_blank_edges_verified':False,'foam_gasket_free_compressed_mm':[.5,.3]}
report['harness']={'diameter_allowance_mm':3.5,'points_mm':route,'endpoint':'Before officialcase in open rear service lane; actual occupied-port entry is a physical routing gate.'}
report['port_lanes']={'side_lane_x_abs_mm':[55.2,71],'side_lane_y_mm':[-43,43],'side_lane_z_mm':[3.5,35.2],
 'side_shell_to_lane_wall_mm':15.55,'lane_to_speaker_bore_min_web_mm':1.5,'top_bottom_access':'Open fromrear; original sourcecase cutouts unchanged; verify actual plugs/bends before fullprint.'}
report['collisions_mm3']={}
for an,av in components.items():
 for bn,bv in components.items():
  if an>=bn:continue
  v=av.intersect(bv).Volume();report['collisions_mm3'][an+'__'+bn]=v
  if v>.01:print('COLLISION',an,bn,v,flush=True)
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2)+'\n')
(ROOT/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('R4 BUILT',report['printed_assembly_bbox_mm'],flush=True)

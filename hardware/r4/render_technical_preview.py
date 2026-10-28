#!/usr/bin/env python3
"""Actual R4 CAD technical views, VTK/Pillow; no invented product photography."""
from pathlib import Path
import json
import argparse
import cadquery as cq
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--illustrative-ui',action='store_true',help='Add the legacy development UI illustration; no released firmware is implied.')
args=parser.parse_args()

def load(n):return cq.importers.importStep(str(R/'STP'/(n+'.stp'))).val()
def actor(s,color):
 vs,ts=s.tessellate(.12,.2);pts=vtk.vtkPoints()
 for v in vs:pts.InsertNextPoint(v.x,v.y,v.z)
 cells=vtk.vtkCellArray()
 for t in ts:
  cells.InsertNextCell(3)
  for i in t:cells.InsertCellPoint(i)
 pd=vtk.vtkPolyData();pd.SetPoints(pts);pd.SetPolys(cells)
 normals=vtk.vtkPolyDataNormals();normals.SetInputData(pd);normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.SplittingOff();normals.Update()
 m=vtk.vtkPolyDataMapper();m.SetInputConnection(normals.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m)
 p=a.GetProperty();p.SetColor(*color);p.SetAmbient(.42);p.SetDiffuse(.65);p.SetSpecular(.1);p.SetSpecularPower(18);return a
parts=[]
for n in ['01_Horizontal_Cabinet','02_Left_Wing_Rear_Cover','03_Right_Wing_Rear_Cover','04_Official_Cassette_Retainer','06_Low_Concealed_Desk_Plinth','07_Internal_Sensor_Service_Cap','08_SEN0428_Internal_Edge_Carrier','09_SEN0428_Rear_Retention_Frame']:
 parts.append((load(n),(.16,.20,.21)))
src=R/'Official-originals'
top=cq.importers.importStep(str(src/'ESP32-S31-Korvo-1_Case_top_20260603.STEP')).val().rotate((0,0,0),(0,1,0),180).translate((53.25,-42,1.3))
bottom=cq.importers.importStep(str(src/'ESP32-S31-Korvo-1_Case_btm_20260603.STEP')).val().translate((53.25,-42,19.1))
parts.extend(((top,(.21,.24,.25)),(bottom,(.21,.24,.25)),(load('REFERENCE_Cognac_TOP_SIDE_Wrap_NOT_FOR_PRINT'),(.54,.29,.14))))
grille=load('05_Flush_Speaker_Grille_PRINT_TWO')
for x in (-94,94):parts.append((grille.translate((x,0,0)),(.07,.09,.10)))
# Locate the actual opening; a neutral landscape orientation surface only.
opens=[]
for face in top.Faces():
 b=face.BoundingBox()
 if b.zlen<1e-5 and abs(b.zmin-1.3)<1e-5:
  for w in face.Wires():
   q=w.BoundingBox()
   if 80<q.xlen<107 and 45<q.ylen<85:opens.append((q.xlen,q.ylen,(q.xmin+q.xmax)/2,(q.ymin+q.ymax)/2))
opening=min(opens,key=lambda v:v[0]*v[1]) if opens else None
cx,cy=opening[2:] if opening else (0,8)
glass=cq.Workplane('XY').box(93.6,56.16,.3,centered=(True,True,False)).translate((cx,cy,1.8)).val();parts.append((glass,(.28,.37,.40)))
(R/'Preview/display-orientation.json').write_text(json.dumps({'revision':'R4','actual_opening_bbox':opening,'glass_mm':[93.6,56.16,.3],'status':'Orientation surface only, excluded from manufacturing files; no measured LCD fit claim.'},indent=2))
ren=vtk.vtkRenderer();ren.SetBackground(.933,.918,.886)
for s,c in parts:ren.AddActor(actor(s,c))
# Optional historical UI art; neutral display is the public default.
if args.illustrative_ui:
 reader=vtk.vtkPNGReader();reader.SetFileName(str(R/'Preview/Horizon-UI-illustrative.png'));reader.Update()
 texture=vtk.vtkTexture();texture.SetInputConnection(reader.GetOutputPort());texture.InterpolateOn()
 plane=vtk.vtkPlaneSource();plane.SetOrigin(cx+46.8,cy-28.08,1.7);plane.SetPoint1(cx-46.8,cy-28.08,1.7);plane.SetPoint2(cx+46.8,cy+28.08,1.7)
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(plane.GetOutputPort());ui=vtk.vtkActor();ui.SetMapper(mapper);ui.SetTexture(texture);ui.GetProperty().LightingOff();ren.AddActor(ui)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1000,600);win.SetMultiSamples(4);win.AddRenderer(ren)
cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetParallelScale(87);cam.SetFocalPoint(0,-1,18);cam.SetViewUp(0,1,0)
def capture(pos):
 cam.SetPosition(*pos);ren.ResetCameraClippingRange();win.Render();c=vtk.vtkWindowToImageFilter();c.SetInput(win);c.ReadFrontBufferOff();c.Update();d=c.GetOutput();w,h,_=d.GetDimensions();a=vtk_to_numpy(d.GetPointData().GetScalars()).reshape(h,w,-1);return Image.fromarray(np.flipud(a)[:,:,:3]).copy()
views=[]
for title,pos in [('FRONT / one continuous horizontal block',(0,-1,-500)),('THREE-QUARTER / flush side panels',(360,150,-500)),('REAR / open cassette service lanes',(0,-1,500)),('SIDE / low concealed rear plinth',(500,-1,18))]:views.append((title,capture(pos)))
fontpath=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
def font(n):return ImageFont.truetype(str(fontpath),n) if fontpath.exists() else ImageFont.load_default()
def sheet_for(items,rows,path,title):
 canvas=Image.new('RGB',(2000,160+rows*650),(238,234,226));d=ImageDraw.Draw(canvas)
 d.text((45,20),title,font=font(32),fill=(28,39,40));d.text((45,67),'240 x 112.8 x 35.2 mm main block / actual CAD / untested print prototype',font=font(24),fill=(54,65,65))
 d.text((45,105),'Original camera, microphones, buttons and case openings retained. Neutral display is orientation art; no physical fit/performance proof.',font=font(22),fill=(54,65,65))
 for i,(label,img) in enumerate(items):
  x=(i%2)*1000;y=160+(i//2)*650;canvas.paste(img,(x,y+35));d.text((x+30,y),label,font=font(25),fill=(34,47,47))
 canvas.save(path)
sheet_for(views[:2],1,R/'Preview/Shannon-horizontal-front-three-quarter.png','WYATT / R4 / HORIZONTAL DESIGN')
print('EARLY FRONT + THREE-QUARTER READY',flush=True)
sheet_for(views,2,R/'Preview/Shannon-technical-four-views.png','WYATT / R4 / TECHNICAL FOUR VIEWS')
# Exact current complete BRep drawings, including inset grilles and rear cap.
compound=cq.Compound.makeCompound([s for s,_ in parts])
for n,vec in [('front',(0,0,-1)),('rear',(0,0,1)),('top',(0,1,0)),('side',(-1,0,0)),('isometric',(-1,-.45,-1))]:
 cq.exporters.export(compound,str(R/'Preview'/(n+'.svg')),opt={'projectionDir':vec,'width':1200,'height':700,'showHidden':False,'strokeWidth':.5})
# Actual lower-left sensor cell, preview-only cropped cabinet and displacedcap.
ren.RemoveAllViewProps()
body=load('01_Horizontal_Cabinet').intersect(cq.Workplane('XY').box(48,37,37,centered=(True,True,False)).translate((-94,-37,-1)).val())
cap=load('07_Internal_Sensor_Service_Cap').translate((47,0,4));gasket=load('REFERENCE_Silicone_Gasket_NOT_FOR_PRINT').translate((39,0,1))
for s,c in [(body,(.23,.29,.30)),(cap,(.22,.27,.28)),(gasket,(.52,.58,.57)),(load('08_SEN0428_Internal_Edge_Carrier'),(.38,.43,.42)),(load('09_SEN0428_Rear_Retention_Frame'),(.38,.43,.42)),(load('REFERENCE_SEN0428_PLANFORM_ONLY'),(.18,.54,.43)),(load('REFERENCE_Internal_Sensor_Harness_NOT_FOR_PRINT'),(.68,.43,.12))]:ren.AddActor(actor(s,c))
win.SetSize(1500,900);cam.SetFocalPoint(-73,-34,17);cam.SetParallelScale(43);cam.SetPosition(10,45,195);ren.ResetCameraClippingRange();img=capture((10,45,195))
canvas=Image.new('RGB',(1500,1050),(238,234,226));canvas.paste(img,(0,150));d=ImageDraw.Draw(canvas)
d.text((35,20),'R4 / INTEGRATED LOWER-LEFT SENSOR CELL',font=font(28),fill=(28,39,40))
d.text((35,65),'Preview cutaway. Green: verified14 x17 mm PCB outline only; module stack height unverified.',font=font(22),fill=(54,65,65))
d.text((35,104),'Rear-only service cap / supported foam gasket / closed wire seal / hidden internal lead.',font=font(22),fill=(54,65,65))
canvas.save(R/'Preview/Shannon-integrated-sensor-open.png');win.Finalize();print('R4 ALL PREVIEWS READY',flush=True)

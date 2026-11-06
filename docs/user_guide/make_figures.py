"""Regenerates the user-guide figures from the game's own art and data/*.json.
Usage: python3 docs/user_guide/make_figures.py   (needs Pillow and the Inter font, falls back to DejaVu)"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
R = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")); OUT = os.path.join(R, "docs/user_guide/images"); os.makedirs(OUT, exist_ok=True)
F = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
def font(w, s):
    try: return ImageFont.truetype(F % w, s)
    except Exception: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
BG=(10,12,32); PANEL=(22,26,58); CYAN=(80,230,255); GOLD=(255,200,71); TXT=(225,235,255); DIM=(150,165,200)
def img(p): return Image.open(os.path.join(R, p.replace("res://",""))).convert("RGBA")
def up(im, k): return im.resize((im.width*k, im.height*k), Image.NEAREST)
def hexc(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def title(d, W, t, sub=None):
    d.text((W//2, 34), t, font=font("Bold", 34), fill=CYAN, anchor="mm")
    if sub: d.text((W//2, 66), sub, font=font("Regular", 16), fill=DIM, anchor="mm")
def load(p): return json.load(open(os.path.join(R,p)))["entries"]

# 1. Crew roster
crew = sorted(load("data/characters/crew.json"), key=lambda c:c["order"])
cw, ch = 240, 380; W = cw*5+40; H = 100+ch*2+20
c = Image.new("RGB",(W,H),BG); d = ImageDraw.Draw(c); title(d,W,"CHOOSE YOUR PIRATE","10 playable crew members")
for i,m in enumerate(crew):
    x = 20+(i%5)*cw; y = 95+(i//5)*ch; col = hexc(m["color"])
    d.rounded_rectangle([x+8,y,x+cw-8,y+ch-14],12,fill=PANEL,outline=col,width=3)
    p = up(img(m["sprite"]["portrait"]),2); c.paste(p,(x+cw//2-p.width//2,y+12),p)
    d.text((x+cw//2,y+268),m["name"],font=font("Bold",19),fill=TXT,anchor="mm")
    d.text((x+cw//2,y+292),m["title"].upper(),font=font("SemiBold",14),fill=col,anchor="mm")
    d.text((x+cw//2,y+313),m["role"],font=font("Regular",14),fill=DIM,anchor="mm")
    s=m["base_stats"]; d.text((x+cw//2,y+340),f"HP {s['hp']}  ATK {s['attack']}  SPD {s['speed']}",font=font("Medium",13),fill=GOLD,anchor="mm")
c.save(os.path.join(OUT,"crew_roster.png"))

# 2. Touch controls mock-up (1280x720 = 640x360 x2)
c = up(img("assets/islands/backgrounds/foosha_village_640x360.png"),2).convert("RGBA")
ov = Image.new("RGBA",c.size,(0,0,20,90)); c = Image.alpha_composite(c,ov); d = ImageDraw.Draw(c)
def put(p,xy,k=1,a=1.0):
    im = up(img(p),k)
    if a<1: im.putalpha(im.getchannel("A").point(lambda v:int(v*a)))
    c.alpha_composite(im,xy); return im.size
put("assets/ui/hud/player_hud_bars.png",(24,20),2)
hero = img("assets/characters/sheets/captain_sunhat_8x8.png").crop((0,0,32,40)); c.alpha_composite(up(hero,4),(560,420))
grunt = img("assets/enemies/marine_grunt_6x4.png").crop((0,0,32,40)).transpose(Image.FLIP_LEFT_RIGHT); c.alpha_composite(up(grunt,4),(800,420))
put("assets/ui/hud/virtual_joystick.png",(60,470),2,0.9)
btns = {"touch_attack":(1080,560),"touch_jump":(1160,460),"touch_dodge":(980,620),"touch_special":(1060,400),"touch_interact":(960,500)}
for n,(x,y) in btns.items(): put(f"assets/ui/touch/{n}.png",(x-72,y-72),2)
def label(x,y,t,tx,ty):
    d.line([(x,y),(tx,ty)],fill=GOLD,width=3); f=font("Bold",20)
    bb=d.textbbox((tx,ty),t,font=f,anchor="mm"); d.rounded_rectangle([bb[0]-10,bb[1]-6,bb[2]+10,bb[3]+6],8,fill=(10,12,32,230),outline=GOLD,width=2)
    d.text((tx,ty),t,font=f,fill=TXT,anchor="mm")
label(330,60,"HP / Energy bars",470,170)
label(188,598,"Move (virtual joystick)",240,430)
label(1080,560,"Attack",1210,690)
label(1160,460,"Jump",1225,340)
label(1060,400,"Special / Skill",1010,290)
label(960,500,"Interact",790,330)
label(980,620,"Dodge",820,690)
label(640,480,"You",640,380)
c.convert("RGB").save(os.path.join(OUT,"touch_controls.png"))

# 3. World map
seas = sorted(load("data/islands/seas.json"),key=lambda s:s["order"]); isl = sorted(load("data/islands/islands.json"),key=lambda s:s["order"])
cw=420; W=cw*3+40; H=880; c=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(c); title(d,W,"THE THREE SEAS","Sail from calm waters to the neon-lit New Frontier")
cols=[(80,230,255),(179,136,255),(255,59,92)]
for i,s in enumerate(seas):
    x=20+i*cw; y=90; col=cols[i]
    d.rounded_rectangle([x+8,y,x+cw-8,H-20],12,fill=PANEL,outline=col,width=3)
    mine=[a for a in isl if a["sea"]==s["id"]]
    bg=img(mine[-1]["background"]).resize((cw-40,(cw-40)*9//16),Image.NEAREST); c.paste(bg,(x+20,y+14))
    d.text((x+cw//2,y+250),f"{i+1}. {s['name']}",font=font("Bold",24),fill=col,anchor="mm")
    d.text((x+cw//2,y+278),"Danger "+"★"*s["danger"]+"☆"*(3-s["danger"]),font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",16),fill=GOLD,anchor="mm")
    for j,a in enumerate(mine):
        yy=y+310+j*44
        d.text((x+30,yy),a["name"],font=font("SemiBold",17),fill=TXT)
        d.text((x+cw-30,yy),f"Lv {a['level']}",font=font("Medium",16),fill=DIM,anchor="ra")
c.save(os.path.join(OUT,"world_map.png"))

# 4. Enemies
en = sorted(load("data/enemies/enemies.json"),key=lambda e:e["order"]); cw=250; W=cw*len(en)+40; H=440
c=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(c); title(d,W,"ENEMIES YOU WILL FACE")
tc={"minion":DIM,"elite":(179,136,255),"boss":(255,59,92)}
for i,e in enumerate(en):
    x=20+i*cw; y=90; col=tc[e["tier"]]
    d.rounded_rectangle([x+8,y,x+cw-8,H-20],12,fill=PANEL,outline=col,width=3)
    sh=img(e["sprite"]["sheet"]); fw=sh.width//6; fh=sh.height//4; fr=sh.crop((0,0,fw,fh)); k=4 if fw<=32 else 3
    fr=up(fr,k); c.paste(fr,(x+cw//2-fr.width//2,y+200-fr.height),fr)
    d.text((x+cw//2,y+225),e["name"],font=font("Bold",20),fill=TXT,anchor="mm")
    d.text((x+cw//2,y+250),e["tier"].upper(),font=font("SemiBold",14),fill=col,anchor="mm")
    s=e["base_stats"]; d.text((x+cw//2,y+278),f"HP {s['hp']}   ATK {s['attack']}",font=font("Medium",15),fill=GOLD,anchor="mm")
    d.text((x+cw//2,y+300),f"+{e['exp']} EXP   +{e['gold']} gold",font=font("Medium",15),fill=DIM,anchor="mm")
c.save(os.path.join(OUT,"enemies.png"))

# 5. Items
items=[i for i in load("data/items/starter_items.json") if i.get("icon")]
rc={"common":DIM,"uncommon":(77,255,154),"rare":(41,216,255),"epic":(179,136,255),"legendary":GOLD}
cw=260; per=4; rows=(len(items)+per-1)//per; W=cw*per+40; H=90+rows*190+10
c=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(c); title(d,W,"ITEMS & GEAR","Rarity: common · uncommon · rare · epic · legendary")
for i,it in enumerate(items):
    x=20+(i%per)*cw; y=90+(i//per)*190; col=rc[it["rarity"]]
    d.rounded_rectangle([x+8,y,x+cw-8,y+176],12,fill=PANEL,outline=col,width=3)
    ic=up(img(it["icon"]),2); c.paste(ic,(x+cw//2-48,y+10),ic)
    d.text((x+cw//2,y+122),it["name"],font=font("Bold",17),fill=TXT,anchor="mm")
    eff=it.get("effect") or it.get("stats") or {}
    s=", ".join(f"{k.replace('heal_','+').replace('_',' ')} {int(v*100) if v<1 else v}{'%' if v<1 else ''}" for k,v in eff.items()) or it["category"]
    d.text((x+cw//2,y+146),f"{it['rarity'].capitalize()} · {s}",font=font("Medium",13),fill=col,anchor="mm")
c.save(os.path.join(OUT,"items.png"))
print("ok", os.listdir(OUT))

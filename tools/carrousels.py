"""Génère les carrousels Prepaide (Instagram 1080x1350 PNG, TikTok 1080x1920 JPEG) au gabarit de la campagne.
Usage : python3 tools/carrousels.py <deck> [<deck>...]   (sans argument : tous)"""
import sys, os, html
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path('/home/claude/motion/node_modules/@fontsource/hanken-grotesk/files')
OUT = ROOT / 'campagne-lancement'

MASCOT = '''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><defs>
<radialGradient id="bgN4" cx="0.5" cy="0.38" r="0.78"><stop offset="0" stop-color="#5E37B0"/><stop offset="0.6" stop-color="#3A1E82"/><stop offset="1" stop-color="#22104F"/></radialGradient>
<radialGradient id="haloN4" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#B49BFF" stop-opacity="0.35"/><stop offset="1" stop-color="#B49BFF" stop-opacity="0"/></radialGradient>
<linearGradient id="backN4" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8CF5C4"/><stop offset="0.5" stop-color="#22C27E"/><stop offset="1" stop-color="#0C8A57"/></linearGradient>
<linearGradient id="frontN4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#F1EDFB"/></linearGradient>
<linearGradient id="eyeN4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26324F"/><stop offset="1" stop-color="#0B1022"/></linearGradient>
<radialGradient id="glossN4" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.6"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
<clipPath id="cardN4"><rect x="190" y="330" width="600" height="520" rx="110"/></clipPath></defs>
{BG}
<g transform="rotate(12 540 480)"><rect x="250" y="230" width="580" height="500" rx="110" fill="url(#backN4)"/>
<ellipse cx="420" cy="290" rx="150" ry="36" fill="url(#glossN4)"/><rect x="400" y="200" width="24" height="64" rx="12" fill="#0B1022"/><rect x="660" y="200" width="24" height="64" rx="12" fill="#0B1022"/></g>
<g transform="rotate(-7 490 560)"><rect x="190" y="330" width="600" height="520" rx="110" fill="#0A0420" opacity="0.3" transform="translate(0 24)"/>
<rect x="190" y="330" width="600" height="520" rx="110" fill="url(#frontN4)"/><g clip-path="url(#cardN4)">
<path d="M190 420 H790 M190 480 H790 M190 540 H790 M190 600 H790 M190 660 H790 M190 720 H790 M190 780 H790" stroke="#E6E0F6" stroke-width="5"/>
<path d="M290 330 V850" stroke="#E25A4E" stroke-width="7" opacity="0.7"/></g>
<rect x="196" y="336" width="588" height="508" rx="104" fill="none" stroke="#FFFFFF" stroke-width="8"/>
<rect x="360" y="470" width="86" height="210" rx="43" fill="url(#eyeN4)"/><rect x="534" y="470" width="86" height="210" rx="43" fill="url(#eyeN4)"/>
<rect x="378" y="492" width="26" height="62" rx="13" fill="#FFFFFF" opacity="0.85"/><rect x="552" y="492" width="26" height="62" rx="13" fill="#FFFFFF" opacity="0.85"/>
<path d="M454 708 Q490 764 526 708 Z" fill="#16203A" stroke="#16203A" stroke-width="10" stroke-linejoin="round"/>
<path d="M472 730 Q490 750 508 730 Q490 720 472 730 Z" fill="#FF8FA3"/>
<ellipse cx="300" cy="724" rx="48" ry="24" fill="#E25A4E" opacity="0.3"/><ellipse cx="680" cy="724" rx="48" ry="24" fill="#E25A4E" opacity="0.3"/></g></svg>'''
ICON = MASCOT.replace('{BG}', '<rect width="1024" height="1024" rx="230" fill="url(#bgN4)"/><circle cx="512" cy="540" r="440" fill="url(#haloN4)"/>')
SYMBOL = MASCOT.replace('{BG}', '').replace('viewBox="0 0 1024 1024"', 'viewBox="160 170 720 720"')
LOCK = '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><rect x="4.5" y="10.5" width="15" height="10" rx="2.5" fill="currentColor" stroke="none"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/></svg>'

CSS = '''
@font-face{font-family:H;font-weight:400;src:url(FONTS/hanken-grotesk-latin-400-normal.woff2)}
@font-face{font-family:H;font-weight:500;src:url(FONTS/hanken-grotesk-latin-500-normal.woff2)}
@font-face{font-family:H;font-weight:600;src:url(FONTS/hanken-grotesk-latin-600-normal.woff2)}
@font-face{font-family:H;font-weight:700;src:url(FONTS/hanken-grotesk-latin-700-normal.woff2)}
@font-face{font-family:H;font-weight:800;src:url(FONTS/hanken-grotesk-latin-800-normal.woff2)}
*{box-sizing:border-box;margin:0}
body{width:1080px;height:var(--h);font-family:H,sans-serif;color:#16203A;-webkit-font-smoothing:antialiased}
.s{position:relative;width:1080px;height:var(--h);overflow:hidden;padding:0 80px}
.light{background:#F7F6FC}
.dark{background:radial-gradient(ellipse 90% 70% at 50% 45%,#6A40C4 0%,#3A1E82 55%,#22104F 100%);color:#fff}
.hd{position:absolute;left:80px;right:80px;top:var(--hdT);display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:16px;font-weight:800;font-size:34px;letter-spacing:-1.4px}
.brand svg{width:58px;height:58px}
.pg{font-weight:600;font-size:24px;color:#5C6580}.dark .pg{color:#B49BFF}
.body{position:absolute;left:80px;right:80px;top:var(--bT)}
.ov{font-weight:800;font-size:24px;letter-spacing:4.5px;text-transform:uppercase;color:#5E37B0;margin-bottom:26px}.dark .ov{color:#B49BFF}
h1{font-weight:800;font-size:88px;line-height:1.02;letter-spacing:-3.8px;text-wrap:balance}
h1.m{font-size:76px;letter-spacing:-3.2px}
h1 em{font-style:normal;color:#22C27E}.light h1 em{color:#5E37B0}
.sub{margin-top:30px;font-size:31px;line-height:1.42;color:#46506B;max-width:860px}.dark .sub{color:rgba(255,255,255,.88)}
.sub b{font-weight:800}
.cards{display:flex;flex-direction:column;gap:26px;margin-top:var(--cT)}
.card{display:flex;gap:26px;align-items:flex-start;background:#fff;border:2px solid #E6E0F6;border-radius:30px;padding:34px 36px;box-shadow:0 10px 26px rgba(34,16,79,.06)}
.dark .card{background:rgba(255,255,255,.08);border-color:rgba(180,155,255,.28);box-shadow:none}
.num{flex:none;width:64px;height:64px;border-radius:16px;background:#3A1E82;color:#fff;font-weight:800;font-size:30px;display:flex;align-items:center;justify-content:center}
.dark .num{background:#22C27E;color:#16203A}
.ct{font-weight:800;font-size:37px;letter-spacing:-1px;line-height:1.15}
.cd{margin-top:8px;font-size:28px;line-height:1.42;color:#46506B}.dark .cd{color:rgba(255,255,255,.82)}
.tag{display:inline-block;font-weight:800;font-size:24px;letter-spacing:2px;padding:8px 16px;border-radius:12px;margin-bottom:14px}
.t-vrai{background:#E3FAEE;color:#0C8A57}.t-faux{background:#FFE9E6;color:#B34236}
.dark .t-vrai{background:#22C27E;color:#16203A}
.quote{font-weight:800;font-size:64px;line-height:1.08;letter-spacing:-2.6px;text-wrap:balance}
.mascot{position:absolute;filter:drop-shadow(0 34px 40px rgba(10,4,32,.45))}
.light .mascot{filter:drop-shadow(0 24px 30px rgba(34,16,79,.22))}
.dots{position:absolute;right:80px;top:var(--dT);display:flex;gap:10px;align-items:center}
.dots i{display:block;width:14px;height:14px;border-radius:7px;background:#C9BDF0}.dots i.on{width:38px;background:#3A1E82}
.dark .dots i{background:rgba(255,255,255,.35)}.dark .dots i.on{background:#fff}
.swipe{position:absolute;left:80px;top:var(--dT);transform:translateY(-14px);display:flex;align-items:center;gap:16px;font-weight:800;font-size:24px}
.swipe span{width:42px;height:42px;border-radius:21px;background:#22C27E;color:#16203A;display:flex;align-items:center;justify-content:center;font-size:24px}
.center{text-align:center;display:flex;flex-direction:column;align-items:center}
.btn{display:inline-block;margin-top:44px;background:#22C27E;color:#16203A;font-weight:800;font-size:32px;padding:26px 46px;border-radius:20px;box-shadow:0 14px 30px rgba(12,138,87,.35)}
.mock{margin-top:var(--cT);background:#fff;border:2px solid #E6E0F6;border-radius:32px;padding:34px;box-shadow:0 14px 30px rgba(34,16,79,.08)}
.chips{display:flex;flex-wrap:wrap;gap:16px;margin-top:var(--cT)}
.chip{background:#fff;border:2px solid #E6E0F6;border-radius:999px;padding:18px 28px;font-weight:700;font-size:30px}
.dark .chip{background:rgba(255,255,255,.1);border-color:rgba(180,155,255,.3)}
.ex{position:absolute;right:30px;bottom:20px;font-size:20px;font-weight:700;color:#7A839C;letter-spacing:1px}
'''.replace('FONTS', FONTS.as_uri())

def esc(s): return s  # les textes sont écrits à la main, balises <em>/<b> autorisées

def page(kind, i, n, fmt, inner, mascot=None):
    tall = fmt == 'tiktok'
    v = dict(h=1920 if tall else 1350, hdT=95 if tall else 70, bT=245 if tall else 170, dT=1490 if tall else 1232, cT='110px' if tall else '90px')
    style = ';'.join(f'--{k}:{x}px' if isinstance(x, int) else f'--{k}:{x}' for k, x in v.items())
    dots = ''.join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(1, n + 1))
    m = ''
    if mascot:
        x, y, size = mascot[tall]
        m = f'<div class="mascot" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px">{SYMBOL}</div>'
    return f'''<!doctype html><meta charset="utf-8"><style>{CSS}</style>
<body style="{style}"><div class="s {kind}">
<div class="hd"><div class="brand">{ICON}<span>Prepaide</span></div><div class="pg">{i}/{n}</div></div>
{m}<div class="body">{inner}</div><div class="dots">{dots}</div>{'<div class="swipe"><span>→</span>Glisse pour découvrir</div>' if i == 1 else ''}
</div></body>'''

def cards(items, dark=False):
    out = []
    for it in items:
        lead = f'<div class="num">{it[0]}</div>' if it[0] else ''
        tag = f'<div class="tag t-{it[3]}">{it[3].upper()}</div><br>' if len(it) > 3 else ''
        out.append(f'<div class="card">{lead}<div>{tag}<div class="ct">{it[1]}</div><div class="cd">{it[2]}</div></div></div>')
    return '<div class="cards">' + ''.join(out) + '</div>'

# ---------------- slides génériques ----------------
COVER_M = {False: (560, 690, 470), True: (520, 820, 520)}
SIDE_M = {False: (80, 760, 300), True: (80, 900, 330)}
CTA_M = {False: (370, 230, 340), True: (350, 280, 380)}

def cover(ov, title, sub):
    return ('dark', f'<div class="ov">{ov}</div><h1>{title}</h1><div class="sub">{sub}</div>', COVER_M)
def big(ov, title, sub, dark=False, mascot=False, small=False):
    return ('dark' if dark else 'light', (f'<div class="ov">{ov}</div>' if ov else '') + f'<h1 class="{"m" if small else ""}">{title}</h1>' + (f'<div class="sub">{sub}</div>' if sub else ''), SIDE_M if mascot else None)
def list_(ov, title, items, dark=False, small=True):
    return ('dark' if dark else 'light', (f'<div class="ov">{ov}</div>' if ov else '') + f'<h1 class="{"m" if small else ""}">{title}</h1>' + cards(items), None)
def cta(title, sub, btn='prepaide.fr · lien en bio'):
    return ('dark', f'<div class="center" style="margin-top:var(--ctaT)"><h1 style="font-size:84px">{title}</h1><div class="sub" style="text-align:center">{sub}</div><div class="btn">{btn}</div></div>', CTA_M)
def raw(kind, inner, mascot=None): return (kind, inner, mascot)

OFFER = '1 mois offert, sans carte bancaire.<br>Invite 2 amis : <b>3 mois offerts.</b>'

DASH_MOCK = '''<div class="mock" style="position:relative"><div class="ex">EXEMPLE</div>
<div style="background:linear-gradient(135deg,#5E37B0,#3A1E82);color:#fff;border-radius:22px;padding:30px 32px;display:flex;justify-content:space-between;align-items:center">
<div><div style="font-size:20px;font-weight:800;letter-spacing:3px;color:#B49BFF">OBJECTIF</div><div style="font-size:44px;font-weight:800;letter-spacing:-1.5px;margin-top:4px">HEC Paris</div></div>
<div style="text-align:right"><div style="font-size:60px;font-weight:800;letter-spacing:-2px;line-height:1">J-182</div><div style="font-size:20px;color:#B49BFF;margin-top:6px">avant les écrits</div></div></div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:30px"><div style="font-size:30px;font-weight:800">Aujourd'hui</div><div style="background:#F1EDFB;color:#5E37B0;font-weight:800;font-size:22px;padding:8px 16px;border-radius:999px">3 révisions</div></div>
''' + ''.join(f'<div style="display:flex;gap:18px;align-items:center;margin-top:20px;font-size:28px"><span style="width:30px;height:30px;border-radius:15px;border:3px solid {c};background:{bg}"></span>{t}</div>'
              for t, c, bg in (('Maths · Intégrales', '#0C8A57', '#22C27E'), ('ESH · La monnaie', '#C4C9D8', '#fff'), ('Anglais · Vocabulaire', '#C4C9D8', '#fff'))) + '</div>'

def week_mock(blur=False):
    days = 'LUN MAR MER JEU VEN SAM'.split()
    cells = {0: [('Maths', '#5E37B0'), ('ESH', '#0C8A57')], 1: [('Culture G', '#C2417A'), ('Révision J+1', None)], 2: [('ESH', '#0C8A57'), ('Maths', '#5E37B0')],
             3: [('HGG', '#C47F10'), ('Colle ESH', '#0C8A57')], 4: [('Maths', '#5E37B0'), ('Révision J+3', None)], 5: [('DS maths', '#E25A4E')]}
    cols = ''
    for i, d in enumerate(days):
        items = ''.join((f'<div style="border:2px dashed #0C8A57;background:#E3FAEE;color:#0C8A57;border-radius:12px;padding:10px 8px;font-size:17px;font-weight:800;margin-top:10px">{t}</div>' if c is None else
                         f'<div style="background:{c}1F;border-left:6px solid {c};color:{c};border-radius:12px;padding:10px 8px;font-size:17px;font-weight:800;margin-top:10px">{t}</div>') for t, c in cells[i])
        cols += f'<div style="flex:1;min-width:0"><div style="font-size:17px;font-weight:800;color:#7A839C;letter-spacing:1px;text-align:center">{d}</div>{items}</div>'
    inner = f'<div style="font-size:30px;font-weight:800;letter-spacing:-1px;margin-bottom:18px">Cette semaine</div><div style="display:flex;gap:10px">{cols}</div>'
    if blur:
        return ('<div class="mock" style="position:relative;overflow:hidden"><div style="filter:blur(13px);opacity:.85">' + inner + '</div>'
                '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center"><div style="display:flex;align-items:center;gap:14px;background:#3A1E82;color:#fff;font-weight:800;font-size:34px;padding:22px 34px;border-radius:22px;box-shadow:0 18px 36px rgba(34,16,79,.35)">'
                + LOCK + 'Disponible le 19.10</div></div></div>')
    return '<div class="mock" style="position:relative">' + inner + '<div class="ex">EXEMPLE</div></div>'

GOAL_MOCK = '''<div class="mock" style="background:#fff;color:#16203A;position:relative"><div style="background:linear-gradient(135deg,#5E37B0,#3A1E82);color:#fff;border-radius:22px;padding:30px 32px;display:flex;justify-content:space-between;align-items:center">
<div><div style="font-size:20px;font-weight:800;letter-spacing:3px;color:#B49BFF">OBJECTIF</div><div style="font-size:44px;font-weight:800;letter-spacing:-1.5px;margin-top:4px">ESSEC</div></div>
<div style="text-align:right"><div style="font-size:60px;font-weight:800;letter-spacing:-2px;line-height:1">J-182</div><div style="font-size:20px;color:#B49BFF;margin-top:6px">avant les écrits</div></div></div>
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:24px;padding-bottom:26px">''' + ''.join(f'<div style="background:#F1EDFB;color:#5E37B0;font-weight:800;font-size:24px;padding:12px 20px;border-radius:999px">{e}</div>' for e in ('HEC Paris','ESSEC','ESCP','emlyon','EDHEC')) + '</div><div class="ex">EXEMPLE</div></div>'

IDEA_MOCK = '''<div class="mock" style="position:relative"><div class="ex">EXEMPLE</div>
<div style="font-size:34px;font-weight:800;letter-spacing:-1px">Proposer une fonctionnalité</div>
<div style="margin-top:22px;border:2px solid #E6E0F6;border-radius:20px;padding:24px 26px;font-size:28px;line-height:1.4;color:#16203A;background:#F7F6FC">Pouvoir réviser mes flashcards dans le train, même sans réseau.</div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:24px">
<div style="display:flex;align-items:center;gap:12px;font-size:24px;font-weight:700;color:#5E37B0;background:#F1EDFB;padding:14px 22px;border-radius:999px">+ Ajouter une image</div>
<div style="background:#3A1E82;color:#fff;font-size:26px;font-weight:800;padding:16px 32px;border-radius:16px">Envoyer</div></div></div>'''

DECKS = {
 'c16-indices': [
  cover('J-4', '4 jours.<br><em>4 indices.</em>', 'Devine ce qui arrive lundi pour ta prépa.'),
  raw('light', '<div class="ov">Indice 1</div><h1>Il connaît <span style="color:#5E37B0">ton emploi du temps.</span></h1><div class="sub">Tes cours, tes DS du samedi, tes colles. Tout au même endroit.</div>' + week_mock(True)),
  big('Indice 2', 'Il sait <em>quand tu vas oublier.</em>', 'Et il te fait réviser juste avant.', dark=True, mascot=True),
  list_('Indices 3 et 4', 'Et ce n\'est pas tout.', [('3', 'Tes notes deviennent des flashcards', 'Sans recopier une seule fiche.'), ('4', 'Ton école en ligne de mire', 'Le compte à rebours des concours, chaque matin.')]),
  cta('Rendez-vous lundi <em>19 octobre.</em>', 'Abonne-toi pour ne rien rater.', 'prepaide.fr · 19.10'),
 ],
 'c17-premiere-semaine': [
  cover('Guide', 'Bien démarrer sur Prepaide <em>en 3 étapes.</em>', 'À faire une fois. Ensuite, ton planning se fait tout seul.'),
  raw('light', '<div class="ov">Étape 1</div><h1 class="m">Ajoute ton <span style="color:#5E37B0">emploi du temps.</span></h1><div class="sub">Tes cours, tes DS, tes colles. Puis ajoute ton planning à ton agenda habituel avec un simple lien.</div>' + week_mock()),
  raw('dark', '<div class="ov">Étape 2</div><h1>Choisis <em>ton école.</em></h1><div class="sub">Ton objectif et le compte à rebours des concours s\'affichent sur ton tableau de bord.</div>' + GOAL_MOCK),
  list_('Étape 3', 'Prends tes notes <em>dans Prepaide.</em>', [('', 'À chaque enregistrement', 'Les flashcards du cours sont créées pour toi.'), ('', 'Dans ton calendrier', 'Les révisions de ce cours se placent toutes seules.')]),
  cta('Essaie Prepaide <em>gratuitement.</em>', OFFER),
 ],
 'c18-vrai-faux': [
  cover('Vrai ou faux', '4 idées reçues sur <em>les révisions.</em>', 'Compte tes bonnes réponses.'),
  list_('Idées reçues 1 et 2', 'Celles qui te font perdre du temps', [('', '« Relire mon cours, c\'est réviser. »', 'Te tester avec des flashcards ou des exercices retient mieux que relire.', 'faux'), ('', '« Tout réviser la veille, ça marche. »', 'Plusieurs petites séances retiennent mieux qu\'une seule grosse.', 'faux')]),
  raw('dark', '<div class="ov">Idée reçue 3</div><div class="tag t-vrai">VRAI</div><div class="quote" style="margin-top:18px">« J\'oublie vite ce que je viens d\'apprendre. »</div><div class="sub">Sans révision, une bonne partie s\'efface en quelques jours. C\'est la courbe de l\'oubli.</div>'),
  raw('light', '<div class="ov">Idée reçue 4</div><div class="tag t-vrai">VRAI</div><div class="quote" style="margin-top:18px">« Revoir au bon moment <span style="color:#5E37B0">ralentit l\'oubli.</span> »</div><div class="sub">J+1, J+3, J+7, puis de plus en plus espacé : c\'est la répétition espacée.</div>', SIDE_M),
  cta('Tes révisions espacées, <em>placées pour toi.</em>', 'Prepaide les met dans ton calendrier.<br>1 mois offert, sans carte bancaire.'),
 ],
 'c19-objectif-ecole': [
  cover('Tableau de bord', 'Ton école, <em>en ligne de mire.</em>', 'Chaque matin, en ouvrant Prepaide.'),
  raw('light', '<div class="ov">Onglet tableau de bord</div><h1 class="m">Ton objectif et le compte à rebours, <span style="color:#5E37B0">d\'un coup d\'œil.</span></h1>' + DASH_MOCK),
  big(None, 'Un objectif visible, <em>c\'est plus facile de s\'y tenir.</em>', 'Chaque séance a un sens : elle te rapproche de ton école.', dark=True, mascot=True),
  list_('Et juste en dessous', 'Ta journée, déjà prête', [('1', 'Aujourd\'hui', 'Tes révisions du jour, déjà choisies.'), ('2', 'Cette semaine', 'Tes DS et tes colles, au même endroit.'), ('3', 'Ta progression', 'Matière par matière, dans l\'onglet Statistiques.')]),
  cta('Essaie Prepaide <em>gratuitement.</em>', OFFER),
 ],
 'c20-avec-toi': [
  cover('Communauté', 'Prepaide se construit <em>avec toi.</em>', 'Une idée pour ta prépa ? On t\'écoute.'),
  raw('light', '<div class="ov">Dans l\'app</div><h1 class="m">Un bouton pour <span style="color:#5E37B0">proposer une fonctionnalité.</span></h1><div class="sub">Décris ton idée, ajoute une capture si besoin, envoie.</div>' + IDEA_MOCK.replace('margin-top:var(--cT)', 'margin-top:60px')),
  big(None, 'Tu vis la prépa. <em>Tu sais ce qui te manque.</em>', 'Les meilleures idées viendront de celles et ceux qui révisent tous les jours.', dark=True, mascot=True),
  raw('light', '<div class="ov">À toi</div><h1 class="m">Quelle fonctionnalité tu veux <span style="color:#5E37B0">en premier ?</span></h1><div class="sub">Réponds en commentaire. Par exemple :</div><div class="chips">' + ''.join(f'<div class="chip">{c}</div>' for c in ('Mode hors connexion', 'Planning de colles partagé', 'Spécial concours blancs', 'Ton idée ?')) + '</div>'),
  cta('Essaie Prepaide, <em>puis dis-nous tout.</em>', OFFER),
 ],
 'c21-quel-prepa': [
  cover('Test', 'Quel préparationnaire <em>es-tu ?</em>', 'Tague ton binôme.'),
  list_('Profils A et B', 'Tu te reconnais ?', [('A', 'Le planificateur', '3 versions du planning, 0 révision faite.'), ('B', 'Le dernier-minute', 'Tout le chapitre la veille de la colle.')]),
  list_('Profils C et D', 'Ou plutôt…', [('C', 'Le surligneur fou', 'Tout le cours en fluo, rien en tête.'), ('D', 'Le fantôme du dimanche', 'Dimanche 22 h : « bon, je fais quoi cette semaine ? »')], dark=True),
  big(None, 'Bonne nouvelle : <em>les 4 ont la même solution.</em>', 'Un planning qui se fait tout seul, et des révisions au bon moment.', mascot=True),
  cta('Essaie Prepaide <em>gratuitement.</em>', OFFER),
 ],
}

def render(decks):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for name in decks:
            slides = DECKS[name]
            for fmt in ('instagram', 'tiktok'):
                d = OUT / name / fmt; d.mkdir(parents=True, exist_ok=True)
                for i, (kind, inner, m) in enumerate(slides, 1):
                    h = page(kind, i, len(slides), fmt, inner, m)
                    h = h.replace('--ctaT', '--x').replace('margin-top:var(--x)', 'margin-top:' + ('460px' if fmt == 'tiktok' else '430px'))
                    pg.set_content(h); pg.evaluate('document.fonts.ready')
                    pg.set_viewport_size({'width': 1080, 'height': 1920 if fmt == 'tiktok' else 1350})
                    png = d / f'{name}-{i}.png'
                    pg.screenshot(path=str(png), clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1920 if fmt == 'tiktok' else 1350})
                    if fmt == 'tiktok':
                        Image.open(png).convert('RGB').save(d / f'{name}-{i}.jpg', 'JPEG', quality=92, optimize=True)
                        png.unlink()
            print('ok', name)
        b.close()

if __name__ == '__main__':
    render(sys.argv[1:] or list(DECKS))

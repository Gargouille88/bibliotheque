import pandas as pd
import json
import re

df = pd.read_csv("books.csv")

books = []
for _, row in df.iterrows():
    isbn = str(row.get("ISBN/UID", "")).strip()
    if isbn in ["nan", "None", ""]:
        isbn = ""
    isbn_clean = isbn.replace("-", "").replace(" ", "")
    cover = (
        f"https://covers.openlibrary.org/b/isbn/{isbn_clean}-M.jpg"
        if isbn_clean and len(isbn_clean) >= 10
        else ""
    )

    def clean(val):
        s = str(val)
        return "" if s == "nan" else s

    books.append({
        "t": clean(row.get("Title", "")),
        "a": clean(row.get("Authors", "")),
        "c": cover,
        "r": clean(row.get("Star Rating", "")),
        "s": clean(row.get("Read Status", "")),
        "g": clean(row.get("Tags", "")),
        "f": clean(row.get("Format", "")),
    })

books_json = json.dumps(books, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ma Bibliothèque</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #1a1208; --paper: #f7f2e8; --cream: #ede6d3;
    --gold: #b8922a; --rust: #8b3a1f;
    --read-color: #5a6e4e; --toread-color: #3a5a8b;
    --dnf-color: #8b3a1f; --reading-color: #b8922a;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background-color: var(--paper); color: var(--ink); font-family: 'Crimson Pro', Georgia, serif; min-height: 100vh; }}
  header {{ background: var(--ink); padding: 2.5rem 2rem 2rem; text-align: center; position: relative; overflow: hidden; }}
  header::before {{ content: ''; position: absolute; inset: 0; background: repeating-linear-gradient(45deg, transparent, transparent 40px, rgba(184,146,42,0.04) 40px, rgba(184,146,42,0.04) 41px); }}
  header h1 {{ font-family: 'Playfair Display', Georgia, serif; font-size: clamp(2rem, 5vw, 3.5rem); color: var(--gold); font-weight: 700; letter-spacing: 0.05em; position: relative; }}
  header p {{ color: rgba(247,242,232,0.55); font-size: 1rem; margin-top: 0.4rem; font-style: italic; letter-spacing: 0.08em; position: relative; }}
  .stats-bar {{ background: var(--cream); border-bottom: 1px solid rgba(26,18,8,0.1); padding: 0.9rem 1.5rem; display: flex; flex-wrap: wrap; gap: 1.2rem; align-items: center; justify-content: center; }}
  .stat-pill {{ display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; font-weight: 500; letter-spacing: 0.02em; }}
  .stat-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .stat-pill span {{ color: rgba(26,18,8,0.6); }}
  .stat-pill strong {{ color: var(--ink); }}
  .controls {{ background: var(--paper); padding: 1.2rem 1.5rem; display: flex; flex-wrap: wrap; gap: 0.8rem; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(26,18,8,0.08); position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 12px rgba(26,18,8,0.06); }}
  .search-wrap {{ position: relative; flex: 1; min-width: 200px; max-width: 360px; }}
  .search-wrap svg {{ position: absolute; left: 10px; top: 50%; transform: translateY(-50%); opacity: 0.4; }}
  #search {{ width: 100%; padding: 0.55rem 0.8rem 0.55rem 2.2rem; border: 1.5px solid rgba(26,18,8,0.18); border-radius: 3px; background: #fff; font-family: 'Crimson Pro', serif; font-size: 1rem; color: var(--ink); outline: none; transition: border-color 0.2s; }}
  #search:focus {{ border-color: var(--gold); }}
  #search::placeholder {{ color: rgba(26,18,8,0.35); font-style: italic; }}
  .filter-group {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
  .filter-btn {{ padding: 0.4rem 0.9rem; border: 1.5px solid rgba(26,18,8,0.18); border-radius: 2px; background: transparent; font-family: 'Crimson Pro', serif; font-size: 0.85rem; cursor: pointer; color: rgba(26,18,8,0.6); transition: all 0.15s; letter-spacing: 0.03em; }}
  .filter-btn:hover {{ border-color: var(--gold); color: var(--gold); }}
  .filter-btn.active {{ background: var(--ink); color: var(--gold); border-color: var(--ink); }}
  .filter-btn.f-read.active {{ background: var(--read-color); border-color: var(--read-color); color: #fff; }}
  .filter-btn.f-toread.active {{ background: var(--toread-color); border-color: var(--toread-color); color: #fff; }}
  .filter-btn.f-dnf.active {{ background: var(--dnf-color); border-color: var(--dnf-color); color: #fff; }}
  .filter-btn.f-reading.active {{ background: var(--reading-color); border-color: var(--reading-color); color: #fff; }}
  .count-label {{ font-size: 0.82rem; color: rgba(26,18,8,0.45); font-style: italic; white-space: nowrap; }}
  #grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1.5rem; padding: 2rem 1.5rem; max-width: 1400px; margin: 0 auto; }}
  .book-card {{ position: relative; cursor: pointer; transition: transform 0.2s ease; }}
  .book-card:hover {{ transform: translateY(-4px); }}
  .cover-wrap {{ position: relative; aspect-ratio: 2/3; background: var(--cream); border-radius: 2px; overflow: hidden; box-shadow: 3px 4px 12px rgba(26,18,8,0.22); }}
  .cover-wrap::after {{ content: ''; position: absolute; left: 0; top: 0; width: 8px; height: 100%; background: linear-gradient(to right, rgba(0,0,0,0.18), transparent); pointer-events: none; }}
  .cover-img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .cover-placeholder {{ width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0.8rem; text-align: center; background: linear-gradient(135deg, #e8dfc8, #d4c9a8); }}
  .cover-placeholder .pl-title {{ font-family: 'Playfair Display', serif; font-size: 0.72rem; font-weight: 700; color: var(--ink); line-height: 1.3; margin-bottom: 0.5rem; word-break: break-word; hyphens: auto; }}
  .cover-placeholder .pl-author {{ font-size: 0.6rem; color: rgba(26,18,8,0.55); font-style: italic; word-break: break-word; }}
  .cover-placeholder .pl-icon {{ font-size: 1.6rem; opacity: 0.3; margin-bottom: 0.4rem; }}
  .status-badge {{ position: absolute; top: 6px; right: 6px; width: 10px; height: 10px; border-radius: 50%; border: 2px solid rgba(247,242,232,0.8); box-shadow: 0 1px 3px rgba(0,0,0,0.3); }}
  .sb-read {{ background: var(--read-color); }} .sb-to-read {{ background: var(--toread-color); }} .sb-did-not-finish {{ background: var(--dnf-color); }} .sb-currently-reading {{ background: var(--reading-color); }}
  .book-rating {{ display: flex; gap: 1px; margin-top: 0.4rem; justify-content: center; }}
  .star {{ font-size: 0.65rem; color: rgba(26,18,8,0.2); }} .star.filled {{ color: var(--gold); }}
  .book-title-short {{ font-family: 'Playfair Display', serif; font-size: 0.72rem; font-weight: 400; color: var(--ink); text-align: center; margin-top: 0.4rem; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
  #modal-overlay {{ display: none; position: fixed; inset: 0; background: rgba(26,18,8,0.7); z-index: 1000; backdrop-filter: blur(4px); align-items: center; justify-content: center; padding: 1rem; }}
  #modal-overlay.open {{ display: flex; }}
  .modal-box {{ background: var(--paper); border-radius: 3px; max-width: 560px; width: 100%; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; box-shadow: 0 20px 60px rgba(0,0,0,0.4); }}
  .modal-body {{ display: flex; gap: 1.5rem; padding: 1.8rem; }}
  .modal-cover {{ flex-shrink: 0; width: 110px; }} .modal-cover .cover-wrap {{ aspect-ratio: 2/3; width: 110px; }}
  .modal-info {{ flex: 1; min-width: 0; }}
  .modal-info h2 {{ font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 700; color: var(--ink); line-height: 1.3; margin-bottom: 0.3rem; }}
  .modal-author {{ font-size: 0.9rem; color: rgba(26,18,8,0.6); font-style: italic; margin-bottom: 0.9rem; }}
  .modal-meta {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.9rem; }}
  .meta-tag {{ padding: 0.2rem 0.6rem; border-radius: 2px; font-size: 0.75rem; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 500; }}
  .tag-read {{ background: rgba(90,110,78,0.15); color: var(--read-color); }} .tag-to-read {{ background: rgba(58,90,139,0.13); color: var(--toread-color); }} .tag-did-not-finish {{ background: rgba(139,58,31,0.13); color: var(--dnf-color); }} .tag-currently-reading {{ background: rgba(184,146,42,0.15); color: #8a6a10; }} .tag-format {{ background: rgba(26,18,8,0.07); color: rgba(26,18,8,0.6); }} .tag-genre {{ background: rgba(184,146,42,0.12); color: #7a5c10; }}
  .modal-rating {{ display: flex; gap: 2px; margin-bottom: 0.5rem; }} .modal-rating .star {{ font-size: 0.9rem; }}
  .close-btn {{ position: sticky; top: 0; background: var(--paper); border: none; padding: 0.8rem 1.8rem; text-align: right; cursor: pointer; font-family: 'Crimson Pro', serif; font-size: 0.85rem; color: rgba(26,18,8,0.5); border-bottom: 1px solid rgba(26,18,8,0.08); letter-spacing: 0.06em; text-transform: uppercase; }}
  .close-btn:hover {{ color: var(--rust); }}
  @media (max-width: 600px) {{ #grid {{ grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 1rem; padding: 1.2rem; }} .modal-body {{ flex-direction: column; }} .modal-cover {{ width: 100%; display: flex; justify-content: center; }} .modal-cover .cover-wrap {{ width: 120px; }} }}
</style>
</head>
<body>
<header>
  <h1>Ma Bibliothèque</h1>
  <p id="header-sub">— —</p>
</header>
<div class="stats-bar" id="stats-bar"></div>
<div class="controls">
  <div class="search-wrap">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input type="search" id="search" placeholder="Titre, auteur…">
  </div>
  <div class="filter-group" id="filter-btns">
    <button class="filter-btn active" data-filter="all">Tous</button>
    <button class="filter-btn f-read" data-filter="read">Lus</button>
    <button class="filter-btn f-toread" data-filter="to-read">À lire</button>
    <button class="filter-btn f-reading" data-filter="currently-reading">En cours</button>
    <button class="filter-btn f-dnf" data-filter="did-not-finish">Abandonnés</button>
  </div>
  <div class="count-label" id="count-label"></div>
</div>
<div id="grid"></div>
<div id="modal-overlay" role="dialog" aria-modal="true">
  <div class="modal-box">
    <button class="close-btn" id="close-modal">Fermer ✕</button>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>
<script>
const BOOKS = {books_json};
const STATUS_LABELS = {{'read':'Lu','to-read':'À lire','did-not-finish':'Abandonné','currently-reading':'En cours'}};
let currentFilter = 'all', currentSearch = '';
function buildStats() {{
  const counts = {{'read':0,'to-read':0,'did-not-finish':0,'currently-reading':0}};
  BOOKS.forEach(b => {{ if (counts[b.s] !== undefined) counts[b.s]++; }});
  const colors = {{'read':'#5a6e4e','to-read':'#3a5a8b','did-not-finish':'#8b3a1f','currently-reading':'#b8922a'}};
  const labels = {{'read':'Lus','to-read':'À lire','did-not-finish':'Abandonnés','currently-reading':'En cours'}};
  document.getElementById('header-sub').textContent = `${{BOOKS.length}} livres dans la collection`;
  document.getElementById('stats-bar').innerHTML = Object.entries(counts).map(([s,n]) => `<div class="stat-pill"><div class="stat-dot" style="background:${{colors[s]}}"></div><strong>${{n}}</strong><span>${{labels[s]}}</span></div>`).join('');
}}
function stars(rating) {{
  if (!rating) return '';
  const r = parseFloat(rating), full = Math.floor(r), half = r%1>=0.5?1:0, empty = 5-full-half;
  return Array(full).fill('<span class="star filled">★</span>').join('')+Array(half).fill('<span class="star filled" style="opacity:.6">★</span>').join('')+Array(empty).fill('<span class="star">★</span>').join('');
}}
function makePlaceholder(book) {{
  const div = document.createElement('div'); div.className = 'cover-placeholder';
  div.innerHTML = `<div class="pl-icon">📖</div><div class="pl-title">${{book.t.length>40?book.t.slice(0,40)+'…':book.t}}</div><div class="pl-author">${{book.a.length>30?book.a.slice(0,30)+'…':book.a}}</div>`;
  return div;
}}
function makeCover(book) {{
  if (book.c) {{
    const img = document.createElement('img'); img.className='cover-img'; img.loading='lazy'; img.alt=book.t; img.src=book.c;
    img.onerror = function() {{ this.parentNode.replaceChild(makePlaceholder(book), this); }};
    return img;
  }}
  return makePlaceholder(book);
}}
function render() {{
  const q = currentSearch.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
  const visible = BOOKS.filter(b => {{
    const m = currentFilter==='all'||b.s===currentFilter;
    if (!q) return m;
    return m && (b.t.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').includes(q)||b.a.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').includes(q));
  }});
  const grid = document.getElementById('grid'); grid.innerHTML='';
  document.getElementById('count-label').textContent=`${{visible.length}} livre${{visible.length>1?'s':''}}`;
  if (!visible.length) {{ grid.innerHTML='<p style="grid-column:1/-1;text-align:center;padding:4rem;color:rgba(26,18,8,.4);font-style:italic">Aucun livre trouvé.</p>'; return; }}
  visible.forEach(book => {{
    const card=document.createElement('div'); card.className='book-card'; card.tabIndex=0;
    const wrap=document.createElement('div'); wrap.className='cover-wrap'; wrap.appendChild(makeCover(book));
    const badge=document.createElement('div'); badge.className=`status-badge sb-${{book.s}}`; wrap.appendChild(badge);
    card.appendChild(wrap);
    if (book.r) {{ const rd=document.createElement('div'); rd.className='book-rating'; rd.innerHTML=stars(book.r); card.appendChild(rd); }}
    const td=document.createElement('div'); td.className='book-title-short'; td.textContent=book.t; card.appendChild(td);
    card.addEventListener('click',()=>openModal(book)); card.addEventListener('keydown',e=>{{if(e.key==='Enter'||e.key===' ')openModal(book);}});
    grid.appendChild(card);
  }});
}}
function openModal(book) {{
  const overlay=document.getElementById('modal-overlay'), body=document.getElementById('modal-body');
  const wrap=document.createElement('div'); wrap.className='modal-cover';
  const cw=document.createElement('div'); cw.className='cover-wrap'; cw.appendChild(makeCover(book)); wrap.appendChild(cw);
  const info=document.createElement('div'); info.className='modal-info';
  const genres=book.g?book.g.split(',').map(g=>g.trim()).filter(Boolean):[];
  info.innerHTML=`<h2>${{book.t}}</h2><div class="modal-author">${{book.a||'Auteur inconnu'}}</div>${{book.r?`<div class="modal-rating">${{stars(book.r)}}<span style="margin-left:.4rem;font-size:.85rem;color:rgba(26,18,8,.5)">${{book.r}}/5</span></div>`:''}}<div class="modal-meta"><span class="meta-tag tag-${{book.s}}">${{STATUS_LABELS[book.s]||book.s}}</span>${{book.f?`<span class="meta-tag tag-format">${{book.f}}</span>`:''}}</div>`;
  body.innerHTML=''; body.appendChild(wrap); body.appendChild(info);
  overlay.classList.add('open'); document.body.style.overflow='hidden';
}}
function closeModal() {{ document.getElementById('modal-overlay').classList.remove('open'); document.body.style.overflow=''; }}
document.getElementById('close-modal').addEventListener('click',closeModal);
document.getElementById('modal-overlay').addEventListener('click',e=>{{if(e.target===e.currentTarget)closeModal();}});
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeModal();}});
document.getElementById('search').addEventListener('input',e=>{{currentSearch=e.target.value;render();}});
document.getElementById('filter-btns').addEventListener('click',e=>{{
  const btn=e.target.closest('[data-filter]'); if(!btn) return;
  currentFilter=btn.dataset.filter;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); render();
}});
buildStats(); render();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ index.html généré avec {len(books)} livres.")

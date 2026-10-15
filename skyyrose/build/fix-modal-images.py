#!/usr/bin/env python3
"""
fix-modal-images.py
Rewrites modal structure and product image mapping in all 3 explore pages.
"""

import json
import os
import re

# ─────────────────────────────────────────────
# 1. Product arrays
# ─────────────────────────────────────────────

BR_PRODUCTS = [
    {
        "id": "br-001",
        "name": "BLACK Rose Crewneck",
        "collection": "BLACK ROSE",
        "badge": "PRE-ORDER",
        "price": "$125",
        "desc": "Gothic luxury blooms in twilight. Embroidered with defiant elegance, a dark romance woven in every thread.",
        "detail": "Premium Cotton \u2022 Relaxed Oversized Fit \u2022 Machine Wash Cold",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black", "hex": "#000000"}],
        "image": "assets/images/products/br-001/br-001-model.jpg",
        "image2": "assets/images/products/br-001/br-001-product-2.jpg",
        "x": 22,
        "y": 62,
    },
    {
        "id": "br-006",
        "name": "BLACK Rose Sherpa Jacket",
        "collection": "BLACK ROSE",
        "badge": "PRE-ORDER",
        "price": "$295",
        "desc": "Unveil your dark allure. Lustrous black satin with plush Sherpa lining, crowned by exquisite embroidered rose.",
        "detail": "Satin Shell \u2022 Sherpa Lining \u2022 Embroidered Rose",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black", "hex": "#000000"}],
        "image": "assets/images/products/br-006/br-006-model.jpg",
        "image2": "assets/images/products/br-006/br-006-product.jpg",
        "x": 50,
        "y": 28,
    },
    {
        "id": "br-003",
        "name": "BLACK is Beautiful Jersey",
        "collection": "BLACK ROSE",
        "badge": "PRE-ORDER",
        "price": "$110",
        "desc": "Dare to bloom in defiant elegance \u2014 where gothic luxury meets a powerful message, stitched in streetwise style.",
        "detail": "Premium Mesh \u2022 Button-Down Jersey \u2022 Sizes S\u20133XL",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [
            {"name": "Last Oakland", "hex": "#1B4D1B"},
            {"name": "Giants", "hex": "#27251F"},
        ],
        "image": "assets/images/products/br-003/br-003-model.jpg",
        "image2": "assets/images/products/br-003/br-003-product.jpg",
        "x": 76,
        "y": 44,
    },
    {
        "id": "br-002",
        "name": "BLACK Rose Joggers",
        "collection": "BLACK ROSE",
        "badge": "PRE-ORDER",
        "price": "$95",
        "desc": "Twilight comfort meets gothic romance. Embroidered black roses bloom on soft fabric made for those who move in darkness.",
        "detail": "Premium Soft-Touch Fabric \u2022 Tapered Fit \u2022 Machine Wash",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black", "hex": "#000000"}],
        "image": "assets/images/products/br-002/br-002-model.jpg",
        "image2": "assets/images/products/br-002/br-002-product.jpg",
        "x": 35,
        "y": 46,
    },
    {
        "id": "br-004",
        "name": "BLACK Rose Hoodie",
        "collection": "BLACK ROSE",
        "badge": "PRE-ORDER",
        "price": "$145",
        "desc": "Gothic luxury in twilight shadows. Intricate embroidery captures the bloom of darkness \u2014 a defiant statement.",
        "detail": "Premium Cotton Fleece \u2022 Kangaroo Pocket \u2022 Drawstring Hood",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black", "hex": "#000000"}],
        "image": "assets/images/products/br-004/br-004-model.jpg",
        "image2": "assets/images/products/br-004/br-004-product-2.jpg",
        "x": 63,
        "y": 68,
    },
    {
        "id": "br-008",
        "name": "Women's BLACK Rose Hooded Dress",
        "collection": "BLACK ROSE",
        "badge": "PRE-ORDER",
        "price": "$175",
        "desc": "Unleash your inner darkness. Intricate black rose embroidery and a silhouette of gothic mystery.",
        "detail": "Premium Fabric \u2022 Attached Hood \u2022 Embroidered Rose",
        "sizes": ["XS", "S", "M", "L", "XL", "2XL"],
        "colors": [{"name": "Black", "hex": "#000000"}],
        "image": "assets/images/products/br-008/br-008-model.jpg",
        "image2": "assets/images/products/br-008/br-008-product.jpg",
        "x": 86,
        "y": 24,
    },
]

LH_PRODUCTS = [
    {
        "id": "lh-001",
        "name": "The Fannie",
        "collection": "LOVE HURTS",
        "badge": "PRE-ORDER",
        "price": "$65",
        "desc": "A luxury fanny pack embodying Oakland grit, passion, and the defiant bloom of a street rose.",
        "detail": "Premium Leather \u2022 Adjustable Strap \u2022 Rose Embroidery",
        "sizes": ["One Size"],
        "colors": [{"name": "Black", "hex": "#000000"}],
        "image": "assets/images/products/lh-001/lh-001-model.jpg",
        "image2": "assets/images/products/lh-001/lh-001-product.jpg",
        "x": 48,
        "y": 50,
    },
    {
        "id": "lh-002",
        "name": "Love Hurts Joggers",
        "collection": "LOVE HURTS",
        "badge": "AVAILABLE",
        "price": "$95",
        "desc": "Where Oakland grit meets luxury. Feel the fire with the embroidered rose, a symbol of passion forged in the streets.",
        "detail": "Premium Fabric \u2022 Tapered Fit \u2022 Zippered Ankles",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black", "hex": "#000000"}, {"name": "White", "hex": "#F5F5F5"}],
        "image": "assets/images/products/lh-002/lh-002-model.jpg",
        "image2": "assets/images/products/lh-002/lh-002-product.jpg",
        "x": 18,
        "y": 42,
    },
    {
        "id": "lh-004",
        "name": "Love Hurts Varsity Jacket",
        "collection": "LOVE HURTS",
        "badge": "PRE-ORDER",
        "price": "$265",
        "desc": "Oakland grit meets broken hearts. Black satin, fire-red script, secret rose garden. Pre-order your battle armor.",
        "detail": "Black Satin Shell \u2022 Rose-Lined Interior \u2022 Bold Script",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black/Red", "hex": "#1A1A1A"}],
        "image": "assets/images/products/lh-001/lh-001-model.jpg",
        "image2": None,
        "x": 73,
        "y": 34,
    },
    {
        "id": "lh-003",
        "name": "Love Hurts Basketball Shorts",
        "collection": "LOVE HURTS",
        "badge": "AVAILABLE",
        "price": "$75",
        "desc": "Where street passion meets luxury. Rock these mesh shorts with a defiant rose design, born from Oakland grit.",
        "detail": "Breathable Mesh \u2022 Elastic Waistband \u2022 Rose Design",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black/White", "hex": "#1A1A1A"}],
        "image": "assets/images/products/lh-003/lh-003-model.jpg",
        "image2": "assets/images/products/lh-003/lh-003-product.jpg",
        "x": 30,
        "y": 70,
    },
    {
        "id": "lh-002",
        "name": "Love Hurts Joggers \u2014 White",
        "collection": "LOVE HURTS",
        "badge": "AVAILABLE",
        "price": "$95",
        "desc": "White colorway. Oakland grit meets luxury. The embroidered rose speaks for itself on clean white fleece.",
        "detail": "Premium Fabric \u2022 Tapered Fit \u2022 Zippered Ankles",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "White", "hex": "#F5F5F5"}],
        "image": "assets/images/products/lh-002/lh-002-model.jpg",
        "image2": "assets/images/products/lh-002b/lh-002b-product.jpg",
        "x": 83,
        "y": 58,
    },
    {
        "id": "lh-004",
        "name": "Love Hurts Varsity \u2014 Battle Edition",
        "collection": "LOVE HURTS",
        "badge": "PRE-ORDER",
        "price": "$265",
        "desc": "The varsity that started it all. Battle-tested satin, fire-red script, and a rose that bleeds.",
        "detail": "Black Satin Shell \u2022 Sherpa Lining \u2022 Limited Edition",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black/Red", "hex": "#8B0000"}],
        "image": "assets/images/products/lh-003/lh-003-model.jpg",
        "image2": None,
        "x": 56,
        "y": 20,
    },
]

SG_PRODUCTS = [
    {
        "id": "sg-001",
        "name": "The Bay Set",
        "collection": "SIGNATURE",
        "badge": "PRE-ORDER",
        "price": "$225",
        "desc": "Embody West Coast luxury. The iconic blue rose and vibrant Bay Area skyline \u2014 prestige elevated.",
        "detail": "Premium Fabric \u2022 Tee + Shorts Set \u2022 Bay Bridge Design",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "White/Blue", "hex": "#F5F5F5"}],
        "image": "assets/images/products/sg-001/sg-001-model.jpg",
        "image2": "assets/images/products/sg-001/sg-001-product.jpg",
        "x": 50,
        "y": 52,
    },
    {
        "id": "sg-006",
        "name": "Mint & Lavender Hoodie",
        "collection": "SIGNATURE",
        "badge": "AVAILABLE",
        "price": "$145",
        "desc": "Elevated comfort where refreshing mint meets opulent lavender artistry \u2014 Bay Area luxury, effortless.",
        "detail": "Premium Soft-Touch \u2022 Kangaroo Pocket \u2022 Ribbed Cuffs",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Mint/Lavender", "hex": "#B8E0D2"}],
        "image": "assets/images/products/sg-006/sg-006-model.jpg",
        "image2": "assets/images/products/sg-006/sg-006-product.jpg",
        "x": 24,
        "y": 38,
    },
    {
        "id": "sg-009",
        "name": "The Sherpa Jacket",
        "collection": "SIGNATURE",
        "badge": "PRE-ORDER",
        "price": "$295",
        "desc": "Command attention. Opulent West Coast outerwear featuring signature rose embroidery. Pre-order your legacy.",
        "detail": "Premium Shell \u2022 Sherpa Interior \u2022 Signature Rose Embroidery",
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Black", "hex": "#000000"}],
        "image": "assets/images/products/sg-009/sg-009-model.jpg",
        "image2": "assets/images/products/sg-009/sg-009-product-2.jpg",
        "x": 76,
        "y": 34,
    },
    {
        "id": "sg-003",
        "name": "The Signature Tee \u2014 Orchid",
        "collection": "SIGNATURE",
        "badge": "AVAILABLE",
        "price": "$65",
        "desc": "Elevated everyday luxury. Showcasing SkyyRose's commitment to couture-level staples in Orchid colorway.",
        "detail": "Premium Cotton \u2022 SR Monogram Label \u2022 Orchid Colorway",
        "sizes": ["XS", "S", "M", "L", "XL", "2XL"],
        "colors": [{"name": "Orchid", "hex": "#9B59B6"}],
        "image": "assets/images/products/sg-003/sg-003-model.jpg",
        "image2": "assets/images/products/sg-003/sg-003-product.jpg",
        "x": 38,
        "y": 68,
    },
    {
        "id": "sg-007",
        "name": "The Signature Beanie",
        "collection": "SIGNATURE",
        "badge": "AVAILABLE",
        "price": "$45",
        "desc": "Elevate your everyday with luxurious knit, bespoke comfort, and a bold statement of West Coast prestige.",
        "detail": "Fine Knit Yarn \u2022 Embroidered Rose Emblem \u2022 3 Colors",
        "sizes": ["One Size"],
        "colors": [
            {"name": "Red", "hex": "#C0392B"},
            {"name": "Purple", "hex": "#7D3C98"},
            {"name": "Black", "hex": "#1A1A1A"},
        ],
        "image": "assets/images/products/sg-007/sg-007-model.jpg",
        "image2": "assets/images/products/sg-007/sg-007-product.jpg",
        "x": 85,
        "y": 54,
    },
    {
        "id": "sg-005",
        "name": "Stay Golden Tee",
        "collection": "SIGNATURE",
        "badge": "AVAILABLE",
        "price": "$75",
        "desc": "West Coast ambition meets luxury. An opulent rose design in gold \u2014 for those who stay golden.",
        "detail": "Premium Cotton \u2022 Gold Rose Print \u2022 Relaxed Fit",
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL"],
        "colors": [{"name": "Gold", "hex": "#D4AF37"}],
        "image": "assets/images/products/sg-005/sg-005-model.jpg",
        "image2": "assets/images/products/sg-005/sg-005-product.jpg",
        "x": 63,
        "y": 73,
    },
]

# ─────────────────────────────────────────────
# 2. New modal inner HTML
# ─────────────────────────────────────────────

NEW_MODAL_INNER = """
  <div style="padding:10px 0 6px;text-align:center"><div class="modal-handle" style="margin:0 auto"></div></div>
  <div id="m-img-wrap" style="display:none;width:100%;height:380px;overflow:hidden;background:#0d0d0d;position:relative">
    <img id="m-img" src="" alt="" style="width:100%;height:100%;object-fit:contain;object-position:center">
    <img id="m-img2" src="" alt="" style="width:100%;height:100%;object-fit:cover;object-position:top center;display:none;position:absolute;inset:0">
    <button id="m-view-btn" onclick="toggleView()" style="position:absolute;bottom:12px;right:12px;background:rgba(0,0,0,.55);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.15);color:rgba(255,255,255,.7);font-size:8px;letter-spacing:.25em;text-transform:uppercase;padding:6px 10px;border-radius:3px;cursor:pointer;font-family:inherit;display:none">MODEL VIEW</button>
    <button class="modal-close" onclick="closeModal()" style="position:absolute;top:12px;right:12px;background:rgba(0,0,0,.5);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.1);color:rgba(255,255,255,.6);font-size:16px;width:32px;height:32px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1">&times;</button>
  </div>
  <div style="padding:20px 24px 32px">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
      <span class="modal-tag" id="m-tag"></span>
      <span id="m-badge" style="display:none;font-size:8px;letter-spacing:.28em;text-transform:uppercase;padding:3px 8px;border:1px solid rgba(183,110,121,.5);color:#B76E79;border-radius:2px"></span>
    </div>
    <div class="modal-name" id="m-name"></div>
    <div class="modal-price" id="m-price"></div>
    <div class="modal-divider"></div>
    <div class="modal-desc" id="m-desc"></div>
    <div class="modal-detail" id="m-detail"></div>
    <div id="m-colors" style="display:none"></div>
    <div class="sizes-label">Select Size</div>
    <div class="sizes-wrap" id="m-sizes"></div>
    <button class="cart-btn waiting" id="m-cart" onclick="addToCart()">Select a Size</button>
  </div>
"""

# ─────────────────────────────────────────────
# 3. New openModal JS (includes toggleView)
# ─────────────────────────────────────────────

NEW_OPEN_MODAL = (
    "var showingModel=false;"
    "window.toggleView=function(){"
    "showingModel=!showingModel;"
    'var img1=document.getElementById("m-img"),img2=document.getElementById("m-img2"),btn=document.getElementById("m-view-btn");'
    'if(showingModel){img1.style.display="none";img2.style.display="block";if(btn)btn.textContent="PRODUCT VIEW";}'
    'else{img1.style.display="block";img2.style.display="none";if(btn)btn.textContent="MODEL VIEW";}'
    "};"
    "window.openModal=function(p){"
    "currentProduct=p;selectedSize=null;showingModel=false;"
    'document.getElementById("m-tag").textContent=p.collection||"";'
    'document.getElementById("m-name").textContent=p.name;'
    'document.getElementById("m-price").textContent=p.price;'
    'document.getElementById("m-desc").textContent=p.desc;'
    'document.getElementById("m-detail").textContent=p.detail;'
    'var badge=document.getElementById("m-badge");'
    'if(badge){if(p.badge){badge.textContent=p.badge;badge.style.display="inline-block";}else{badge.style.display="none";}}'
    'var imgWrap=document.getElementById("m-img-wrap");'
    'var img1=document.getElementById("m-img"),img2=document.getElementById("m-img2"),btn=document.getElementById("m-view-btn");'
    "if(imgWrap&&p.image){"
    'img1.src=p.image;img1.alt=p.name;img1.style.display="block";'
    'if(p.image2&&img2){img2.src=p.image2;img2.alt=p.name;img2.style.display="none";if(btn)btn.style.display="block";}'
    'else{if(img2)img2.style.display="none";if(btn)btn.style.display="none";}'
    'imgWrap.style.display="block";'
    '}else if(imgWrap){imgWrap.style.display="none";}'
    'var sz=document.getElementById("m-sizes");sz.innerHTML="";'
    "p.sizes.forEach(function(s){"
    'var btn2=document.createElement("button");btn2.className="size-btn";btn2.textContent=s;'
    'btn2.addEventListener("click",function(){selectedSize=s;sz.querySelectorAll(".size-btn").forEach(function(b){b.classList.remove("selected")});btn2.classList.add("selected");var c=document.getElementById("m-cart");c.textContent="Add to Cart";c.className="cart-btn ready"});'
    "sz.appendChild(btn2);"
    "});"
    'var colEl=document.getElementById("m-colors");'
    "if(colEl){"
    'colEl.innerHTML="";'
    "if(p.colors&&p.colors.length>1){"
    'colEl.style.display="block";'
    'var cl=document.createElement("div");cl.style.cssText="font-size:9px;letter-spacing:.35em;text-transform:uppercase;color:rgba(255,255,255,.4);margin-bottom:8px";cl.textContent="COLOR";colEl.appendChild(cl);'
    'var cw=document.createElement("div");cw.style.cssText="display:flex;gap:8px;margin-bottom:16px";'
    'p.colors.forEach(function(col){var sw=document.createElement("div");sw.style.cssText="width:18px;height:18px;border-radius:50%;border:1px solid rgba(255,255,255,.2);cursor:pointer;transition:transform .2s;background:"+col.hex;sw.title=col.name;sw.onmouseenter=function(){this.style.transform="scale(1.2)"};sw.onmouseleave=function(){this.style.transform="scale(1)"};cw.appendChild(sw);});'
    "colEl.appendChild(cw);"
    '}else{colEl.style.display="none";}'
    "}"
    'document.getElementById("m-cart").textContent="Select a Size";'
    'document.getElementById("m-cart").className="cart-btn waiting";'
    'document.getElementById("modal-backdrop").classList.add("open");'
    'requestAnimationFrame(function(){document.getElementById("modal").classList.add("open")});'
    "};"
)

# ─────────────────────────────────────────────
# 4. Processing function
# ─────────────────────────────────────────────

FILES = {
    "/Users/coreyfoster/DevSkyy/skyyrose/explore-black-rose.html": BR_PRODUCTS,
    "/Users/coreyfoster/DevSkyy/skyyrose/explore-love-hurts.html": LH_PRODUCTS,
    "/Users/coreyfoster/DevSkyy/skyyrose/explore-signature.html": SG_PRODUCTS,
}


def replace_products(content, products):
    """Replace var PRODUCTS=[...]; with new array."""
    new_products_js = f"var PRODUCTS={json.dumps(products, ensure_ascii=False)};"
    new_content, n = re.subn(r"var PRODUCTS=\[.*?\];", new_products_js, content, flags=re.DOTALL)
    return new_content, n > 0


def replace_modal_html(content):
    """Replace the inner HTML of <div id="modal">...</div>."""
    marker = 'id="modal">'
    start = content.find(marker)
    if start == -1:
        return content, False

    inner_start = start + len(marker)

    # Find the closing </div> that matches the modal div.
    # We look for </div>\n<script> or </div>\n\n<script>
    # Try both patterns
    for pattern in ["</div>\n<script>", "</div>\n\n<script>"]:
        pos = content.find(pattern, inner_start)
        if pos != -1:
            close_div_pos = pos
            new_content = content[:inner_start] + NEW_MODAL_INNER + content[close_div_pos:]
            return new_content, True

    # Fallback: count nesting depth to find matching </div>
    depth = 1
    i = inner_start
    while i < len(content) and depth > 0:
        open_tag = content.find("<div", i)
        close_tag = content.find("</div>", i)
        if close_tag == -1:
            break
        if open_tag != -1 and open_tag < close_tag:
            depth += 1
            i = open_tag + 4
        else:
            depth -= 1
            if depth == 0:
                close_div_pos = close_tag
                new_content = content[:inner_start] + NEW_MODAL_INNER + content[close_div_pos:]
                return new_content, True
            i = close_tag + 6

    return content, False


def replace_open_modal(content):
    """Replace window.openModal=function(p){...}; with new version."""
    # Match from window.openModal=function(p){ to the first }; after it
    # The function ends with }; on its own (after the closing brace of the function)
    # Use a greedy match up to the pattern that ends the function block
    new_content, n = re.subn(
        r"window\.openModal=function\(p\)\{.*?\};", NEW_OPEN_MODAL, content, flags=re.DOTALL
    )
    return new_content, n > 0


def fix_max_height(content):
    """Replace max-height:75vh with max-height:90vh in #modal CSS."""
    new_content = content.replace("max-height:75vh", "max-height:90vh")
    changed = new_content != content
    return new_content, changed


def process_file(filepath, products):
    print(f"\n{'=' * 60}")
    print(f"Processing: {os.path.basename(filepath)}")
    print(f"{'=' * 60}")

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_size = len(content)

    # Step 1: Replace PRODUCTS
    content, products_ok = replace_products(content, products)
    print(f"  PRODUCTS replaced:   {'YES' if products_ok else 'NO - NOT FOUND'}")

    # Step 2: Replace modal HTML
    content, modal_ok = replace_modal_html(content)
    print(f"  Modal HTML replaced: {'YES' if modal_ok else 'NO - NOT FOUND'}")

    # Step 3: Replace openModal
    content, openmodal_ok = replace_open_modal(content)
    print(f"  openModal replaced:  {'YES' if openmodal_ok else 'NO - NOT FOUND'}")

    # Step 4: Fix max-height
    content, maxheight_ok = fix_max_height(content)
    print(f"  max-height updated:  {'YES' if maxheight_ok else 'NO (already 90vh or not found)'}")

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    new_size = len(content)
    print("  File written:        YES")
    print(f"  Size: {original_size:,} -> {new_size:,} bytes (delta: {new_size - original_size:+,})")

    return products_ok and modal_ok and openmodal_ok


# ─────────────────────────────────────────────
# 5. Run
# ─────────────────────────────────────────────

all_ok = True
for filepath, products in FILES.items():
    ok = process_file(filepath, products)
    if not ok:
        all_ok = False

print(f"\n{'=' * 60}")
print(f"All done. Overall status: {'SUCCESS' if all_ok else 'PARTIAL - check warnings above'}")
print(f"{'=' * 60}\n")

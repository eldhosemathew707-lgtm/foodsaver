import requests
import json
import os
from datetime import datetime, timezone, timedelta

# --- CONFIGURATION ---
TOKEN = os.getenv("SALLING_TOKEN") 
URL = "https://api.sallinggroup.com/v1/food-waste/"
ZIP_CODE = "6400"
PLACEHOLDER_IMG = "https://placehold.co/400x300/252525/e0e0e0?text=No+Image+Available&font=roboto"

def get_clearance_data():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    params = {"zip": ZIP_CODE}
    try:
        response = requests.get(URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Connection error: {e}")
    return []

def generate_html(data):
    store_names = set()
    for store_entry in data:
        store_names.add(store_entry['store']['name'])
        
    dropdown_options = '<option value="all">All Stores</option>'
    for name in sorted(store_names):
        dropdown_options += f'<option value="{name}">{name}</option>'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sønderborg Food Waste Clearance</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-6Y185D49HV"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', 'G-6Y185D49HV');
        </script>
        
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #121212; margin: 0; padding: 0; color: #e0e0e0; }}
            .header-container {{ background: #1e1e1e; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #333;}}
            h1 {{ text-align: center; margin: 0 0 15px 0; font-size: 1.6em; color: #ffffff; font-weight: 800; letter-spacing: -0.5px;}}
            .controls {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }}
            .controls input, .controls select {{ padding: 12px 16px; font-size: 0.95em; border: 1px solid #444; border-radius: 25px; width: 100%; max-width: 220px; outline: none; background: #2a2a2a; color: #fff; transition: all 0.2s;}}
            .controls input:focus, .controls select:focus {{ border-color: #2ecc71; box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.2);}}
            .main-content {{ padding: 20px; max-width: 1200px; margin: 0 auto; }}
            .brand-section {{ margin-bottom: 40px; }}
            .brand-header {{ font-size: 1.8em; font-weight: 800; margin-bottom: 15px; padding-bottom: 5px; border-bottom: 2px solid #333; text-transform: uppercase; color: #fff;}}
            .netto {{ color: #fece00; }}
            .foetex {{ color: #4b7bec; }}
            .bilka {{ color: #3498db; }}
            .store-location {{ font-size: 1.1em; color: #e0e0e0; margin-top: 30px; margin-bottom: 15px; font-weight: 800; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;}}
            .traffic-badge {{ font-size: 0.75em; font-weight: 600; padding: 6px 12px; border-radius: 20px; background: #2a2a2a; color: #aaa; border: 1px solid #444;}}
            .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }}
            .product-card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 16px; overflow: hidden; transition: transform 0.2s; display: flex; flex-direction: column; position: relative;}}
            .product-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.5); border-color: #555;}}
            .img-container {{ width: 100%; height: 160px; background: #252525; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; padding: 15px; box-sizing: border-box; border-bottom: 1px solid #333;}}
            .product-img {{ width: 100%; height: 100%; object-fit: contain; transition: transform 0.3s ease; }}
            .product-card:hover .product-img {{ transform: scale(1.08); }}
            
            /* Badges */
            .discount-badge {{ position: absolute; top: 12px; right: 12px; background: #e74c3c; color: white; padding: 6px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 800; z-index: 10;}}
            .new-badge {{ position: absolute; top: 12px; left: 12px; background: #3498db; color: white; padding: 6px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 800; z-index: 10;}}

            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }}
            .category {{ font-size: 0.7em; text-transform: uppercase; color: #888; margin-bottom: 6px; font-weight: 800;}}
            .title {{ font-weight: 600; font-size: 0.95em; margin-bottom: 12px; line-height: 1.4; color: #ffffff; flex-grow: 1; }}
            .price-box {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 10px; flex-wrap: wrap;}}
            .new-price {{ color: #2ecc71; font-weight: 800; font-size: 1.5em; letter-spacing: -0.5px;}}
            .old-price {{ text-decoration: line-through; color: #888; font-size: 0.9em; }}
            .savings {{ font-size: 0.75em; color: #2ecc71; font-weight: 800; background: rgba(46, 204, 113, 0.1); padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(46, 204, 113, 0.2); width: fit-content; margin-bottom: 10px;}}
            .meta-info {{ font-size: 0.75em; color: #aaa; background: #1a1a1a; padding: 12px 15px; border-top: 1px solid #333; }}
            .meta-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; align-items: center;}}
            .meta-row:last-child {{ margin-bottom: 0; }}
            .expire-alert {{ color: #ff6b6b; font-weight: 800; background: rgba(255, 107, 107, 0.1); padding: 3px 8px; border-radius: 6px;}}
            .low-stock {{ color: #f39c12; font-weight: 800; display: flex; align-items: center; gap: 4px; background: rgba(243, 156, 18, 0.1); padding: 2px 6px; border-radius: 4px;}}
        </style>
    </head>
    <body>
        <div class="header-container">
            <h1>🛒 Sønderborg Food Rescue</h1>
            <div class="controls">
                <input type="text" id="searchInput" onkeyup="filterItems()" placeholder="Search (e.g., chicken, milk)...">
                <select id="storeSelect" onchange="filterItems()">
                    {dropdown_options}
                </select>
                <select id="sortSelect" onchange="sortItems()">
                    <option value="default">Sort: Default</option>
                    <option value="date-new">Date: Newest First</option>
                    <option value="date-old">Date: Oldest First</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="price-desc">Price: High to Low</option>
                    <option value="discount-desc">Discount: High to Low</option>
                </select>
            </div>
        </div>
        <div class="main-content">
    """

    brands = {}
    for store_entry in data:
        brand = store_entry['store']['brand']
        if brand not in brands: brands[brand] = []
        brands[brand].append(store_entry)

    for brand, stores in brands.items():
        html_content += f'<div class="brand-section" id="brand-{brand}"><div class="brand-header {brand}">{brand}</div>'
        
        for store in stores:
            store_name = store['store']['name']
            store_info = store['store']
            flow_data = "[]"
            
            if 'hours' in store_info and len(store_info['hours']) > 0:
                today_hours = store_info['hours'] 
                if 'customerFlow' in today_hours:
                    flow_data = str(today_hours['customerFlow'])

            html_content += f'<div class="store-container" data-store="{store_name}">'
            html_content += f"""
                <div class="store-location">
                    <span>📍 {store_name}</span>
                    <span class="traffic-badge" data-flow="{flow_data}">Loading traffic...</span>
                </div>
                <div class="product-grid">
            """
            
            for item in store['clearances']:
                desc = item['product']['description']
                new_price = item['offer']['newPrice']
                old_price = item['offer']['originalPrice']
                percent = item['offer']['percentDiscount']
                stock = item['offer']['stock']
                stock_unit = item['offer']['stockUnit']
                
                savings = round(old_price - new_price, 2)
                
                start_raw = item['offer']['startTime'] 
                start = start_raw.replace('T', ' ')[:16]
                expire = item['offer']['endTime'].replace('T', ' ')[:16]

                is_new = False
                try:
                    start_dt = datetime.strptime(start_raw[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) - start_dt <= timedelta(hours=24):
                        is_new = True
                except Exception:
                    pass

                new_badge_html = '<div class="new-badge">✨ NEW</div>' if is_new else ''

                categories = item['product'].get('categories', {})
                if 'en' in categories:
                    cat_text = categories['en'].split('>')[-1]
                elif 'da' in categories:
                    cat_text = categories['da'].split('>')[-1]
                else:
                    cat_text = "General"

                img_src = item['product'].get('image') or PLACEHOLDER_IMG

                # Clean Up Decimal Weights
                if stock_unit == 'kg':
                    stock_display_val = f"{round(stock, 2)} kg"
                else:
                    stock_display_val = f"{int(stock)} {stock_unit}"

                if float(stock) <= 2:
                    stock_display = f'<span class="low-stock">🔥 Only {stock_display_val} left!</span>'
                else:
                    stock_display = f'<strong>{stock_display_val}</strong>'

                html_content += f"""
                <div class="product-card" data-start="{start_raw}">
                    <div class="img-container">
                        {new_badge_html}
                        <div class="discount-badge">-{percent}%</div>
                        <img src="{img_src}" class="product-img" loading="lazy" onerror="this.onerror=null;this.src='{PLACEHOLDER_IMG}';">
                    </div>
                    <div class="info">
                        <div class="category">{cat_text}</div>
                        <div class="title">{desc}</div>
                        <div class="price-box">
                            <span class="new-price">{new_price} kr.</span>
                            <span class="old-price">{old_price} kr.</span>
                        </div>
                        <div class="savings">Save {savings:.2f} kr.</div>
                    </div>
                    <div class="meta-info">
                        <div class="meta-row"><span>📦 Stock:</span> {stock_display}</div>
                        <div class="meta-row"><span>🕒 Start:</span> <span>{start}</span></div>
                        <div class="meta-row expire-alert"><span>⏳ Exp:</span> <span>{expire}</span></div>
                    </div>
                </div>
                """
            html_content += '</div></div>'
        html_content += '</div>'
        
    html_content += """
        </div> 
        <script>
            function filterItems() {
                let searchVal = document.getElementById("searchInput").value.toLowerCase();
                let storeVal = document.getElementById("storeSelect").value;
                let storeGroups = document.querySelectorAll(".store-container");
                
                storeGroups.forEach(group => {
                    let storeName = group.getAttribute("data-store");
                    let isStoreMatch = (storeVal === "all" || storeVal === storeName);
                    let cards = group.querySelectorAll(".product-card");
                    let visibleCards = 0;
                    
                    cards.forEach(card => {
                        let text = card.innerText.toLowerCase();
                        if (isStoreMatch && text.includes(searchVal)) {
                            card.style.display = "flex";
                            visibleCards++;
                        } else {
                            card.style.display = "none";
                        }
                    });
                    group.style.display = (visibleCards > 0) ? "block" : "none";
                });
            }

            function sortItems() {
                let sortVal = document.getElementById("sortSelect").value;
                let storeGroups = document.querySelectorAll(".store-container");

                storeGroups.forEach(group => {
                    let grid = group.querySelector(".product-grid");
                    let cards = Array.from(grid.querySelectorAll(".product-card"));

                    if (sortVal !== "default") {
                        cards.sort((a, b) => {
                            let priceA = parseFloat(a.querySelector(".new-price").innerText.replace(" kr.", ""));
                            let priceB = parseFloat(b.querySelector(".new-price").innerText.replace(" kr.", ""));
                            let discountA = parseFloat(a.querySelector(".discount-badge").innerText.replace("-", "").replace("%", ""));
                            let discountB = parseFloat(b.querySelector(".discount-badge").innerText.replace("-", "").replace("%", ""));
                            let dateA = new Date(a.getAttribute("data-start"));
                            let dateB = new Date(b.getAttribute("data-start"));

                            if (sortVal === "price-asc") return priceA - priceB;
                            if (sortVal === "price-desc") return priceB - priceA;
                            if (sortVal === "discount-desc") return discountB - discountA; 
                            if (sortVal === "date-new") return dateB - dateA; 
                            if (sortVal === "date-old") return dateA - dateB; 
                            return 0;
                        });
                    }
                    cards.forEach(card => grid.appendChild(card));
                });
            }

            function updateTraffic() {
                let currentHour = new Date().getHours();
                let badges = document.querySelectorAll(".traffic-badge");
                
                badges.forEach(badge => {
                    let flowStr = badge.getAttribute("data-flow");
                    if (flowStr && flowStr !== "[]") {
                        let flowData = JSON.parse(flowStr);
                        let flow = flowData[currentHour];
                        
                        if (flow === 0) badge.innerHTML = "🌙 Closed";
                        else if (flow < 0.20) badge.innerHTML = "🟢 Quiet right now";
                        else if (flow < 0.40) badge.innerHTML = "🟡 Steady traffic";
                        else badge.innerHTML = "🔴 Busy right now";
                    } else {
                        badge.innerHTML = "⚪ No traffic data";
                    }
                });
            }
            document.addEventListener('DOMContentLoaded', updateTraffic);
        </script>
    </body></html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success: 'index.html' created.")

data = get_clearance_data()
if data:
    generate_html(data)
else:
    print("Failed to generate HTML: No data was found.")

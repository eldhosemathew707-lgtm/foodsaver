import requests
import json
import os

# --- CONFIGURATION ---
# Uses the secure environment variable for GitHub Actions
TOKEN = os.getenv("SALLING_TOKEN") 
URL = "https://api.sallinggroup.com/v1/food-waste/"
ZIP_CODE = "6400"
PLACEHOLDER_IMG = "https://placehold.co/400x300?text=No+Image+Available&font=roboto"

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
    # 1. Create a list of unique stores for the dropdown filter
    store_names = set()
    for store_entry in data:
        store_names.add(store_entry['store']['name'])
        
    dropdown_options = '<option value="all">All Stores</option>'
    for name in sorted(store_names):
        dropdown_options += f'<option value="{name}">{name}</option>'

    # 2. Build the HTML Header with CSS and the Search/Filter Controls
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sønderborg Food Waste Clearance</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; padding: 20px; color: #333; }}
            h1 {{ text-align: center; margin-bottom: 20px; }}
            
            /* Search and Filter Bar */
            .controls {{ display: flex; gap: 15px; justify-content: center; margin-bottom: 40px; flex-wrap: wrap; }}
            .controls input, .controls select {{ padding: 12px; font-size: 1em; border: 1px solid #ccc; border-radius: 8px; width: 100%; max-width: 300px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            
            /* Brand Headers */
            .brand-section {{ margin-bottom: 50px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .brand-header {{ font-size: 2.2em; font-weight: 800; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #eee; text-transform: uppercase; }}
            .netto {{ color: #fece00; text-shadow: 1px 1px 0 #000; }}
            .foetex {{ color: #101c4e; }}
            .bilka {{ color: #005aa3; }}

            /* Grid & Layout */
            .store-location {{ font-size: 1.3em; color: #333; margin-top: 30px; margin-bottom: 15px; font-weight: 600; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; flex-wrap: wrap; gap: 10px;}}
            .traffic-badge {{ font-size: 0.7em; font-weight: normal; padding: 4px 10px; border-radius: 20px; background: #eee; color: #555; }}
            .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 25px; }}
            
            /* Product Card */
            .product-card {{ background: #fff; border: 1px solid #e1e1e1; border-radius: 10px; overflow: hidden; transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; }}
            .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
            .img-container {{ width: 100%; height: 180px; background: #fff; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
            .product-img {{ width: 100%; height: 100%; object-fit: contain; padding: 10px; box-sizing: border-box; }}
            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }}
            .category {{ font-size: 0.75em; text-transform: uppercase; color: #888; margin-bottom: 5px; }}
            .title {{ font-weight: bold; font-size: 1em; margin-bottom: 10px; line-height: 1.3; min-height: 2.6em; }}
            
            /* Prices */
            .prices {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px; }}
            .price-box {{ display: flex; flex-direction: column; }}
            .new-price {{ color: #d9534f; font-weight: 800; font-size: 1.4em; }}
            .old-price {{ text-decoration: line-through; color: #999; font-size: 0.9em; }}
            .discount-badge {{ background: #d9534f; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.85em; font-weight: bold; height: fit-content; }}

            /* Footer Info */
            .meta-info {{ margin-top: auto; font-size: 0.75em; color: #666; background: #fafafa; padding: 10px; border-top: 1px solid #eee; }}
            .meta-row {{ display: flex; justify-content: space-between; margin-bottom: 3px; }}
            .expire-alert {{ color: #d9534f; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Food Waste Clearance (6400)</h1>
        
        <!-- Search and Filter Tools -->
        <div class="controls">
            <input type="text" id="searchInput" onkeyup="filterItems()" placeholder="Search (e.g., chicken, milk, egg)...">
            <select id="storeSelect" onchange="filterItems()">
                {dropdown_options}
            </select>
        </div>
    """

    # Organize data: Brand -> Store List
    brands = {}
    for store_entry in data:
        brand = store_entry['store']['brand']
        if brand not in brands: brands[brand] = []
        brands[brand].append(store_entry)

    # 3. Generate HTML for each brand and store
    for brand, stores in brands.items():
        html_content += f'<div class="brand-section" id="brand-{brand}"><div class="brand-header {brand}">{brand}</div>'
        
        for store in stores:
            store_name = store['store']['name']
            
            # Extract customer flow array safely
            store_info = store['store']
            flow_data = "[]"
            if 'hours' in store_info and len(store_info['hours']) > 0:
                today_hours = store_info['hours'] 
                if 'customerFlow' in today_hours:
                    flow_data = str(today_hours['customerFlow'])

            # Add data-store attribute so Javascript can filter by store name
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
                
                # Format Dates
                start = item['offer']['startTime'].replace('T', ' ')[:16]
                expire = item['offer']['endTime'].replace('T', ' ')[:16]

                # Safe Category extraction
                categories = item['product'].get('categories', {})
                if 'en' in categories:
                    cat_text = categories['en'].split('>')
                elif 'da' in categories:
                    cat_text = categories['da'].split('>')
                else:
                    cat_text = "General"

                # Image Handling
                img_src = item['product'].get('image') or PLACEHOLDER_IMG

                # HTML Card
                html_content += f"""
                <div class="product-card">
                    <div class="img-container">
                        <img src="{img_src}" class="product-img" loading="lazy" onerror="this.onerror=null;this.src='{PLACEHOLDER_IMG}';">
                    </div>
                    <div class="info">
                        <div class="category">{cat_text}</div>
                        <div class="title">{desc}</div>
                        <div class="prices">
                            <div class="price-box">
                                <span class="new-price">{new_price} kr.</span>
                                <span class="old-price">{old_price} kr.</span>
                            </div>
                            <div class="discount-badge">-{percent}%</div>
                        </div>
                    </div>
                    <div class="meta-info">
                        <div class="meta-row"><span>📦 Stock:</span> <strong>{stock} {stock_unit}</strong></div>
                        <div class="meta-row"><span>🕒 Start:</span> <span>{start}</span></div>
                        <div class="meta-row expire-alert"><span>⏳ Expires:</span> <span>{expire}</span></div>
                    </div>
                </div>
                """
            html_content += '</div></div>' # End Grid and Store Container
        html_content += '</div>' # End Brand Section

    # 4. Inject JavaScript for the filters and live customer traffic
    html_content += """
        <script>
            // Logic for the Search Bar and Store Dropdown Filter
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
                        // If the text matches the search AND the store matches the dropdown, show it
                        if (isStoreMatch && text.includes(searchVal)) {
                            card.style.display = "flex";
                            visibleCards++;
                        } else {
                            card.style.display = "none";
                        }
                    });
                    
                    // Hide the entire store header if no products match the search
                    group.style.display = (visibleCards > 0) ? "block" : "none";
                });
            }

            // Logic to calculate how busy the store is right now
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

            // Run the traffic calculation as soon as the page loads
            document.addEventListener('DOMContentLoaded', updateTraffic);
        </script>
    </body></html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success: 'index.html' created.")

# Run the script
data = get_clearance_data()
if data:
    generate_html(data)
else:
    print("Failed to generate HTML: No data was found. Check your API token or internet connection.")

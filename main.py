import requests
import json
import os

# --- CONFIGURATION ---
import os
TOKEN = os.getenv("SALLING_TOKEN")
URL = "https://api.sallinggroup.com/v1/food-waste/"
ZIP_CODE = "6400"

# A generic grey image to show when the real product photo is missing
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
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sønderborg Food Waste Clearance</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; padding: 20px; color: #333; }}
            h1 {{ text-align: center; margin-bottom: 40px; }}
            
            /* Brand Headers */
            .brand-section {{ margin-bottom: 50px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .brand-header {{ font-size: 2.2em; font-weight: 800; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #eee; }}
            .netto {{ color: #fece00; text-shadow: 1px 1px 0 #000; }}
            .foetex {{ color: #101c4e; }}
            .bilka {{ color: #005aa3; }}

            /* Grid Layout */
            .store-location {{ font-size: 1.3em; color: #555; margin-top: 30px; margin-bottom: 15px; font-weight: 600; display: flex; align-items: center; }}
            .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 25px; }}
            
            /* Product Card */
            .product-card {{ background: #fff; border: 1px solid #e1e1e1; border-radius: 10px; overflow: hidden; transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; }}
            .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
            
            /* Image Handling */
            .img-container {{ width: 100%; height: 180px; background: #fff; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
            .product-img {{ width: 100%; height: 100%; object-fit: contain; padding: 10px; box-sizing: border-box; }}
            
            /* Card Content */
            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }}
            .category {{ font-size: 0.75em; text-transform: uppercase; color: #888; margin-bottom: 5px; letter-spacing: 0.5px; }}
            .title {{ font-weight: bold; font-size: 1em; margin-bottom: 10px; line-height: 1.3; min-height: 2.6em; }}
            
            /* Prices */
            .prices {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px; }}
            .price-box {{ display: flex; flex-direction: column; }}
            .new-price {{ color: #d9534f; font-weight: 800; font-size: 1.4em; }}
            .old-price {{ text-decoration: line-through; color: #999; font-size: 0.9em; }}
            .discount-badge {{ background: #d9534f; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.85em; font-weight: bold; height: fit-content; }}

            /* Footer Info */
            .meta-info {{ margin-top: auto; font-size: 0.75em; color: #666; background: #fafafa; padding: 10px; border-top: 1px solid #eee; border-radius: 0 0 10px 10px; }}
            .meta-row {{ display: flex; justify-content: space-between; margin-bottom: 3px; }}
        </style>
    </head>
    <body>
        <h1>Food Waste Clearance Offers (6400)</h1>
    """

    # Organize data: Brand -> Store List
    brands = {}
    for store_entry in data:
        brand = store_entry['store']['brand']
        if brand not in brands:
            brands[brand] = []
        brands[brand].append(store_entry)

    # Generate HTML for each brand
    for brand, stores in brands.items():
        html_content += f'<div class="brand-section"><div class="brand-header {brand}">{brand.upper()}</div>'
        
        for store in stores:
            store_name = store['store']['name']
            address = store['store']['address']['street']
            
            html_content += f'<div class="store-location">📍 {store_name} <span style="font-size:0.8em; font-weight:normal; margin-left:10px; color:#888;">({address})</span></div>'
            html_content += '<div class="product-grid">'
            
            for item in store['clearances']:
                # Extract Data
                desc = item['product']['description']
                new_price = item['offer']['newPrice']
                old_price = item['offer']['originalPrice']
                percent = item['offer']['percentDiscount']
                stock = item['offer']['stock']
                stock_unit = item['offer']['stockUnit']
                
                # Time formatting
                start = item['offer']['startTime'].replace('T', ' ')[:16] # Cut seconds
                update = item['offer']['lastUpdate'].replace('T', ' ')[:16]

                # Category handling
                categories = item['product'].get('categories', {})
                # Try English, then Danish, then fallback
                if 'en' in categories:
                    cat_text = categories['en'].split('>') # Get main category only
                elif 'da' in categories:
                    cat_text = categories['da'].split('>')
                else:
                    cat_text = "General"

                # IMAGE HANDLING: Use placeholder if None, otherwise use URL
                img_url = item['product'].get('image')
                if not img_url:
                    img_src = PLACEHOLDER_IMG
                else:
                    img_src = img_url

                # HTML Card
                html_content += f"""
                <div class="product-card">
                    <div class="img-container">
                        <img src="{img_src}" 
                             class="product-img" 
                             alt="{desc}" 
                             loading="lazy"
                             onerror="this.onerror=null;this.src='{PLACEHOLDER_IMG}';">
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
                        <div class="meta-row"><span>🔄 Update:</span> <span>{update}</span></div>
                    </div>
                </div>
                """
            html_content += '</div>' # End Grid
        html_content += '</div>' # End Brand Section

    html_content += "</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success: 'index.html' created with broken image protection.")

# Run Script
data = get_clearance_data()
if data:
    generate_html(data)
else:
    print("No data found or connection failed.")
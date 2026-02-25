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
    update_time = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%d-%m-%Y at %H:%M")

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

        <!-- FIREBASE SDK INJECTION -->
        <script type="module">
            import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
            import {{ getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, signOut }} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
            import {{ getFirestore, doc, setDoc, getDoc }} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

            // TODO: PASTE YOUR FIREBASE CONFIG HERE:
            const firebaseConfig = {{
                apiKey: "AIzaSyBB6C2ipV6hRF7F_CEWQtb2ENx94CLuGKM",
                authDomain: "food-rescueapp.firebaseapp.com",
                projectId: "food-rescueapp",
                storageBucket: "food-rescueapp.firebasestorage.app",
                messagingSenderId: "201559525774",
                appId: "1:201559525774:web:420f9fc505ae453a04bcdf"
            }};

            // Initialize Firebase
            const app = initializeApp(firebaseConfig);
            window.auth = getAuth(app);
            window.db = getFirestore(app);
            window.signInWithEmailAndPassword = signInWithEmailAndPassword;
            window.createUserWithEmailAndPassword = createUserWithEmailAndPassword;
            window.signOut = signOut;
            window.doc = doc;
            window.setDoc = setDoc;
            window.getDoc = getDoc;
            
            // Fire an event when Firebase is fully loaded
            window.dispatchEvent(new Event('firebase-ready'));
        </script>
        
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #121212; margin: 0; padding: 0; color: #e0e0e0; overflow-x: hidden; }}
            
            /* Header */
            .header-container {{ background: #1e1e1e; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #333; transition: all 0.3s ease;}}
            .header-top {{ display: flex; align-items: center; justify-content: space-between; }} 
            h1 {{ margin: 0; font-size: 1.6em; color: #ffffff; font-weight: 800; letter-spacing: -0.5px;}}
            
            /* Buttons */
            #loginBtn {{ background: #3498db; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }}
            #loginBtn:hover {{ background: #2980b9; }}
            #mobile-menu-btn {{ display: none; }}
            
            /* Controls */
            .controls {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; transition: 0.3s ease; align-items: center; margin-top: 15px; }}
            .controls input, .controls select {{ padding: 12px 16px; font-size: 0.95em; border: 1px solid #444; border-radius: 25px; width: 100%; max-width: 220px; outline: none; background: #2a2a2a; color: #fff; transition: all 0.2s;}}
            
            .fav-filter-container {{ display: flex; align-items: center; gap: 8px; background: #2a2a2a; padding: 12px 16px; border-radius: 25px; border: 1px solid #444; cursor: pointer; color: #fff; font-size: 0.95em; font-weight: 600; user-select: none; transition: 0.2s; }}
            .fav-filter-container input {{ width: auto; margin: 0; cursor: pointer; accent-color: #e74c3c; }}

            /* Mobile Toggle Buttons */
            .close-sidebar-btn {{ display: none; }}
            #sidebar-overlay {{ display: none; }}

            .main-content {{ padding: 20px; max-width: 1200px; margin: 0 auto; min-height: 80vh; }}
            .brand-section {{ margin-bottom: 40px; }}
            .brand-header {{ font-size: 1.8em; font-weight: 800; margin-bottom: 15px; padding-bottom: 5px; border-bottom: 2px solid #333; text-transform: uppercase; color: #fff;}}
            .netto {{ color: #fece00; }}
            .foetex {{ color: #4b7bec; }}
            .bilka {{ color: #3498db; }}
            .store-location {{ font-size: 1.1em; color: #e0e0e0; margin-top: 30px; margin-bottom: 15px; font-weight: 800; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;}}
            .traffic-badge {{ font-size: 0.75em; font-weight: 600; padding: 6px 12px; border-radius: 20px; background: #2a2a2a; color: #aaa; border: 1px solid #444;}}
            .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }}
            .product-card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 16px; overflow: hidden; transition: transform 0.2s; display: flex; flex-direction: column; position: relative;}}
            .img-container {{ width: 100%; height: 160px; background: #252525; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; padding: 15px; box-sizing: border-box; border-bottom: 1px solid #333;}}
            .product-img {{ width: 100%; height: 100%; object-fit: contain; }}
            
            .discount-badge {{ position: absolute; top: 12px; right: 12px; background: #e74c3c; color: white; padding: 6px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 800; z-index: 10;}}
            .new-badge {{ position: absolute; top: 12px; left: 12px; background: #3498db; color: white; padding: 6px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 800; z-index: 10;}}
            .fav-btn {{ position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.6); border: none; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; font-size: 1.2em; cursor: pointer; z-index: 10; transition: 0.2s; backdrop-filter: blur(4px); }}
            
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
            
            .site-footer {{ text-align: center; padding: 25px; color: #888; font-size: 0.9em; border-top: 1px solid #333; background-color: #1a1a1a; margin-top: 20px; }}
            .site-footer span {{ color: #2ecc71; font-weight: 600; }}

            @media (max-width: 768px) {{
                .header-container {{ padding: 12px 15px; }}
                h1 {{ font-size: 1.25em; }}
                #mobile-menu-btn {{ display: inline-block; background: #2a2a2a; color: #fff; border: 1px solid #444; border-radius: 8px; padding: 6px 12px; font-size: 0.9em; font-weight: 600; cursor: pointer; margin-left: 8px;}}
                #loginBtn {{ padding: 6px 12px; font-size: 0.9em; }}
                
                .controls {{ position: fixed; top: 0; left: -300px; width: 260px; height: 100%; background: #1a1a1a; flex-direction: column; justify-content: flex-start; align-items: stretch; padding: 25px 20px; box-shadow: 4px 0 20px rgba(0,0,0,0.8); z-index: 1001; overflow-y: auto; margin-top: 0;}}
                .controls.open {{ left: 0; }}
                .controls input, .controls select {{ max-width: 100%; width: 100%; box-sizing: border-box; }}
                .fav-filter-container {{ max-width: 100%; width: 100%; box-sizing: border-box; justify-content: flex-start; }}
                
                .close-sidebar-btn {{ display: block; background: none; border: none; color: #fff; font-size: 1.5em; font-weight: bold; text-align: right; margin-bottom: 15px; cursor: pointer; }}
                #sidebar-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; opacity: 0; visibility: hidden; transition: 0.3s; }}
                #sidebar-overlay.open {{ opacity: 1; visibility: visible; }}
            }}
        </style>
    </head>
    <body>
        <div id="sidebar-overlay" onclick="toggleSidebar()"></div>

        <div class="header-container">
            <div class="header-top">
                <h1>🛒 Food Rescue</h1>
                <div>
                    <button id="loginBtn" onclick="handleLoginFlow()">Login / Register</button>
                    <button id="mobile-menu-btn" onclick="toggleSidebar()">☰ Filters</button>
                </div>
            </div>
            
            <div class="controls" id="sidebar">
                <button class="close-sidebar-btn" onclick="toggleSidebar()">✕</button>
                <input type="text" id="searchInput" onkeyup="filterItems()" placeholder="Search (e.g., chicken)...">
                <select id="storeSelect" onchange="filterItems()">
                    {dropdown_options}
                </select>
                <select id="sortSelect" onchange="sortItems()">
                    <option value="default">Sort: Default</option>
                    <option value="date-new">Date: Newest First</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="discount-desc">Discount: High to Low</option>
                </select>
                
                <label class="fav-filter-container">
                    <input type="checkbox" id="favFilter" onchange="filterItems()"> 
                    <span>⭐ Favorites Only</span>
                </label>
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
                ean = item['offer'].get('ean', 'unknown')
                
                savings = round(old_price - new_price, 2)
                start_raw = item['offer']['startTime'] 
                start = start_raw.replace('T', ' ')[:16]
                expire = item['offer']['endTime'].replace('T', ' ')[:16]

                is_new = False
                try:
                    start_dt = datetime.strptime(start_raw[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) - start_dt <= timedelta(hours=24):
                        is_new = True
                except Exception: pass
                new_badge_html = '<div class="new-badge">✨ NEW</div>' if is_new else ''

                cat_text = item['product'].get('categories', {}).get('en', 'General').split('>')[-1]
                img_src = item['product'].get('image') or PLACEHOLDER_IMG

                if stock_unit == 'kg': stock_display_val = f"{round(stock, 2)} kg"
                else: stock_display_val = f"{int(stock)} {stock_unit}"
                stock_display = f'<span class="low-stock">🔥 Only {stock_display_val} left!</span>' if float(stock) <= 2 else f'<strong>{stock_display_val}</strong>'

                html_content += f"""
                <div class="product-card" data-start="{start_raw}" data-ean="{ean}">
                    <div class="img-container">
                        {new_badge_html}
                        <div class="discount-badge">-{percent}%</div>
                        <button class="fav-btn" onclick="toggleFavorite(event, '{ean}')">🤍</button>
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
        
    html_content += f"""
        </div> 
        <div class="site-footer">🟢 Live data last updated: <span>{update_time}</span></div>
        
        <script>
            let userFavorites = [];

            // Listen for Firebase to initialize before setting up auth checks
            window.addEventListener('firebase-ready', () => {{
                window.auth.onAuthStateChanged(async (user) => {{
                    if (user) {{
                        document.getElementById("loginBtn").innerText = "Logout";
                        document.getElementById("loginBtn").onclick = handleLogout;
                        
                        // Fetch favorites from Cloud Database
                        try {{
                            const docRef = window.doc(window.db, "users", user.uid);
                            const docSnap = await window.getDoc(docRef);
                            if (docSnap.exists()) {{
                                userFavorites = docSnap.data().favorites || [];
                            }} else {{
                                userFavorites = [];
                            }}
                        }} catch(e) {{ console.log("Db Error:", e); }}
                        
                    }} else {{
                        document.getElementById("loginBtn").innerText = "Login / Register";
                        document.getElementById("loginBtn").onclick = handleLoginFlow;
                        userFavorites = [];
                    }}
                    refreshFavoriteUI();
                }});
            }});

            async function handleLoginFlow() {{
                let email = prompt("Enter your email:");
                if (!email) return;
                let password = prompt("Enter your password (min 6 characters):");
                if (!password) return;

                try {{
                    // Try to log in
                    await window.signInWithEmailAndPassword(window.auth, email, password);
                    alert("Welcome back!");
                }} catch (error) {{
                    // If account doesn't exist, ask to register
                    if (error.code === 'auth/user-not-found' || error.code === 'auth/invalid-credential') {{
                        if(confirm("Account not found. Do you want to create a new account with this email?")) {{
                            try {{
                                await window.createUserWithEmailAndPassword(window.auth, email, password);
                                alert("Account successfully created!");
                            }} catch(err) {{
                                alert("Registration error: " + err.message);
                            }}
                        }}
                    }} else {{
                        alert("Login Error: " + error.message);
                    }}
                }}
            }}

            async function handleLogout() {{
                await window.signOut(window.auth);
                alert("You have been logged out.");
                filterItems(); // Reset the screen if "Show Favorites" was active
            }}

            async function toggleFavorite(event, ean) {{
                event.preventDefault(); 
                
                if (!window.auth || !window.auth.currentUser) {{
                    alert("Please click 'Login / Register' to save favorites to the cloud!");
                    return;
                }}
                
                let btn = event.currentTarget;
                if (userFavorites.includes(ean)) {{
                    userFavorites = userFavorites.filter(id => id !== ean);
                    btn.innerText = "🤍";
                }} else {{
                    userFavorites.push(ean);
                    btn.innerText = "❤️";
                }}
                
                // Save immediately to Firebase Cloud
                try {{
                    const docRef = window.doc(window.db, "users", window.auth.currentUser.uid);
                    await window.setDoc(docRef, {{ favorites: userFavorites }});
                }} catch(e) {{
                    alert("Error saving to cloud: " + e.message);
                }}
                
                if(document.getElementById("favFilter").checked) filterItems();
            }}

            function refreshFavoriteUI() {{
                document.querySelectorAll('.product-card').forEach(card => {{
                    let ean = card.getAttribute('data-ean');
                    let btn = card.querySelector('.fav-btn');
                    if(userFavorites.includes(ean)) btn.innerText = "❤️";
                    else btn.innerText = "🤍";
                }});
            }}

            // --- MENU & FILTERING LOGIC ---
            function toggleSidebar() {{
                document.getElementById("sidebar").classList.toggle("open");
                document.getElementById("sidebar-overlay").classList.toggle("open");
            }}

            function filterItems() {{
                let searchVal = document.getElementById("searchInput").value.toLowerCase();
                let storeVal = document.getElementById("storeSelect").value;
                let showFavs = document.getElementById("favFilter").checked;
                let storeGroups = document.querySelectorAll(".store-container");
                
                storeGroups.forEach(group => {{
                    let storeName = group.getAttribute("data-store");
                    let isStoreMatch = (storeVal === "all" || storeVal === storeName);
                    let cards = group.querySelectorAll(".product-card");
                    let visibleCards = 0;
                    
                    cards.forEach(card => {{
                        let text = card.innerText.toLowerCase();
                        let ean = card.getAttribute('data-ean');
                        let matchesSearch = text.includes(searchVal);
                        let matchesFav = !showFavs || userFavorites.includes(ean);
                        
                        if (isStoreMatch && matchesSearch && matchesFav) {{
                            card.style.display = "flex";
                            visibleCards++;
                        }} else {{
                            card.style.display = "none";
                        }}
                    }});
                    group.style.display = (visibleCards > 0) ? "block" : "none";
                }});
            }}

            function sortItems() {{
                let sortVal = document.getElementById("sortSelect").value;
                document.querySelectorAll(".store-container").forEach(group => {{
                    let grid = group.querySelector(".product-grid");
                    let cards = Array.from(grid.querySelectorAll(".product-card"));

                    if (sortVal !== "default") {{
                        cards.sort((a, b) => {{
                            let priceA = parseFloat(a.querySelector(".new-price").innerText);
                            let priceB = parseFloat(b.querySelector(".new-price").innerText);
                            let discA = parseFloat(a.querySelector(".discount-badge").innerText.replace(/[^0-9.]/g, ''));
                            let discB = parseFloat(b.querySelector(".discount-badge").innerText.replace(/[^0-9.]/g, ''));
                            let dateA = new Date(a.getAttribute("data-start"));
                            let dateB = new Date(b.getAttribute("data-start"));

                            if (sortVal === "price-asc") return priceA - priceB;
                            if (sortVal === "discount-desc") return discB - discA; 
                            if (sortVal === "date-new") return dateB - dateA; 
                            return 0;
                        }});
                    }}
                    cards.forEach(card => grid.appendChild(card));
                }});
                if(window.innerWidth <= 768) toggleSidebar();
            }}

            document.addEventListener('DOMContentLoaded', () => {{
                let currentHour = new Date().getHours();
                document.querySelectorAll(".traffic-badge").forEach(badge => {{
                    let flowStr = badge.getAttribute("data-flow");
                    if (flowStr && flowStr !== "[]") {{
                        let flowData = JSON.parse(flowStr);
                        let flow = flowData[currentHour];
                        if (flow === 0) badge.innerHTML = "🌙 Closed";
                        else if (flow < 0.20) badge.innerHTML = "🟢 Quiet right now";
                        else if (flow < 0.40) badge.innerHTML = "🟡 Steady traffic";
                        else badge.innerHTML = "🔴 Busy right now";
                    }} else badge.innerHTML = "⚪ No traffic data";
                }});
            }});
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

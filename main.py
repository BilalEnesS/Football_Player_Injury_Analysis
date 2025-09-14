import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from io import StringIO

# ---- 1. Helper Function: Extract Injury Table from Single Player ----
def get_injury_history(player_id, player_name):
    """
    Extracts injury table for a player from Transfermarkt.
    
    Args:
        player_id (int): Transfermarkt player ID (e.g., Cristiano Ronaldo = 8198)
        player_name (str): Player name (for logging/dataset)
    
    Returns:
        pd.DataFrame: Player's injury history
    """
    url = f"https://www.transfermarkt.com/player/verletzungen/spieler/{player_id}"
    headers = {"User-Agent": "Mozilla/5.0"}  # Fake user agent
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException as req_err:
        print(f"Error: Request failed for {player_name} ({player_id}): {req_err}")
        return pd.DataFrame()

    if response.status_code != 200:
        print(f"Error: Page failed to load for {player_name} ({player_id}). Status {response.status_code}")
        return pd.DataFrame()
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        print(f"Injury table not found for {player_name}.")
        return pd.DataFrame()

    # Parse each table individually and find the appropriate one
    candidate_df = None
    for html_table in tables:
        try:
            parsed_list = pd.read_html(StringIO(str(html_table)))
        except ValueError:
            continue
        if not parsed_list:
            continue
        df_try = parsed_list[0]

        # Skip empty table
        if df_try.empty:
            continue

        # Normalize column names
        normalized_cols = [str(c).strip().lower() for c in df_try.columns]

        # Expected fields may contain English/German variations
        has_injury_col = any(x in normalized_cols for x in ["injury", "verletzung"])
        has_from_col = any(x in normalized_cols for x in ["from", "von"]) or any("from" in x for x in normalized_cols)
        has_until_col = any(x in normalized_cols for x in ["until", "bis"]) or any("until" in x for x in normalized_cols)

        # Select candidate based on column count and key columns
        if (has_injury_col and has_from_col and has_until_col) or len(df_try.columns) >= 6:
            candidate_df = df_try.copy()
            break

    if candidate_df is None:
        print(f"Suitable injury table not found for {player_name}.")
        return pd.DataFrame()

    df = candidate_df

    # Some tables may have extra/missing columns; take first 6 columns and rename
    if df.shape[1] < 6:
        # If less than 6 columns, data is unreliable; skip
        print(f"Table column count for {player_name} is less than expected ({df.shape[1]}). Skipping.")
        return pd.DataFrame()

    df = df.iloc[:, :6].copy()
    df.columns = ["Season", "Injury", "From", "Until", "Days", "GamesMissed"]
    
    # Add player name and ID
    df["Player"] = player_name
    df["PlayerID"] = player_id
    
    # Convert dates to datetime with dayfirst=True
    df["From"] = pd.to_datetime(df["From"], errors="coerce", dayfirst=True)
    df["Until"] = pd.to_datetime(df["Until"], errors="coerce", dayfirst=True)

    # If day count exists, use it; otherwise calculate from From/Until difference
    if "Days" in df.columns:
        df["Days"] = pd.to_numeric(df["Days"], errors="coerce")

    # If Days is empty, calculate it ourselves
    df.loc[df["Days"].isna() & df["From"].notna() & df["Until"].notna(), "Days"] = \
        (df["Until"] - df["From"]).dt.days

    # Convert to weeks
    df["Weeks"] = (df["Days"] / 7).round(1)

    
    return df

# ---- 1.b Helper: Find Transfermarkt Player ID from Name ----
def search_player_id(player_name):
    """
    Returns the first player ID corresponding to the player name using Transfermarkt quick search.
    Returns None if not found.
    """
    search_url = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(search_url, params={"query": player_name}, headers=headers, timeout=20)
    except requests.RequestException as req_err:
        print(f"Search error: {player_name}: {req_err}")
        return None

    if resp.status_code != 200:
        print(f"Search error: {player_name} status {resp.status_code}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    # Player profile links usually contain '/spieler/<id>'
    first_link = None
    for a in soup.select("a"):
        href = a.get("href") or ""
        if "/spieler/" in href:
            first_link = href
            break
    if not first_link:
        return None
    # href example: /mauro-icardi/profil/spieler/68863 → id is the last number
    try:
        parts = [p for p in first_link.split("/") if p]
        # the last number could be id; otherwise search for the one after 'spieler'
        player_id = None
        for i, part in enumerate(parts):
            if part == "spieler" and i + 1 < len(parts):
                if parts[i+1].isdigit():
                    player_id = int(parts[i+1])
                    break
        if player_id is None and parts[-1].isdigit():
            player_id = int(parts[-1])
        return player_id
    except Exception:
        return None

# ---- 2. Player Names List (IDs will be found automatically) ----
player_names = [
    # Galatasaray
    "Mauro Icardi",
    "Dries Mertens",
    "Hakim Ziyech", 
    "Lucas Torreira",
    "Fernando Muslera",
    "Kerem Aktürkoğlu",
    "Barış Alper Yılmaz",
    "Wilfried Zaha",
    "Tanguy Ndombele",
    "Edin Dzeko",
    "Dusan Tadic",
    "Sebastian Szymanski",
    "Fred",
    "Ferdi Kadioglu",
    "Cengiz Ünder",
    "Dominik Livakovic",
    "Vincent Aboubakar",
    "Cenk Tosun",
    "Semih Kılıçsoy",
    "Gedson Fernandes",
    "Rachid Ghezzal",
    "Romain Saïss",
    "Edin Višća",
    "Paul Onuachu",
    "Trezeguet",
    "Anastasios Bakasetas",
    "Yusuf Yazıcı",
    "Davy Klaassen",
    "Edgar Ié",
    "Ryan Kent",
    
    # Beşiktaş
    "Mert Günok",
    "Necip Uysal",
    "Ersin Destanoğlu",
    "Daniel Amartey",
    "Eric Bailly",
    
    # Fenerbahçe
    "İrfan Can Kahveci",
    "Mert Müldür",
    "İsmail Yüksek",
    "Samuel Osayi-Samuel",
    "Alexander Djiku",
    "Miha Zajc",
    "Michy Batshuayi",
    
    # Trabzonspor
    "Uğurcan Çakır",
    "Onuralp Çevikkan",
    "Ahmet Yıldırım",
    "Arseniy Batagov",
    "Serdar Saatçı",
    
    # Real Madrid
    "Thibaut Courtois",
    "Andriy Lunin",
    "Dani Carvajal",
    "Éder Militão",
    "David Alaba",
    "Trent Alexander-Arnold",
    "Federico Valverde",
    "Aurelien Tchouameni",
    "Arda Güler",
    "Dani Ceballos",
    "Vinícius Jr",
    "Kylian Mbappé",
    "Rodrygo",
    
    # Barcelona
    "Marc-André ter Stegen",
    "Jules Koundé",
    "Ronald Araújo",
    "Pau Cubarsí",
    "Andreas Christensen",
    "Alejandro Balde",
    "Pedri",
    "Frenkie de Jong",
    "Gavi",
    "Lamine Yamal",
    "Raphinha",
    "Dani Olmo",
    "Robert Lewandowski",
    "Marcus Rashford",
    "Ferran Torres",
    
    # Atlético Madrid
    "Jan Oblak",
    "José María Giménez",
    "Nahuel Molina",
    "Koke",
    "Marcos Llorente",
    "Antoine Griezmann",
    "Julián Álvarez",
    
    # Lille
    "Berke Özer",
    "Aïssa Mandi",
    "Nabil Bentaleb",
    "Benjamin André",
    "Olivier Giroud",
    
    # Real Betis
    "Álvaro Valles",
    "Héctor Bellerín",
    "Pablo Fornals",
    "Sofyan Amrabat",
    "Isco",
    
    # Everton
    "Jordan Pickford",
    "Nathan Patterson",
    "James Tarkowski",
    "Jarrad Branthwaite",
    "Dwight McNeil",
    "Idrissa Gueye",
    "James Garner",
    "Carlos Alcaraz",
    
    # Arsenal
    "David Raya",
    "William Saliba",
    "Ben White",
    "Gabriel",
    "Martin Ødegaard",
    "Eberechi Eze",
    "Leandro Trossard",
    "Noni Madueke",
    
    # Crystal Palace
    "Dean Henderson",
    "Joel Ward",
    "Marc Guehi",
    "Jefferson Lerma",
    "Daichi Kamada",
    
    # Fulham
    "Bernd Leno",
    "Kenny Tete",
    "Joachim Andersen",
    "Timothy Castagne",
    "Harrison Reed",
    "Tom Cairney",
    "Alex Iwobi",
    "Sander Berge",
    "Emile Smith Rowe",
    "Adama Traoré",
    
    # Brighton
    "Bart Verbruggen",
    "Tariq Lamptey",
    "Lewis Dunk",
    "Pervis Estupiñán",
    "Joel Veltman",
    "James Milner",
    "Solly March",
    "Carlos Baleba"
]

# ---- 3. Find Player IDs and Extract Injury Data ----
print("🔍 Searching for player IDs and extracting injury data...")

all_injuries = []
successful_players = 0
total_players = len(player_names)

for i, player_name in enumerate(player_names):
    print(f"  {i+1}/{total_players}: Processing {player_name}...")
    
    # Find player ID
    player_id = search_player_id(player_name)
    if player_id is None:
        print(f"    ❌ ID not found: {player_name}")
        continue
    
    print(f"    ✅ ID found: {player_id}")
    
    # Extract injury data
    df = get_injury_history(player_id, player_name)
    if not df.empty:
        all_injuries.append(df)
        successful_players += 1
        print(f"    📊 {len(df)} injury records found")
    else:
        print(f"    ⚠️ No injury data found")
    
    time.sleep(2)  # delay for anti-ban

print(f"\n📈 Summary: Data extracted from {successful_players}/{total_players} players")

# ---- 3. Merge Dataset ----
if all_injuries:
    final_df = pd.concat(all_injuries, ignore_index=True)
    print(final_df.head(20))
    final_df.to_csv("injury_dataset_extended.csv", index=False, encoding="utf-8-sig")
    print("\n✅ injury_dataset_extended.csv saved!")
else:
    print("No data could be extracted.")

# ---- 4. Major Players Playing in Turkey: Extract with Name List and Save Separately ----
tr_player_names = [
    "Mauro Icardi",
    "Dries Mertens", 
    "Hakim Ziyech",
    "Lucas Torreira",
    "Fernando Muslera",
    "Kerem Aktürkoğlu",
    "Barış Alper Yılmaz",
    "Wilfried Zaha",
    "Tanguy Ndombele",
    "Edin Dzeko",
    "Dusan Tadic",
    "Sebastian Szymanski",
    "Fred",
    "Ferdi Kadioglu",
    "Cengiz Ünder",
    "Dominik Livakovic",
    "Vincent Aboubakar",
    "Cenk Tosun",
    "Semih Kılıçsoy",
    "Gedson Fernandes",
    "Rachid Ghezzal",
    "Romain Saïss",
    "Edin Višća",
    "Paul Onuachu",
    "Trezeguet",
    "Anastasios Bakasetas",
    "Yusuf Yazıcı",
    "Davy Klaassen",
    "Edgar Ié",
    "Ryan Kent"
]

resolved_players_tr = []
for name in tr_player_names:
    pid = search_player_id(name)
    if pid is not None:
        resolved_players_tr.append((pid, name))
    else:
        print(f"ID not found (skipped): {name}")
    time.sleep(1.5)  # small delay for search requests

tr_injuries = []
for pid, pname in resolved_players_tr:
    df_tr = get_injury_history(pid, pname)
    if not df_tr.empty:
        tr_injuries.append(df_tr)
    time.sleep(2)

if tr_injuries:
    final_tr = pd.concat(tr_injuries, ignore_index=True)
    print(final_tr.head(20))
    final_tr.to_csv("injury_dataset_tr.csv", index=False, encoding="utf-8-sig")
    print("\n✅ injury_dataset_tr.csv saved!")
else:
    print("No data could be extracted for Turkey list.")

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json
import os

def scrape_greed_index():
    """Scrape CNN Fear & Greed Index and related indices"""
    url = "https://edition.cnn.com/markets/fear-and-greed"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        data = {
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        # Try to parse JSON blocks first (if CNN provides structured data)
        found = False
        for script in soup.find_all('script', type='application/json'):
            try:
                js = script.string
                if not js:
                    continue
                j = json.loads(js)
                # look for common keys
                if isinstance(j, dict) and ('fearAndGreedIndex' in j or 'components' in j):
                    fim = j.get('fearAndGreedIndex') or {}
                    if fim:
                        data['fear_greed'] = fim.get('value')
                        data['fear_greed_label'] = fim.get('label')
                    for comp in j.get('components', []):
                        name = comp.get('name', '').lower()
                        val = comp.get('value')
                        label = comp.get('label')
                        if 'market momentum' in name:
                            data['market_momentum'] = val; data['market_momentum_label']=label
                        elif 'stock price' in name:
                            data['stock_strength'] = val; data['stock_strength_label']=label
                        elif 'junk bond' in name:
                            data['junk_bond'] = val; data['junk_bond_label']=label
                        elif 'volatility' in name:
                            data['volatility'] = val; data['volatility_label']=label
                        elif 'put/call' in name or 'put call' in name:
                            data['put_call'] = val; data['put_call_label']=label
                        elif 'market breadth' in name or 'breadth' in name:
                            data['breadth'] = val; data['breadth_label']=label
                        elif 'safe haven' in name or 'safe-haven' in name:
                            data['safe_haven'] = val; data['safe_haven_label']=label
                    found = True
            except Exception:
                continue

        # If JSON parse didn't find data, try DOM scraping (fallback)
        if not found:
            # Attempt to find the main gauge value
            main = soup.find(lambda tag: tag.name in ('div','span') and tag.get_text(strip=True).endswith('%'))
            if main:
                txt = main.get_text(strip=True).replace('%','').strip()
                try:
                    data['fear_greed'] = int(txt)
                except:
                    pass

            # Try to extract component blocks by common labels on the page
            mapping = {
                'Market Momentum': 'market_momentum',
                'Stock Price Strength': 'stock_strength',
                'Junk Bond Demand': 'junk_bond',
                'Market Volatility': 'volatility',
                'Put/Call Ratio': 'put_call',
                'Market Breadth': 'breadth',
                'Safe Haven Demand': 'safe_haven'
            }
            for label, key in mapping.items():
                el = soup.find(string=lambda s: s and label in s)
                if el:
                    parent = el.find_parent()
                    if parent:
                        # find number nearby
                        num = parent.find(lambda t: t.name in ('div','span') and t.get_text(strip=True).replace('%','').isdigit())
                        if num:
                            try:
                                data[key] = int(num.get_text(strip=True).replace('%',''))
                            except:
                                pass

        return data

    except Exception as e:
        print(f"Error scraping: {e}")
        return None

def update_csv(data):
    """Update CSV file with new data"""
    csv_file = 'greed-index-data.csv'

    fieldnames = [
        'date',
        'timestamp',
        'fear_greed',
        'fear_greed_label',
        'market_momentum',
        'market_momentum_label',
        'stock_strength',
        'stock_strength_label',
        'junk_bond',
        'junk_bond_label',
        'volatility',
        'volatility_label',
        'put_call',
        'put_call_label',
        'breadth',
        'breadth_label',
        'safe_haven',
        'safe_haven_label'
    ]

    # Ensure all keys exist (avoid write errors)
    row = {k: data.get(k, '') for k in fieldnames}

    file_exists = os.path.isfile(csv_file)

    # Avoid duplicate entries for the same date
    if file_exists:
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            if len(lines) > 1 and lines[-1].startswith(row['date'] + ','):
                print("Today's entry already exists, skipping.")
                return

    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"Data updated: {row['date']}")

if __name__ == '__main__':
    data = scrape_greed_index()
    if data:
        update_csv(data)

from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
API_KEY = '3e244de1c2010e1e5c6711c3b61cb146'  # Replace with your actual API key

COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Australia", 
    "India", "Germany", "France", "Brazil", "Japan"
]

def get_serp_results(query, location="United States", language="en"):
    url = "http://api.serpstack.com/search"
    params = {
        'access_key': API_KEY,
        'query': query,
        'location': location,
        'language': language
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("organic_results", [])
    return []

def analyze_website(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            keywords = [meta.get('content') for meta in soup.find_all('meta', {'name': 'keywords'})]
            description = soup.find('meta', {'name': 'description'})
            description = description['content'] if description else "No description available"
            headings = {f"h{i}": [tag.get_text() for tag in soup.find_all(f"h{i}")] for i in range(1, 7)}
            backlinks = ["example.com/backlink1", "example.com/backlink2"]  # Mocked backlink data
            return {
                "keywords": keywords,
                "description": description,
                "headings": headings,
                "backlinks": backlinks
            }
        return {"error": "Unable to fetch page data"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html', countries=COUNTRIES)

@app.route('/api/analyze', methods=['GET'])
def analyze():
    keyword = request.args.get('keyword')
    location = request.args.get('location', "United States")  # Get location from query params
    if not keyword:
        return jsonify({"error": "No keyword provided"}), 400

    competitor_data = get_serp_results(keyword, location=location)
    if not competitor_data:
        return jsonify([])

    results = []
    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(analyze_website, item['url']): item for item in competitor_data}
        for future in future_to_url:
            item = future_to_url[future]
            try:
                analysis = future.result()
                results.append({
                    "position": item.get("position"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "description": item.get("snippet"),
                    "analysis": analysis
                })
            except Exception as e:
                results.append({
                    "position": item.get("position"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "description": item.get("snippet"),
                    "analysis": {"error": str(e)}
                })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

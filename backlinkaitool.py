from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

SERPAPI_KEY = "37897912aa59a0c6db9829c9e2fb5eb42a2cd24a6aa3862c780064dcc1593380"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI SEO Audit Tool – Thirupathi</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    body {
      font-family: 'Poppins', sans-serif;
      background: radial-gradient(circle at top left, #1e3a8a, #0f172a);
      color: #f8fafc;
      margin: 0;
      padding: 20px;
      min-height: 100vh;
      background-attachment: fixed;
    }
    h1 {
      text-align: center;
      color: #60a5fa;
      font-weight: 700;
      margin-top: 20px;
      letter-spacing: 1px;
    }
    form {
      text-align: center;
      margin: 40px auto;
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(12px);
      border-radius: 16px;
      padding: 25px;
      width: 80%;
      box-shadow: 0 0 25px rgba(255, 255, 255, 0.05);
    }
    input, button {
      padding: 12px 18px;
      font-size: 16px;
      margin: 10px;
      border-radius: 10px;
      border: none;
      outline: none;
      transition: 0.3s;
    }
    input {
      width: 45%;
      background: rgba(255, 255, 255, 0.12);
      color: #f1f5f9;
      border: 1px solid rgba(255,255,255,0.25);
      font-size: 17px;
      font-weight: 500;
      font-family: 'Poppins', sans-serif;
      letter-spacing: 0.5px;
      border-radius: 12px;
      padding: 14px 18px;
      transition: all 0.3s ease;
      box-shadow: inset 0 0 5px rgba(255,255,255,0.05);
    }
    input::placeholder {
      color: #cbd5e1;
      font-style: italic;
      opacity: 0.8;
    }
    input:focus {
      border-color: #60a5fa;
      box-shadow: 0 0 12px rgba(96,165,250,0.4);
      background: rgba(255,255,255,0.18);
    }
    button {
      background: linear-gradient(90deg, #2563eb, #1e40af);
      color: white;
      cursor: pointer;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    button:hover {
      transform: scale(1.05);
      box-shadow: 0 0 15px rgba(96,165,250,0.5);
    }
    .card {
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(14px);
      border-radius: 18px;
      padding: 35px;
      margin: 25px auto;
      width: 85%;
      box-shadow: 0 0 25px rgba(255,255,255,0.05);
      line-height: 1.8;
    }
    .green { color: #22c55e; font-weight: bold; }
    .red { color: #f87171; font-weight: bold; }
    .score { font-size: 24px; font-weight: bold; color: #60a5fa; }
    .rank { font-weight: bold; color: #22c55e; font-size: 20px; }
    .traffic { color: #38bdf8; font-weight: 600; }
    hr { border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 20px 0; }
    .recommendations {
      background: rgba(30,58,138,0.3);
      padding: 25px;
      border-left: 5px solid #60a5fa;
      border-radius: 12px;
      margin-top: 30px;
      box-shadow: 0 0 20px rgba(96,165,250,0.15);
    }
    .recommendations h3 {
      color: #93c5fd;
      margin-bottom: 10px;
    }
    .recommendations ul {
      margin: 0;
      padding-left: 20px;
    }
    .footer {
      text-align: center;
      margin-top: 50px;
      font-size: 14px;
      color: #94a3b8;
    }
    .footer span {
      color: #60a5fa;
    }
  </style>
</head>
<body>
  <h1>🌐 AI SEO Audit Tool by <span style="color:#93c5fd;">Thirupathi</span></h1>
  <form method="post">
    <input type="text" name="url" placeholder="Enter full URL (https://...)" required><br>
    <input type="text" name="keyword" placeholder="Enter keyword" required><br>
    <button type="submit">Run Audit 🚀</button>
  </form>

  {% if result %}
  <div class="card">
    <h2>🔍 SEO Audit Results</h2>
    <p><b>URL:</b> {{ result.url }}</p>
    <p><b>Keyword:</b> {{ result.keyword }}</p>
    <hr>
    <p><b>Title:</b> {{ result.title }}</p>
    <p>✅ Keyword in Title: <span class="{{ 'green' if result.keyword_in_title else 'red' }}">{{ result.keyword_in_title }}</span></p>
    <p>📏 Title Length: {{ result.title_length }} chars 
    {% if result.title_length <= 60 %}<span class="green">(Ideal)</span>{% else %}<span class="red">(Too long)</span>{% endif %}</p>
    <hr>
    <p><b>Meta Description:</b> {{ result.meta }}</p>
    <p>✅ Keyword in Meta: <span class="{{ 'green' if result.keyword_in_meta else 'red' }}">{{ result.keyword_in_meta }}</span></p>
    <p>📏 Meta Length: {{ result.meta_length }} chars 
    {% if result.meta_length <= 160 %}<span class="green">(Ideal)</span>{% else %}<span class="red">(Too long)</span>{% endif %}</p>
    <hr>
    <p><b>H1 Tag:</b> {{ result.h1 }}</p>
    <p>✅ Keyword in H1: <span class="{{ 'green' if result.keyword_in_h1 else 'red' }}">{{ result.keyword_in_h1 }}</span></p>
    <hr>
    <p><b>robots.txt Found:</b> {{ result.robots }}</p>
    <p><b>sitemap.xml Found:</b> {{ result.sitemap }}</p>
    <p><b>Missing Image Alts:</b> {{ result.missing_alts }}</p>
    <p><b>Internal Links Found:</b> {{ result.internal_links }}</p>
    <p><b>External Links Found:</b> {{ result.external_links }}</p>
    <p><b>Schema Found:</b> {{ result.schema }}</p>
    <hr>
    <p>📈 Google Rank: <span class="rank">{{ result.rank }}</span></p>
    <p class="traffic">{{ result.traffic }}</p>
    <p class="score">🏁 Final SEO Score: {{ result.score }}/100</p>

    <div class="recommendations">
      <h3>🧠 AI Thirupathi Recommendations</h3>
      <ul>
        <li>✅ Keep Title under <b>60 characters</b> for best display.</li>
        <li>✅ Maintain Meta Description between <b>155–160 characters</b>.</li>
        <li>✅ Add focus keyword naturally in Title, Meta, and H1.</li>
        <li>🖼 Add <b>alt text</b> to all images for accessibility.</li>
        <li>🔗 Increase internal links & fix any broken links.</li>
        <li>🤖 Make sure <b>robots.txt</b> and <b>sitemap.xml</b> are active.</li>
        <li>💡 Implement <b>structured data (schema)</b> for rich results.</li>
      </ul>
      <p style="margin-top:10px; color:#cbd5e1;">✨ <i>“SEO is about clarity — Help Google understand you better.” – <b>AI Thirupathi</b></i></p>
    </div>
  </div>
  {% endif %}

  <div class="footer">
    © 2025 <span>AI SEO Audit by Thirupathi</span> | Powered with ❤️ and Python
  </div>
</body>
</html>
"""

# ✅ New Function — Website Traffic Estimation (via SimilarWeb API)
def get_traffic_estimate(domain):
    try:
        api_url = f"https://data.similarweb.com/api/v1/data?domain={domain}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            visits = data.get('visits', None)
            if visits:
                return f"🌍 Estimated Monthly Traffic: {int(visits):,} visits"
            else:
                return "🌍 Traffic data not available"
        else:
            return "🌍 Unable to fetch traffic data"
    except Exception as e:
        return f"Error fetching traffic data: {e}"

def get_google_rank(keyword, url):
    try:
        serp_api = f"https://serpapi.com/search.json?q={keyword}&api_key={SERPAPI_KEY}&num=20"
        r = requests.get(serp_api, timeout=10).json()
        results = [res['link'] for res in r.get('organic_results', [])]
        for i, link in enumerate(results, start=1):
            if url in link:
                return f"#{i} in Google"
        return "Not in Top 20"
    except Exception as e:
        return f"Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        url = request.form['url'].strip()
        keyword = request.form['keyword'].strip().lower()

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')

            title = soup.title.string.strip() if soup.title else ''
            title = ' '.join(title.split())
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            meta = meta_tag['content'] if meta_tag and meta_tag.get('content') else ''
            h1_tag = soup.find('h1')
            h1 = h1_tag.text.strip() if h1_tag else 'None'

            keyword_in_title = keyword in title.lower()
            keyword_in_meta = keyword in meta.lower()
            keyword_in_h1 = keyword in h1.lower()

            robots = requests.get(url.rstrip('/') + '/robots.txt').status_code == 200
            sitemap = requests.get(url.rstrip('/') + '/sitemap.xml').status_code == 200
            missing_alts = len([img for img in soup.find_all('img') if not img.get('alt')])

            parsed_domain = urlparse(url).netloc
            internal_found = False
            external_found = False

            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                if urlparse(link).netloc == parsed_domain:
                    internal_found = True
                elif "http" in link:
                    external_found = True

            internal_links = "Found ✅" if internal_found else "Not Found ❌"
            external_links = "Found ✅" if external_found else "Not Found ❌"

            schema = bool(soup.find('script', type='application/ld+json'))
            rank = get_google_rank(keyword, url)

            # ✅ Traffic Data
            domain = urlparse(url).netloc
            traffic_info = get_traffic_estimate(domain)

            score = 0
            if keyword_in_title: score += 15
            if keyword_in_meta: score += 10
            if keyword_in_h1: score += 10
            if robots: score += 10
            if sitemap: score += 10
            if schema: score += 10
            if internal_found: score += 15
            if external_found: score += 10
            if missing_alts == 0: score += 10

            result = {
                "url": url,
                "keyword": keyword,
                "title": title,
                "title_length": len(title),
                "keyword_in_title": keyword_in_title,
                "meta": meta,
                "meta_length": len(meta),
                "keyword_in_meta": keyword_in_meta,
                "h1": h1,
                "keyword_in_h1": keyword_in_h1,
                "robots": robots,
                "sitemap": sitemap,
                "missing_alts": missing_alts,
                "internal_links": internal_links,
                "external_links": external_links,
                "schema": schema,
                "rank": rank,
                "traffic": traffic_info,
                "score": score
            }

        except Exception as e:
            result = {"error": str(e)}

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(debug=True)

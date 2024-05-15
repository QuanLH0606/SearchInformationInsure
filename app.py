from flask import Flask, render_template, request
from googlesearch import search
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title').text if soup.find('title') else 'No title found'
        
        # Tìm tất cả các đoạn văn bản từ thẻ <p> và không thuộc footer
        paragraphs = soup.find_all(lambda tag: tag.name == 'p' and not tag.find_parents('footer'))
        # Trích xuất nội dung từ các đoạn văn bản
        content = "\n".join([para.text for para in paragraphs if para.text.strip()])  # Bỏ qua các đoạn trống
        
        return title, content
    except requests.RequestException as e:
        return "Error", str(e)

def calculate_relevance(query, title, content):
    query_words = query.lower().split()
    title_score = sum([1 for word in query_words if word in title.lower()])
    content_score = sum([1 for word in query_words if word in content.lower()])
    return title_score + content_score

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_query():
    query = request.form['query']
    try:
        results = search(query, lang="vi", num_results=2)
        
        best_result = None
        best_score = -1
        
        for result in results:
            if result:
                title, content = extract_info(result)
                if title != "Error":
                    score = calculate_relevance(query, title, content)
                    if score > best_score:
                        best_score = score
                        best_result = (result, title, content)
        
        if best_result:
            url, title, content = best_result
            return f"<p>{content}</p>"
        else:
            return "<p>No relevant results found.</p>"
    except StopIteration:
        return "<p>No results found.</p>"
    except Exception as e:
        return f"<p>An error occurred: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True, port=5001)

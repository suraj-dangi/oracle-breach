#!/usr/bin/env python3
"""
Flask web application for checking domains against the Oracle breach database.
This application searches a database of allegedly leaked domains from the Oracle breach
to determine if a company domain was potentially affected.

Includes logging of all searches to track usage and hits.
"""
from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Set up logging
LOG_DIR = './data/logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Configure application logger
app.logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'app.log'),
    maxBytes=10485760,  # 10MB
    backupCount=10
)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Configure search hits logger
search_logger = logging.getLogger('search_hits')
search_logger.setLevel(logging.INFO)
hits_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'search_hits.log'),
    maxBytes=10485760,  # 10MB
    backupCount=10
)
hits_handler.setFormatter(formatter)
search_logger.addHandler(hits_handler)

# Database path
DB_PATH = './data/oracle_breach.db'


# Route for home page
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


# Route for search functionality
@app.route('/search', methods=['POST'])
def search():
    domain = request.form.get('domain', '').strip().lower()
    client_ip = request.remote_addr
    search_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not domain:
        app.logger.warning(f"Empty search from {client_ip}")
        return jsonify({"error": "Please enter a domain"}), 400

    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Search for exact match
        cursor.execute("SELECT domain FROM breached_domains WHERE domain = ?", (domain,))
        exact_match = cursor.fetchone()

        # Search for partial matches
        cursor.execute("SELECT domain FROM breached_domains WHERE domain LIKE ?", (f"%{domain}%",))
        partial_matches = [row[0] for row in cursor.fetchall() if row[0] != domain]

        conn.close()

        # Log the search and result
        if exact_match:
            log_message = f"HIT - {client_ip} - '{domain}' - FOUND IN BREACH LIST"
            search_logger.info(log_message)
            app.logger.info(log_message)

            return jsonify({
                "found": True,
                "message": f"WARNING: {domain} was found in the alleged Oracle breach list!",
                "partial_matches": partial_matches
            })
        else:
            partial_hit = "with partial matches" if partial_matches else "no partial matches"
            log_message = f"MISS - {client_ip} - '{domain}' - NOT FOUND ({partial_hit})"
            app.logger.info(log_message)

            return jsonify({
                "found": False,
                "message": f"Good news! {domain} was not found in the alleged Oracle breach list.",
                "partial_matches": partial_matches
            })

    except Exception as e:
        error_message = f"ERROR - {client_ip} - '{domain}' - {str(e)}"
        app.logger.error(error_message)
        return jsonify({"error": f"Database error: {str(e)}"}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check if database exists and is accessible
        if not os.path.exists(DB_PATH):
            app.logger.error("Health check failed: Database not found")
            return jsonify({"status": "error", "message": "Database not found"}), 503

        # Try to connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM breached_domains")
        count = cursor.fetchone()[0]
        conn.close()

        # Check log directory
        log_files = os.listdir(LOG_DIR)

        app.logger.info(f"Health check: OK. Database has {count} domains. Log files: {len(log_files)}")
        return jsonify({
            "status": "healthy",
            "domains_count": count,
            "logs": log_files
        })

    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 503


# Log statistics endpoint
@app.route('/stats', methods=['GET'])
def stats():
    try:
        # Get total number of domains in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM breached_domains")
        total_domains = cursor.fetchone()[0]

        # Count total search queries in log
        hits_count = 0
        miss_count = 0
        total_searches = 0

        log_path = os.path.join(LOG_DIR, 'app.log')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                for line in f:
                    if " - HIT - " in line:
                        hits_count += 1
                    elif " - MISS - " in line:
                        miss_count += 1

        total_searches = hits_count + miss_count
        hit_ratio = hits_count / total_searches if total_searches > 0 else 0

        return jsonify({
            "total_domains": total_domains,
            "total_searches": total_searches,
            "hits": hits_count,
            "misses": miss_count,
            "hit_ratio": f"{hit_ratio:.2%}"
        })

    except Exception as e:
        app.logger.error(f"Stats endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Ensure templates directory exists
    os.makedirs('templates', exist_ok=True)

    # Create index.html if it doesn't exist
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Oracle Breach Domain Search</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
        }
        .search-box {
            margin: 20px 0;
        }
        input[type="text"] {
            padding: 10px;
            width: 70%;
            font-size: 16px;
        }
        button {
            padding: 10px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
        }
        .warning {
            background-color: #f8d7da;
            color: #721c24;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .partial-matches {
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <h1>Oracle Breach Domain Search</h1>
    <p>Enter a domain name to check if it appears in the alleged Oracle breach list.</p>

    <div class="search-box">
        <input type="text" id="domain-input" placeholder="Enter domain (e.g. example.com)">
        <button onclick="searchDomain()">Check</button>
    </div>

    <script>
        function searchDomain() {
            const domain = document.getElementById('domain-input').value.trim();
            if (!domain) {
                alert('Please enter a domain');
                return;
            }

            // Send request to server
            fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `domain=${encodeURIComponent(domain)}`
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';

                if (data.error) {
                    resultDiv.className = 'result warning';
                    resultDiv.innerHTML = `<strong>Error: ${data.error}</strong>`;
                    return;
                }

                if (data.found) {
                    resultDiv.className = 'result warning';
                    resultDiv.innerHTML = `<strong>${data.message}</strong>`;
                } else {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `<strong>${data.message}</strong>`;
                }

                // Show partial matches if any
                if (data.partial_matches && data.partial_matches.length > 0) {
                    let partialMatchesHtml = '<div class="partial-matches"><p>Similar domains found in the database:</p><ul>';
                    data.partial_matches.forEach(match => {
                        partialMatchesHtml += `<li>${match}</li>`;
                    });
                    partialMatchesHtml += '</ul></div>';
                    resultDiv.innerHTML += partialMatchesHtml;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        }

        // Allow Enter key to trigger search
        document.getElementById('domain-input').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                searchDomain();
            }
        });
    </script>
</body>
</html>
            ''')

    # Run the application
    app.run(host='0.0.0.0', port=5002)
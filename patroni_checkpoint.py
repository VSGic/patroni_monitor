import requests
from flask import Flask, jsonify, render_template
from datetime import datetime
from collections import OrderedDict

# Replace with the actual Patroni metrics endpoint
PATRONI_METRICS_URL = 'http://<<your patroni ip or host>>:8008/metrics'

app = Flask(__name__)

def fetch_metrics(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_metrics(metrics):
    result = {}
    lines = metrics.split('\n')
    for line in lines:
        if line.startswith('patroni_postgres_running'):
            parts = line.split()
            key = parts[0]
            value = parts[1]
            result['patroni_postgres_running'] = int(value)
        elif line.startswith('patroni_xlog_replayed_timestamp'):
            parts = line.split()
            key = parts[0]
            value = parts[1]
            result['patroni_xlog_replayed_timestamp'] = float(value)
    return result

def convert_timestamp(timestamp):
    ts = float(timestamp)
    human_readable = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return human_readable

@app.route('/checkpoint', methods=['GET'])
def checkpoint():
    try:
        metrics = fetch_metrics(PATRONI_METRICS_URL)
        parsed_metrics = parse_metrics(metrics)

        response = OrderedDict()

        if 'patroni_postgres_running' in parsed_metrics:
            response["patroni_postgres_running"] = parsed_metrics['patroni_postgres_running']
            if response["patroni_postgres_running"] == 1:
              response["patroni_postgres_running"] = "Yes"
            else:
              response["patroni_postgres_running"] = "No"

        if 'patroni_xlog_replayed_timestamp' in parsed_metrics:
            timestamp = parsed_metrics['patroni_xlog_replayed_timestamp']
            human_readable_timestamp = convert_timestamp(timestamp)
            response["patroni_xlog_replayed_timestamp"] = timestamp
            response["patroni_xlog_replayed_timestamp_human_readable"] = human_readable_timestamp

        return render_template('checkpoint.html', **response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5077)

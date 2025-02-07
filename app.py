from flask import Flask, jsonify, render_template
import subprocess
import os
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)
battery_reports = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-report')
def generate_report():
    report_path = os.path.expanduser("~/Desktop/battery-report.html")
    subprocess.run(["powercfg", "/batteryreport", "/output", report_path], shell=True)
    
    with open(report_path, 'r', encoding='utf-8') as file:
        report_content = file.read()
    
    # Parse battery health info
    soup = BeautifulSoup(report_content, 'html.parser')
    battery_info = {}
    for table in soup.find_all('table'):
        if 'CAPACITY' in table.get_text():
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if 'DESIGN CAPACITY' in key or 'FULL CHARGE CAPACITY' in key:
                        battery_info[key] = value

    report = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'content': report_content,
        'battery_info': battery_info
    }
    battery_reports.append(report)
    
    return jsonify({"message": "Battery report generated successfully!", "index": len(battery_reports) - 1})

@app.route('/view-report/<int:index>')
def view_report(index):
    if 0 <= index < len(battery_reports):
        return battery_reports[index]['content']
    return "Report not found", 404

@app.route('/get-battery-health/<int:index>')
def get_battery_health(index):
    if 0 <= index < len(battery_reports):
        battery_info = battery_reports[index]['battery_info']
        
        try:
            design_capacity = float(battery_info['DESIGN CAPACITY'].replace(',', '').replace(' mWh', ''))
            full_charge = float(battery_info['FULL CHARGE CAPACITY'].replace(',', '').replace(' mWh', ''))
            health_percentage = round((full_charge / design_capacity) * 100, 2)
            battery_info['HEALTH_PERCENTAGE'] = health_percentage
        except (KeyError, ValueError):
            battery_info['HEALTH_PERCENTAGE'] = None
            
        return jsonify(battery_info)
    return "Report not found", 404

@app.route('/list-reports')
def list_reports():
    return jsonify([{'index': i, 'timestamp': report['timestamp']} 
                   for i, report in enumerate(battery_reports)])

if __name__ == '__main__':
    app.run(port=5000, debug=True)

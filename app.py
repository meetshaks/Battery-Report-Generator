from flask import Flask, send_file, render_template # type: ignore
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-report')
def generate_report():
    report_path = os.path.expanduser("~/Desktop/battery-report.html")
    
    # Run the powercfg command
    subprocess.run(["powercfg", "/batteryreport", "/output", report_path], shell=True)
    
    return "Battery report generated successfully!"

@app.route('/view-report')
def view_report():
    report_path = os.path.expanduser("~/Desktop/battery-report.html")
    
    if os.path.exists(report_path):
        return send_file(report_path)
    else:
        return "No report found. Please generate one first.", 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)

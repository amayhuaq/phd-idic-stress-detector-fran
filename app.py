import pandas as pd
import numpy as np
from flask import *
import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from StressDetector import StressDetector

UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')

# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)

# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'This is your secret key to utilize session in Flask'


def process_from_csv(filename, freq, processed_data_file_path):
    WIN_SIZE = 3 * freq * 60   # 720 3 mins x 4 samples x 60 seconds
    samples_per_minute = freq * 60
    detector = StressDetector(3, samples_per_minute)
    df_data = pd.read_csv(filename, header=None)
    eda_data_raw = df_data[0].tolist()
    last_val = len(eda_data_raw) // WIN_SIZE
    eda_data = eda_data_raw[0:(last_val * WIN_SIZE)]

    detector.process_gsr(eda_data)
    stress_levels = detector.get_sax_values()
    stress_levels = np.repeat(stress_levels, WIN_SIZE)

    df = pd.DataFrame(stress_levels)
    df.to_csv(processed_data_file_path, header=None, index=None)


@app.route('/', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        # upload file flask
        samples_per_sec = int(request.form.get("freq"))
        f = request.files.get('file')

        # Extracting uploaded file name
        data_filename = secure_filename(f.filename)

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))

        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
        session['processed_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], "stress_levels.csv")

        if samples_per_sec > 0:
            process_from_csv(session['uploaded_data_file_path'], samples_per_sec, session['processed_data_file_path'])
            return render_template("index.html", msg="Processed file")
        else:
            return render_template("index.html", msg="Missing number of samples per second")

    return render_template("index.html", msg="")


@app.route('/show_data')
def showData():
    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)
    # read csv
    uploaded_df = pd.read_csv(data_file_path,
                              encoding='unicode_escape')
    # Converting to html Table
    uploaded_df_html = uploaded_df.to_html()
    return render_template('show_graph.html',
                           data_var=uploaded_df_html)


@app.route('/download_processed')
def download_csv():
    data_file_path = session.get('processed_data_file_path', None)
    return send_file(data_file_path, as_attachment=True, download_name="stress_levels.csv")


if __name__ == '__main__':
    app.run(debug=True)

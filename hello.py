from flask import Flask, request, jsonify, abort, redirect, url_for, render_template, send_file
import numpy as np
from sklearn.externals import joblib
import pandas as pd



app = Flask(__name__)
knn = joblib.load('knn.joblib')

@app.route('/')
def hello_world():
    return 'Hello, yaz!!!!!!!'

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

@app.route('/avg/<nums>')
def avg(nums):
    nums = nums.split(',')
    nums = [float(num) for num in nums]
    print(nums)
    return str(mean(nums))

@app.route('/iris/<param>')
def iris(param):
    param = param.split(',')
    param = [float(num) for num in param]
    param = np.array(param).reshape(1, -1)
    predict = knn.predict(param)
    return str(predict)

@app.route('/badrequest400')
def bad_request():
    return abort(400)


@app.route('/show_image')
def show_image():
    return '<img src="/static/setosa.jpg" alt="setosa">'


@app.route('/iris_post', methods=['POST'])
def iris_post():
    try:
        content = request.get_json()
        param = content['flower'].split(',')
        param = [float(num) for num in param]
        param = np.array(param).reshape(1, -1)
        predict = knn.predict(param)
        predict = {'class':str(predict[0])}
    except:
        return redirect(url_for('bad_request'))
    return jsonify(predict)

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired

from werkzeug.utils import secure_filename
import os

class MyForm(FlaskForm):
    name = StringField('name')
    file = FileField()

@app.route('/submit', methods=('GET', 'POST'))
def submit():
    form = MyForm()
    if form.validate_on_submit():

        f = form.file.data
        filename = form.name.data + '.csv'
        # filename = form.text.data + '.txt'
        # f.save(os.path.join(
        #     filename
        # ))

        df = pd.read_csv(f, header=None)

        predict = knn.predict(df)
        print(predict)
        result = pd.DataFrame(predict)
        result.to_csv(filename, index=False)

        return send_file(filename,
                     mimetype='text/csv',
                     attachment_filename=filename,
                     as_attachment=True)

    return render_template('submit.html', form=form)

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename + 'uploaded')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'file uploaded'
    
    return '''
    <!doctype html>
    <title>Upload new File2</title>
    <h1>Upload new File2</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
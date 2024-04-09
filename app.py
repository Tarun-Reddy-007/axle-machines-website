from flask import Flask, render_template, request, jsonify, redirect, session, send_file
import os
from datetime import datetime
import pandas as pd
from fuzzywuzzy import process
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import shutil
import json
import calendar
matplotlib.use('Agg')
import numpy as np
import secrets
from flask_mysqldb import MySQL
import re
from PyPDF2 import PdfReader
import zipfile
import hashlib
import random
import smtplib

def processor(skills,count,file_path, cdt):

    def convert_folder_to_zip(folder_path):
        parent_directory = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        zip_path = os.path.join(parent_directory, f"{folder_name}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

    def remove_dots_from_file_names(folder_path):
        files = os.listdir(folder_path)
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            file_name_no_ext, file_extension = os.path.splitext(file_name)
            new_file_name = file_name_no_ext.replace(".", "")
            new_file_name_with_ext = new_file_name + file_extension
            new_file_path = os.path.join(folder_path, new_file_name_with_ext)
            os.rename(file_path, new_file_path)

    def copy_file(source_file, destination_directory):
        shutil.copy(source_file, destination_directory)

    def create_folder(directory, folder_name):
        folder_path = os.path.join(directory, folder_name)
        os.makedirs(folder_path)

    def unzip_file(filex_path, extract_path):
        with zipfile.ZipFile(filex_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
    directory_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'
    folder_name = 'filtered'+str(count)

    directory_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'filtered'+str(count)+cdt+'/'
    for sk in skills:
        create_folder(directory_path, sk)

    create_folder('D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/', 'filtered'+str(count)+cdt)

    zip_file_path = file_path
    extract_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'filtered'+str(count)+cdt
    unzip_file(zip_file_path, extract_directory)

    directory_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/'
    folder_name = 'txt files'
    create_folder(directory_path, folder_name)

    ukfolder = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'filtered'+str(count)+cdt
    directories = next(os.walk(ukfolder))[1]
    unknown_folder_name = directories[0]
    

    folder_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'filtered'+str(count)+cdt+'/'+unknown_folder_name
    remove_dots_from_file_names(folder_path)

    files_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'filtered'+str(count)+cdt+'/'+unknown_folder_name
    txt_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/txt files'

    for filename in os.listdir(files_directory):

        if filename.endswith(".pdf"):
            file_path = os.path.join(files_directory, filename)
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(txt_directory, txt_filename)
            with open(file_path, "rb") as file:
                pdf_reader = PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text_content)
        else:
            print("Folder contains file formats other than pdf which were ignored in the process.")

    txt_directory = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/txt files'
    for filename in os.listdir(txt_directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(txt_directory, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                words = content.split()

                wordsl=[]
                for i in words:
                    l=i.lower()
                    wordsl.append(l)

                for sk in skills:
                    if sk in wordsl:
                        li= filename.split(".")
                        li[1]="pdf"
                        filename=".".join(li)
                        pdf_path = os.path.join('D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'filtered'+str(count)+cdt+'/'+unknown_folder_name, filename)
                        destination_directory=os.path.join('D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'filtered'+str(count)+cdt,sk)
                        copy_file(pdf_path, destination_directory)

    shutil.rmtree('D:/axlemachineswebsite frontend/html and flask/static/resumes/txt files')
    shutil.rmtree('D:/axlemachineswebsite frontend/html and flask/static/resumes/Uploads/'+'filtered'+str(count)+cdt)

    folder_path = 'D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'filtered'+str(count)+cdt
    convert_folder_to_zip(folder_path)
    shutil.rmtree('D:/axlemachineswebsite frontend/html and flask/static/resumes/filters/'+'filtered'+str(count)+cdt)


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Tarun@1511'
app.config['MYSQL_DB'] = 'axlemachineswebsite'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

app.secret_key = secrets.token_hex(16)  

uploaded_dataset = None

@app.route('/')
def index():
    return render_template('Home.html')

def is_valid_email(email):
    email_pattern = re.compile(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        first_name = userDetails['first_name']
        last_name = userDetails['last_name']
        email = userDetails['email']
        password = userDetails['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as count FROM users WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()

        if result['count']>0:
            error_message = 'Email ID Exists. Please sign in.'
            return render_template('Login.html', error_messageup=error_message, right_panel_active=True)
        elif not is_valid_password(password):
            error_message = 'Invalid Password.'
            return render_template('Login.html', error_messageup=error_message, right_panel_active=True)
        else:
            hashed_password = hash_password(password)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users(first_name, last_name, email, pass) VALUES(%s, %s, %s, %s)", (first_name, last_name, email, hashed_password))
            mysql.connection.commit()
            cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            user_id = cur.fetchone()['user_id']
            cur.close()
            session['user_id'] = user_id
            return render_template('Home.html')
    else:
        return render_template('Login.html')

def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password[:254]

def verify_password(plain_text_password, hashed_password):
    return hash_password(plain_text_password) == hashed_password

def is_valid_password(password):
    if len(password) < 8:
        return False
    has_number = any(char.isdigit() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_special = any(char in '!@#$%^&*()-_+=~`[]{}|;:,.<>?/ ' for char in password)
    return has_number and has_upper and has_special
    
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        
        if user and verify_password(password, user['pass']):
            session['user_id'] = user['user_id']
            return redirect('Home.html')
        else:
            error_msg = 'Incorrect Email ID or password. Please try again.'
            return render_template('Login.html', error_msg=error_msg)
    else:
        return render_template('Login.html')
    
@app.route('/signout', methods=['GET', 'POST'])
def signout():
    session.pop('user_id', None)
    return render_template('Home.html')
    
@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['text']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contact_us (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
        mysql.connection.commit()
        cur.close()
        return render_template('Aboutus.html')

@app.route('/Home.html')
def home():
    return render_template('Home.html')

@app.route('/Projects.html')
def projects():
    return render_template('Projects.html')

@app.route('/Services.html')
def services():
    return render_template('Services.html')

@app.route('/Tools.html')
def tools():
    return render_template('Tools.html')

@app.route('/Aboutus.html')
def aboutus():
    return render_template('Aboutus.html')

@app.route('/Login.html')
def login():
    return render_template('Login.html')

#@app.route('/Profile.html')
#def profile():
 #   if 'user_id' in session:
  #      user_id = session['user_id']
  #      cursor = mysql.connection.cursor()
   #     cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    #    user_data = cursor.fetchone()
     #   return render_template('Profile.html', user_data=user_data)
    #else:
     #   return render_template('Login.html')

@app.route('/arft.html')
def arft():
    if 'user_id' not in session:
        return render_template('Login.html')
    return render_template('arft.html')

@app.route('/dashboard.html')
def dashboard():
    if 'user_id' not in session:
        return render_template('Login.html')
    return render_template('dashboard.html')

current_date_with_ms = datetime.now()
current_date= current_date_with_ms.strftime("%Y-%m-%d %H:%M:%S.%f")
date_string = ''.join(c for c in current_date if c.isdigit())
directory_path = os.path.join('static','plots', date_string)
os.makedirs(os.path.join('static','plots', date_string))

@app.route('/uploadresume', methods=['POST'])
def upload_resume():
    file = request.files['file']
    user_id = session.get('user_id')
    uploads_folder = os.path.join(app.root_path,'static','resumes', 'uploads')
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)
    file_path = os.path.join(uploads_folder, f'upload_{user_id}_{date_string}.zip')
    file.save(file_path)
    skills = request.form.getlist('skills[]')
    processor(skills, user_id, file_path, date_string)
    zip_file_path = os.path.join(app.root_path, 'static', 'resumes', 'filters', f'filtered{user_id}{date_string}.zip')
    return send_file(zip_file_path, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'})
    if file:
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_' + file.filename
        dataset_path = os.path.join('datasets', filename)
        file.save(dataset_path)

        if filename.endswith('.csv'):
            df = pd.read_csv(dataset_path)
        elif filename.endswith('.xlsx'):
            try:
                df = pd.read_excel(dataset_path)
            except Exception as e:
                return jsonify({'message': 'Error reading Excel file: ' + str(e)})
        else:
            return jsonify({'message': 'Unsupported file format'})

        df_pro = df.copy()

        date_columns = [col for col in df_pro.columns if 'date' in col.lower()]

        if date_columns:
            for col in date_columns:
                df_pro[col] = pd.to_datetime(df_pro[col])

                df_pro['day'] = df_pro[col].dt.day
                df_pro['month'] = df_pro[col].dt.month
                df_pro['year'] = df_pro[col].dt.year
        
        object_columns = df_pro.select_dtypes(include=['object']).columns
        for col in object_columns:
            if 'date' not in col.lower():
                unique_values_ratio = df_pro[col].nunique() / len(df_pro)
                if unique_values_ratio > 0.7:
                    del df_pro[col]

        global uploaded_dataset
        uploaded_dataset = df_pro

        table_html = df.to_html(classes='data', header='true', index=False)

        columns = df.columns.tolist()
        rows = len(df)
        num_columns = len(columns)
        missing = df.isnull().sum()
        missing_dict = missing.to_dict()

        missing_dict = {key: value for key, value in missing_dict.items() if value != 0}

        if len(missing_dict) == 0:
            return jsonify({'message': 'File uploaded successfully', 'table_html': table_html, 'num_columns': num_columns, 'columns': columns, 'rows': rows, 'missing': "There are no missing values in the dataset"})
        else:
            return jsonify({'message': 'File uploaded successfully', 'table_html': table_html, 'num_columns': num_columns, 'columns': columns, 'rows': rows, 'missing': missing_dict})


@app.route('/process_message', methods=['POST'])
def process_message():
    global uploaded_dataset

    if uploaded_dataset is None:
        return jsonify({'response': 'Please upload a dataset first.'})

    data = request.get_json()
    message = data['message'].lower()
    message_lower=message.lower()
    summary_keywords = ['summary', 'overview', 'describe']
    summary_match, summary_score = process.extractOne(message_lower, summary_keywords)
    plot_keywords = ['plot', 'create', 'show', 'visualize', 'generate', 'display']
    plot_match, plot_score = process.extractOne(message_lower, plot_keywords)
    compare_keywords = ['compare','comparison' ]
    compare_match, compare_score = process.extractOne(message_lower, compare_keywords)
    if summary_score >= 60 and summary_score > plot_score and summary_score > compare_score:
        matched_column = find_matched_column(message_lower)

        if matched_column:
            if "date" in matched_column.lower():
                oldest_date = uploaded_dataset[matched_column].min().strftime('%Y-%m-%d')
                latest_date = uploaded_dataset[matched_column].max().strftime('%Y-%m-%d')
                day_value_counts = uploaded_dataset['day'].value_counts()
                most_frequent_day = day_value_counts.idxmax()
                least_frequent_day = day_value_counts.idxmin()
                month_value_counts = uploaded_dataset['month'].value_counts()
                most_frequent_month = calendar.month_name[month_value_counts.idxmax()]
                least_frequent_month = calendar.month_name[month_value_counts.idxmin()]
                year_value_counts = uploaded_dataset['year'].value_counts()
                most_frequent_year = year_value_counts.idxmax()
                least_frequent_year = year_value_counts.idxmin()
                response = f'The data is recorded from : {oldest_date} to {latest_date}.\n Most frequent year : {most_frequent_year}\n Least Frequent year : {least_frequent_year}\n Most frequent month : {most_frequent_month}\n Least Frequent month : {least_frequent_month}\n Most frequent day/date : {most_frequent_day}\n Least Frequent day/date : {least_frequent_day}'
                
            else:
                column_type = uploaded_dataset[matched_column].dtype
                if column_type in ['int64', 'float64']:
                    unique_values_count = uploaded_dataset[matched_column].nunique()
                    if unique_values_count < 12:
                        value_counts = uploaded_dataset[matched_column].value_counts()
                        response = f'Value counts for {matched_column}:\n\n'
                        for value, count in value_counts.items():
                            response += f'{value}: {count}\n'
                    else:
                        average = round(uploaded_dataset[matched_column].mean(),2)
                        maximum = uploaded_dataset[matched_column].max()
                        minimum = uploaded_dataset[matched_column].min()
                        response = f'Average of {matched_column}: {average}\n Minimum of {matched_column}: {minimum}\n maximum of {matched_column}: {maximum}'

                elif column_type == 'object':
                    value_counts = uploaded_dataset[matched_column].value_counts()
                    response = f'Value counts for {matched_column}:\n\n'
                    for value, count in value_counts.items():
                        response += f'{value}: {count}\n'
                else:
                    response = 'Summary not available for this column type.'
        else:
            response = 'Column not found in the query.'

        return jsonify({'response': response})

    elif plot_score >= 60 and plot_score > summary_score and compare_score<=80:
        single_variable_plots = ['histograms', 'pie', 'violin', 'area', 'bar', 'stack']
        double_variable_plots = ['line', 'scatter', 'box', 'pair', 'heatmaps', 'joint', 'facet']
        message_lower = message.lower()
        single_variable_match, single_variable_score = process.extractOne(message, single_variable_plots)
        double_variable_match, double_variable_score = process.extractOne(message, double_variable_plots)
        if single_variable_score >= 60 and single_variable_score>double_variable_score:
            matched_column = find_matched_column(message_lower)
            if matched_column:
                if 'histograms' == single_variable_match:
                    sns.histplot(uploaded_dataset[matched_column])
                    plt.title(f'Histogram of {matched_column}')
                    plt.xlabel(matched_column)
                    plt.ylabel('Frequency')
                    plt.savefig(f'static/plots/{date_string}/plot.png')
                    plt.close()
                    return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'pie' == single_variable_match:
                    plt.pie(uploaded_dataset[matched_column].value_counts(), labels=uploaded_dataset[matched_column].unique(), autopct='%1.1f%%')
                    plt.title(f'Pie chart of {matched_column}')
                    plt.savefig(f'static/plots/{date_string}/plot.png')
                    plt.close()
                    return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'violin'== single_variable_match:
                    sns.violinplot(data=uploaded_dataset, y=matched_column)
                    plt.title(f'Violin plot of {matched_column}')
                    plt.ylabel(matched_column)
                    plt.savefig(f'static/plots/{date_string}/plot.png')
                    plt.close()
                    return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'area' == single_variable_match:
                    uploaded_dataset[matched_column].value_counts().sort_index().plot.area()
                    plt.title(f'Area plot of {matched_column}')
                    plt.xlabel(matched_column)
                    plt.ylabel('Frequency')
                    plt.savefig(f'static/plots/{date_string}/plot.png')
                    plt.close()
                    return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'stack' == single_variable_match:
                    uploaded_dataset[matched_column].value_counts().sort_index().plot.area(stacked=True)
                    plt.title(f'Stack plot of {matched_column}')
                    plt.xlabel(matched_column)
                    plt.ylabel('Frequency')
                    plt.tight_layout()
                    plt.savefig(f'static/plots/{date_string}/plot.png')
                    plt.close()
                    return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'bar' == single_variable_match:
                    value_counts = uploaded_dataset[matched_column].value_counts()
                    value_counts.plot(kind='bar')
                    plt.title(f'Bar plot {matched_column}')
                    plt.xlabel(matched_column)
                    plt.ylabel(f"Value Counts for {matched_column}")
                    plt.savefig(f'static/plots/{date_string}/plot.png')
                    plt.close()
                    return jsonify({'response': f"static/plots/{date_string}/plot.png"})
            else:
                return jsonify({'response': 'Column not found for plotting.'})
            
        elif double_variable_score >= 60 and double_variable_score >= single_variable_score:
            columns = find_matched_columns(message_lower)
            if columns:
                if 'line' == double_variable_match:
                    if(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                        sns.lineplot(data=uploaded_dataset, x=columns[1], y=columns[0])
                        plt.title(f'Line plot of {columns[1]} and {columns[0]}')
                        plt.xlabel(columns[1])
                        plt.ylabel(columns[0])
                        plt.tight_layout()
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    else:
                        sns.lineplot(data=uploaded_dataset, x=columns[0], y=columns[1])
                        plt.title(f'Line plot of {columns[0]} and {columns[1]}')
                        plt.xlabel(columns[0])
                        plt.ylabel(columns[1])
                        plt.tight_layout()
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    
                elif 'scatter' == double_variable_match:
                    if(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                        sns.scatterplot(data=uploaded_dataset, x=columns[1], y=columns[0])
                        plt.title(f'Scatter plot of {columns[1]} and {columns[0]}')
                        plt.xlabel(columns[1])
                        plt.ylabel(columns[0])
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    else:
                        sns.scatterplot(data=uploaded_dataset, x=columns[0], y=columns[1])
                        plt.title(f'Scatter plot of {columns[0]} and {columns[1]}')
                        plt.xlabel(columns[0])
                        plt.ylabel(columns[1])
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    
                elif 'box' == double_variable_match:
                    if(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                        sns.boxplot(data=uploaded_dataset, x=columns[1], y=columns[0])
                        plt.title(f'Box plot of {columns[1]} and {columns[0]}')
                        plt.xlabel(columns[1])
                        plt.ylabel(columns[0])
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    else:
                        sns.boxplot(data=uploaded_dataset, x=columns[0], y=columns[1])
                        plt.title(f'Box plot of {columns[0]} and {columns[1]}')
                        plt.xlabel(columns[0])
                        plt.ylabel(columns[1])
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'pair' == double_variable_match:
                    if(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                        sns.pairplot(uploaded_dataset[[columns[1], columns[0]]])
                        plt.title(f'Pair plot of {columns[1]} and {columns[0]}')
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    else:
                        sns.pairplot(uploaded_dataset[[columns[0], columns[1]]])
                        plt.title(f'Pair plot of {columns[0]} and {columns[1]}')
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'heatmaps' == double_variable_match:
                    if(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                        pivot_table = uploaded_dataset.pivot_table(index=columns[1], columns=columns[0], aggfunc=len)
                        sns.heatmap(pivot_table, cmap="YlGnBu")
                        plt.title(f'Heatmap of {columns[1]} and {columns[0]}')
                        plt.xlabel(columns[1])
                        plt.ylabel(columns[0])
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    else:
                        pivot_table = uploaded_dataset.pivot_table(index=columns[0], columns=columns[1], aggfunc=len)
                        sns.heatmap(pivot_table, cmap="YlGnBu")
                        plt.title(f'Heatmap of {columns[0]} and {columns[1]}')
                        plt.xlabel(columns[0])
                        plt.ylabel(columns[1])
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'joint' == double_variable_match:
                    if(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                        sns.jointplot(data=uploaded_dataset, x=columns[1], y=columns[0], kind='scatter')
                        plt.title(f'Joint plot of {columns[1]} and {columns[0]}')
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    else:
                        sns.jointplot(data=uploaded_dataset, x=columns[0], y=columns[1], kind='scatter')
                        plt.title(f'Joint plot of {columns[0]} and {columns[1]}')
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                elif 'facet' == double_variable_match:
                    if(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                        sns.FacetGrid(uploaded_dataset, col=columns[1], hue=columns[0]).map(plt.scatter, columns[1], columns[0]).add_legend()
                        plt.title(f'Facet plot of {columns[1]} and {columns[0]}')
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                    else:
                        sns.FacetGrid(uploaded_dataset, col=columns[0], hue=columns[1]).map(plt.scatter, columns[0], columns[1]).add_legend()
                        plt.title(f'Facet plot of {columns[0]} and {columns[1]}')
                        plt.savefig(f'static/plots/{date_string}/plot.png')
                        plt.close()
                        return jsonify({'response': f"static/plots/{date_string}/plot.png"})
                else:
                    return jsonify({'response': 'Terri Did not understand the plot you were asking for. Please try again differently.'})
            else:
                return jsonify({'response': 'Column not found for plotting.'})
        else:
            return jsonify({'response': 'Plots Not found.'})
        
    elif compare_score >= 60 and compare_score > summary_score:
        columns = find_matched_columns(message_lower)
        if columns:
            if columns:
                if(uploaded_dataset[columns[0]].dtype=='object' and uploaded_dataset[columns[1]].dtype!='object'):
                    mean_per_category = uploaded_dataset.groupby(columns[0])[columns[1]].mean()
                    mean_per_category=np.round(mean_per_category,2)
                    result_dict = mean_per_category.to_dict()
                    result_list1 = [{'category': key, 'Average value': value} for key, value in result_dict.items()]
                    #result_list1.insert(0,f"{columns[0]} vs {columns[1]}")
                    mode_per_category = uploaded_dataset.groupby(columns[1])[columns[0]].apply(lambda x: x.mode().iloc[0])
                    result_dict = mode_per_category.to_dict()
                    #result_list1.append(f"{columns[1]} vs {columns[1]}")
                    result_list1.append([{'category': key, 'Most frequent value': value} for key, value in result_dict.items()])
                elif(uploaded_dataset[columns[0]].dtype!='object' and uploaded_dataset[columns[1]].dtype=='object'):
                    mean_per_category = uploaded_dataset.groupby(columns[1])[columns[0]].mean()
                    mean_per_category=np.round(mean_per_category,2)
                    result_dict = mean_per_category.to_dict()
                    result_list1 = [{'category': key, 'Average value': value} for key, value in result_dict.items()]
                    #result_list1.insert(0, f"{columns[1]} vs {columns[0]}")
                    mode_per_category = uploaded_dataset.groupby(columns[0])[columns[1]].apply(lambda x: x.mode().iloc[0])
                    result_dict = mode_per_category.to_dict()
                    #result_list1.append(f"{columns[0]} vs {columns[1]}")
                    result_list1.append([{'category': key, 'Most frequent value': value} for key, value in result_dict.items()])
                elif(uploaded_dataset[columns[0]].dtype=='object' and uploaded_dataset[columns[1]].dtype=='object'):
                    mode_per_category_1 = uploaded_dataset.groupby(columns[0])[columns[1]].apply(lambda x: x.mode().iloc[0])
                    result_dict = mode_per_category_1.to_dict()
                    result_list1 = [{'category': key, 'Most frequent value': value} for key, value in result_dict.items()]
                    #result_list1.insert(0, f"{columns[0]} vs {columns[1]}")
                    mode_per_category_1 = uploaded_dataset.groupby(columns[1])[columns[0]].apply(lambda x: x.mode().iloc[0])
                    result_dict = mode_per_category_1.to_dict()
                    #result_list1.append(f"{columns[1]} vs {columns[0]}")
                    result_list1.append([{'category': key, 'Most frequent value': value} for key, value in result_dict.items()])
                else:
                    mean_per_category = uploaded_dataset.groupby(columns[0])[columns[1]].mean()
                    mean_per_category=np.round(mean_per_category,2)
                    result_dict = mean_per_category.to_dict()
                    result_list1 = [{'category': key, 'Average value': value} for key, value in result_dict.items()]
                    #result_list1.insert(0, f"{columns[0]} vs {columns[1]}")
                    mean_per_category = uploaded_dataset.groupby(columns[1])[columns[0]].mean()
                    mean_per_category=np.round(mean_per_category,2)
                    result_dict = mean_per_category.to_dict()
                    #result_list1.append(f"{columns[1]} vs {columns[0]}")
                    result_list1.append([{'category': key, 'Average value': value} for key, value in result_dict.items()])
                return jsonify({'response': json.dumps(result_list1)})
            else:
                return jsonify({'response' : "Columns not found for comparing"})
    else:
        return jsonify({'response': "Terri did not catch what you were trying to ask. Please try another way."})

def find_matched_column(message_lower):
    global uploaded_dataset
    columns = uploaded_dataset.columns.tolist()
    column_match, column_score = process.extractOne(message_lower, columns)
    if column_score >= 50:
        return column_match
    return None

def find_matched_columns(message_lower):
    global uploaded_dataset
    columns = sorted(uploaded_dataset.columns.tolist(), key=len)
    column_matches = process.extract(message_lower, columns, limit=2)
    if column_matches[0][1] >= 50 and column_matches[1][1] >= 50:
        return [column_matches[0][0], column_matches[1][0]]
    
    return None

if __name__ == '__main__':
    app.run(debug=False)

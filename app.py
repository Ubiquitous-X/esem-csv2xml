import os, csv
from flask import Flask, flash, Markup, request, url_for, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv('.env')
ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = os.getcwd()
xmlFile = os.path.join(UPLOAD_FOLDER, 'ProductRowPrices.xml')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('Ingen fil i anropet')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Du måste välja en fil')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, 'incomming.csv'))
            with open(UPLOAD_FOLDER + '/' + 'incomming.csv','rt') as csvfile:
                csvData = csv.reader(csvfile, delimiter=';', quotechar=',')
            # csvData = csv.reader(open(UPLOAD_FOLDER + '/' + 'incomming.csv','rt'))
                csvData = list(csvData)

                tags = [item.replace(' ', '_') for item in csvData[0]] # get the headers. Not currently in use, as they are hardcoded at the moment
                csvData = (csvData[1:]) # strip headers from dataset

                xmlData = open(xmlFile, 'w')
                xmlData.write('<?xml version="1.0" encoding="UTF-8"?>\n<ProductRowPriceImportSet xmlns="http://www.logica.com/BusinessForUtilities/2012/ProductRowPriceImportSet.xsd">\n')

                previous_id = None
                rows = 0
                for row in csvData:  
                    row_id = row[0]
                    # close previous group, unless it is the first group
                    if previous_id is not None:
                        xmlData.write('</ProductRowPrice>\n')
                    # open new group
                    xmlData.write('<ProductRowPrice>\n<ExternalCodePriceList>{}</ExternalCodePriceList>\n'.format(row[1]))
                    xmlData.write('<ExternalCodeProductRow>{}</ExternalCodeProductRow>\n'.format(row[2]))
                    xmlData.write('<Date>{} {}</Date>\n'.format(row[3],'00:00:00'))
                    xmlData.write('<Price>{}</Price>\n'.format(row[4]))
                    xmlData.write('<FixedPriceVersionName>{}</FixedPriceVersionName>\n'.format(row[5]))
                    # remember new group's id
                    previous_id = row_id
                    rows += 1

                # close group
                xmlData.write('</ProductRowPrice>\n')
                xmlData.write('</ProductRowPriceImportSet>\n')
                xmlData.close()
                flash('{} rader har konverterats.'.format(rows))
                return redirect(url_for('success', pricerows = rows))

        else:
            flash('Endast CSV-filer tillåtna')

    return render_template('index.html')

@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        if request.form.get('download') == 'Hämta XML-filen':
            return send_from_directory(UPLOAD_FOLDER,'ProductRowPrices.xml',as_attachment=True)
        else:
            return redirect(url_for('upload_file'))
    elif request.method == 'GET':
        return render_template('success.html')

@app.route('/mall', methods=['GET'])
def example():
    return send_from_directory(UPLOAD_FOLDER,'ProductRowPricesExempelfil.csv',as_attachment=True)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)

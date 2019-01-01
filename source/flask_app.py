from flask import Flask, make_response, request, render_template
from processxml import readxml, writexml
from dataframe import create_dataframe, create_previous
from generate import model, debug_gen
#from processing import readxml, create_dataframe, create_previous, debug_gen, model, writexml
from viz import generate_json
from sklearn.preprocessing import LabelEncoder
import xml.etree.cElementTree as ET
import smtplib

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')

def index():
    return render_template("index.html")

@app.route('/send')

def send():

    name = request.args.get("name")
    email = request.args.get("email")
    words = request.args.get("message")

    gmail_user = '*********@gmail.com'
    gmail_password = '***********'

    FROM = gmail_user
    TO = ['************@gmail.com']
    SUBJECT = name
    TEXT = "Email: " + email + "\n\n" + "Message: \n" + words

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(FROM, TO, message)
        server.close()

        print('Email sent!')
    except Exception as e:
        print('Something went wrong...')
        print(e)
    return ''

@app.route('/run')

def run():

    path = 'Beethoven - Fur Elise V3.xml'

    debug = False

    tree = ET.parse(path)
    root = tree.getroot()

    column_chord = []
    column_step = []
    column_alter = []
    column_octave = []
    column_type = []
    column_dot = []

    readxml(root, column_chord, column_step, column_alter, column_octave, column_type, column_dot)

    data = create_dataframe(column_chord, column_step, column_alter, column_octave, column_type, column_dot)

    filename_out = 'static/export.json'
    json_out = open(filename_out,'w')
    json_out.write(generate_json(data))
    json_out.close()

    enc = LabelEncoder()
    data['note'] = enc.fit_transform(data['note'])

    df = create_previous(data)

    gen_notes = model(df)

    if debug:
        gen_notes = debug_gen(data)

    writexml(root, tree, data, gen_notes)

    #xml_to_midi('output.xml')

    with open('output.xml', 'rb') as myfile:
        response = make_response(myfile.read())
        response.headers["Content-Disposition"] = "attachment; filename=output.xml"
        return response

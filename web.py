from flask import Flask, request, jsonify, abort, make_response, after_this_request, send_from_directory
import markdown
import re
import os
import subprocess
import shutil
import gzip
import lib.Libtech3


app = Flask(__name__)
app.config.from_pyfile('config.cfg')

@app.route('/')
def index():
    return markdown.markdown(open('README.md', 'r').read())

@app.route('/parse/<int:demo_id>')
def list_maps(demo_id):
    #"demo0000.tv_84"
    demos=[]
    try:
        for filename in os.listdir('demos/'+str(demo_id)):
            demos.append(int(re.search('demo(\d+)\.tv_84', filename).group(1)))
    except FileNotFoundError:
        return jsonify([])
    return jsonify(demos)

@app.route('/parse/<int:demo_id>/<int:map_number>')
def parse(demo_id,map_number):
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if 'gzip' not in accept_encoding.lower():
        #TODO: sent info that request has to accept gzip
        return abort(406)
    file_path="demos/{}/demo{:04}.tv_84".format(demo_id,int(map_number))
    json_folder="jsons/{}".format(demo_id)
    json_path=json_folder+"/demo{:04}.json".format(int(map_number))
    if os.name == 'nt':
        file_path=file_path.replace('/','\\')
        json_path = json_path.replace('/', '\\')
    if os.path.isfile(json_path+'.gz'): #TODO: compare json and lib modification time
        response = make_response(open(json_path + '.gz', 'rb').read())
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Vary'] = 'Accept-Encoding'
        return response
    os.makedirs(json_folder,exist_ok=True)
    arg = app.config['INDEXER'] % (file_path, json_path)
    subprocess.call([app.config['PARSERPATH'], 'indexer', arg])

    try:
        with open(json_path, 'rb') as f_in:
            with gzip.open(json_path+'.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(json_path)
        response = make_response(open(json_path+'.gz','rb').read())
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Vary'] = 'Accept-Encoding'
        return response
    except FileNotFoundError:
        print("not found:",json_path)
        abort(404)

@app.route('/cut', methods=['POST'])
def cut():
    demo_path = "demos/{}/demo{:04}.tv_84".format(request.form['demo_id'], int(request.form['map_number']))
    cut_name = request.form['demo_id']+"_"+request.form['map_number']+"_"+request.form['start']+"_"+request.form['end']+"_"+request.form['cut_type']+"_"+request.form['client_num']+".dm_84"
    cut_path = "cuts/"+cut_name
    try:
        lib.Libtech3.cut(
            app.config['PARSERPATH'], demo_path, cut_path, request.form['start'],
            request.form['end'], request.form['cut_type'], request.form['client_num'])
    except Exception as e:
        return e
    return send_from_directory(directory='cuts',filename=cut_name, as_attachment=True,
                               attachment_filename=cut_name)

if __name__ == "__main__":
    app.run(port=5222, host='0.0.0.0',debug=True)
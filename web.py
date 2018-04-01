from flask import Flask, request, jsonify, abort, make_response, after_this_request
import markdown
import re
import os
import subprocess
import shutil
import gzip


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
    file_path="{}/demo{:04}.tv_84".format(demo_id,int(map_number))
    json_path="jsons/{}/demo{:04}.json".format(demo_id,int(map_number))
    if os.path.isfile(json_path+'.gz'): #TODO: compare json and lib modification time
        response = make_response(open(json_path + '.gz', 'rb').read())
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Vary'] = 'Accept-Encoding'
        return response

    arg = app.config['INDEXER'] % (file_path, json_path)
    subprocess.call([app.config['PARSERPATH'], 'indexer', arg])
    #json_path=json_path.replace('\\','/')
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
    return "TODO"

if __name__ == "__main__":
    app.run(port=5222, host='0.0.0.0',debug=True)
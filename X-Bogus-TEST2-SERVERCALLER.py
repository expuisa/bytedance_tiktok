** NEEDS SERVER FOR CALLING BOGUS **

from flask import Flask, request, jsonify
import execjs
import urllib.parse

app = Flask(__name__)

@app.route('/gen', methods=['POST'])
def handler():
    payload = request.get_json()
    incoming_url = payload.get('url')
    ua = payload.get('user_agent')
    
    parsed_query = urllib.parse.urlparse(incoming_url).query
    
    js_ctx = execjs.compile(open('./X-Bogus.js').read())
    bogus_token = js_ctx.call('sign', parsed_query, ua)
    
    modified_url = f"{incoming_url}&X-Bogus={bogus_token}"
    
    return jsonify({
        "param": modified_url,
        "X-Bogus": bogus_token
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8787)

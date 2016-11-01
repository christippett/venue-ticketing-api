from flask import Flask, make_response, jsonify  # type: ignore
from venue import VIFGateway

app = Flask(__name__)

gateway = VIFGateway(site_name='BARKER',
                     host='202.189.77.154',
                     auth_key='1081930166',
                     agent_no='48')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/venue/get_data', methods=['GET'])
def get_tasks():
    data = gateway.get_data()
    return jsonify({
        'data': data
    })


@app.route('/api/venue/handshake', methods=['GET'])
def handshake():
    data = gateway.handshake()
    return jsonify({
        'data': data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0')

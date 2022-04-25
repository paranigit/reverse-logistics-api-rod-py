from flask import Flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from waitress import serve
import requests
import os

app = Flask(__name__)

@app.route('/')
def hello():
     # Get IBM Cloud Access Token to access WML API Gateway
    try:
        API_KEY = os.environ.get("IBM_CLOUD_API_KEY")
        URL_IBM_ACCESS_ENDPOINT = os.environ.get("URL_IBM_ACCESS_ENDPOINT")
        URL_WML_ENDPOINT = os.environ.get("URL_WML_ENDPOINT")

        payload_access = {
            "apikey": API_KEY,
            "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'
        }
        print(payload_access)
        token_response = requests.post(URL_IBM_ACCESS_ENDPOINT, payload_access)

    except Exception as e:
        print(e)
        result = {
            'message' : 'failure',
            'error': str(e)
        }

        return jsonify(result)
    
    return jsonify({'message' : 'IBM Auth verified; API is Working!'})

@app.route('/predict/v1', methods=['POST', 'GET'])
@cross_origin()
def predict_cp4d():
    if request.method == 'POST':
        data = request.json
        result = {}
        print("data is " + format(data))
        try:
            # Get IBM Cloud Access Token to access WML API Gateway
            API_KEY = os.environ.get("IBM_CLOUD_API_KEY")
            URL_IBM_ACCESS_ENDPOINT = os.environ.get("URL_IBM_ACCESS_ENDPOINT")
            URL_WML_ENDPOINT = os.environ.get("URL_WML_ENDPOINT")

            payload_access = {
                "apikey": API_KEY,
                "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'
            }
            print(payload_access)

            token_response = requests.post(URL_IBM_ACCESS_ENDPOINT, payload_access)
            mltoken = token_response.json()["access_token"]
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
            payload_scoring = {
                "input_data": [{
                    "fields": ["category", "seller", "product", "city", "mop", "mod", "delivery_month", "delivery_dow"], 
                    "values": [list(data['values'])]
                }]
            }
            print(payload_scoring)

            response_scoring = requests.post(URL_WML_ENDPOINT, json=payload_scoring, headers=headers)
            print(response_scoring)
            
            predict = response_scoring.json()
            print(predict)
            result = {
                'message' : 'success',
                'return_prob_no': (predict['predictions'][0]['values'][0][1][0] * 100),
                'return_prob_yes': (predict['predictions'][0]['values'][0][1][1] * 100)
            }

        except Exception as e:
            print(e)
            result = {
                'message' : 'failure',
                'error': str(e)
            }
    else:
        result = {
            'message' : 'failure',
            'error' : 'invalid HTTP request. Use Post method instead.'
        }

    return jsonify(result)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)

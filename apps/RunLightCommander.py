import time
import vonage
from flask import Flask, request
import os

from LightCommander import LightCommander

# Example code https://github.com/vonage/vonage-python-code-snippets/blob/master/sms/receive-flask.py

app = Flask(__name__)

client = vonage.Client(key=os.environ.get('VONAGE_KEY'), secret=os.environ.get('VONAGE_SECRET'))
sms = vonage.Sms(client)

# Need to run `ngrok http 3000 --host-header="localhost:3000"`
# Include something like `https://34be-169-229-22-180.ngrok.io/webhooks/inbound-sms`
# to https://dashboard.nexmo.com/settings under `Inbound SMS webhooks`

lc = LightCommander()

@app.route('/webhooks/inbound-sms', methods=['GET', 'POST'])
def inbound_sms():
    data = dict(request.form) or dict(request.args)
    resp = lc.handleMessage(data['text'])
    responseData = sms.send_message(
        {
            "from": "18664603571",
            "to": "19163078818",
            "text": resp,
        }
    )
    if responseData["messages"][0]["status"] == "0":
        print("Message sent successfully.")
    else:
        print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
    return ('', 204)

if __name__ == '__main__':
    app.run(port=3000)

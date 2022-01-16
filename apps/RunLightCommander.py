import time
import vonage
from flask import Flask, request

from LightCommander import LightCommander

# Example code https://github.com/vonage/vonage-python-code-snippets/blob/master/sms/receive-flask.py

app = Flask(__name__)

# Make these secrets env variables before pushing onto git
client = vonage.Client(key="e0fd3a2a", secret="jLZHKTQdYA4rjcGa")
sms = vonage.Sms(client)

# Need to run `ngrok http 8840 --host-header="localhost:8840"`
# Include something like `http://efc2-169-229-22-180.ngrok.io/webhooks/inbound-sms`
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

app.run(port=8840)


# if responseData["messages"][0]["status"] == "0":
#     print("Message sent successfully.")
# else:
#     print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

# from drlm_app.drlm_app import DrlmApp
# from drlm_common.datatypes import Color
# from SolidColorApp import SolidColor
#
# if __name__ == "__main__":
#     app = SolidColor(Color.from_rgb(15, 7, 1), ranges = [(150, 250)])
#     app.run()
#     app.close()

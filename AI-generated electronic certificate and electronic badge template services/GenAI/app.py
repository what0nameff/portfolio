import os
import smtplib
import base64 
import traceback 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import AzureOpenAI
import json
import logging


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

client = AzureOpenAI(
    api_version="2024-05-01-preview",
    azure_endpoint="https://muelsyse.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-email', methods=['POST'])
def send_email():  
    data = request.json  
    recipient_email = data.get('email')  
    image_data = data.get('image')  # base64 image data

    try:
        # Email configuration
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'notreply.gen.img.ai@gmail.com' # pls enter your or Company email 
        sender_password = 'password'

        # Create the email content  
        msg = MIMEMultipart()  
        msg['Subject'] = "Your Design"  
        msg['From'] = sender_email  
        msg['To'] = recipient_email  
  
        # Attach text  
        text = MIMEText("Here is your Design.")  
        msg.attach(text)  
  
        # Decode the base64 image  
        image_format, image_str = image_data.split(';base64,')  
        decoded_image = base64.b64decode(image_str)  
        image = MIMEImage(decoded_image)  
  
        # Attach the image  
        msg.attach(image)  
  
        # Connect to the SMTP server  
        with smtplib.SMTP(smtp_server, smtp_port) as server:  
            server.starttls()  # Upgrade the connection to secure  
            server.login(sender_email, sender_password)  
  
            # Send the email  
            server.sendmail(sender_email, recipient_email, msg.as_string())  
  
        return jsonify({'status': 'success'})  
  
    except Exception as e:  
        print(traceback.format_exc())  # print the traceback  
        return jsonify({'status': 'error', 'message': str(e)}), 500  

@app.route('/generate-image', methods=['GET', 'POST'])
def generate_image():
    logging.debug(f"Request data: {request.json}")
    print("Route hit!")

    if request.method == 'POST':
        data = request.json
        prompt = data.get('prompt', '')

        try:
            result = client.images.generate(
                model="GenAI_01",
                prompt=prompt,
                n=1
            )
            image_url = json.loads(result.model_dump_json())['data'][0]['url']
            return jsonify({'url': image_url})

        except Exception as e:
            logging.error("Error generating image: %s", str(e))
            return jsonify({'error': str(e)}), 500

    elif request.method == 'GET':
        return jsonify({'message': 'This endpoint handles image generation requests.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
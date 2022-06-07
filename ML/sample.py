import base64

with(open('SVM Predictions.png'), 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
print(image_data)
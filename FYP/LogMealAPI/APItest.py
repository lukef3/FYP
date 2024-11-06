import requests
img = 'Images/spaghetti-bolognese-36-720x720.jpg'
api_user_token = 'b4528aa735161c38b4637a41719bd23d8cbbfdb1'
headers = {'Authorization': 'Bearer ' + api_user_token}

# Single/Several Dishes Detection
url = 'https://api.logmeal.com/v2/image/segmentation/complete'
resp = requests.post(url,files={'image': open(img, 'rb')}, headers=headers)
print(resp.json()["segmentation_results"]) # display dish only
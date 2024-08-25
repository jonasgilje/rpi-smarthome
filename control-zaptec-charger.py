import requests
 
ZAPTEC_USERNAME = ...
ZAPTEC_PASSWORD = ...
CHARGER_ID = ...
# 506: stop; 507: start
CHARGER_COMMAND = "507"
AUTH_URL = "https://api.zaptec.com/oauth/token"
COMMAND_URL = f"https://api.zaptec.com/api/chargers/{CHARGER_ID}/sendCommand/{CHARGER_COMMAND}"
 
def main() -> None:
	data = {"grant_type": "password",
		"username": ZAPTEC_USERNAME,
		"password": ZAPTEC_PASSWORD}
	x = requests.post(AUTH_URL, data=data)
	access_token = x.json()["access_token"]
 
	resp = requests.post(COMMAND_URL, headers={"accept": "*/*", "Authorization": f"Bearer {access_token}"})
	print(resp.status_code)
 
if __name__ == "__main__":
	main()

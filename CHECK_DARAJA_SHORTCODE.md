# URGENT: Find Your Correct Business Shortcode

## The Problem

Error: **"Merchant does not exist"** (Error Code: 500.001.1001)

This means the Business Shortcode **9659929** is NOT registered with your Daraja app for STK Push.

## Your Numbers (From Safaricom):

```
STORE NO:           9659929  ← Currently using this (NOT WORKING)
TILL NO:            3132055
HEAD OFFICE/SHORT CODE: 9659906  ← Try this one!
```

## What To Do RIGHT NOW:

### Step 1: Login to Daraja Portal
Go to: https://developer.safaricom.co.ke

### Step 2: Find Your Production App
- Click on your Production app
- NOT Sandbox - Production!

### Step 3: Check "Lipa Na M-Pesa Online" Section
Look for a section or tab labeled "Lipa Na M-Pesa Online" or "STK Push"

### Step 4: Find Business Shortcode
You should see something like:

```
Lipa Na M-Pesa Online
─────────────────────
Business Shortcode: XXXXXXX  ← THIS IS WHAT YOU NEED!
Passkey: [long string]
```

## Most Likely Solutions:

### Option 1: Use Head Office Shortcode (9659906)
For most Safaricom setups, the **Head Office Shortcode** is used for STK Push, NOT the Store Number.

**Try this:**
1. Open Tookio Mpesa Settings
2. Change Store Number from **9659929** to **9659906**
3. Save
4. Test again

### Option 2: Check Daraja Portal
If Option 1 doesn't work, the shortcode in your Daraja portal might be different from all three numbers you have.

## Testing Each Shortcode

We can test each shortcode to see which one works:

### Test 1: Head Office Shortcode (9659906)
```python
# In bench console
from tookio_mpesa.utils import get_access_token
import frappe
import requests
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth

settings = frappe.get_single("Tookio Mpesa Settings")
access_token = get_access_token()

# Test with Head Office Shortcode
shortcode = "9659906"
passkey = settings.get_password('passkey')
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
password_str = f"{shortcode}{passkey}{timestamp}"
password = base64.b64encode(password_str.encode('utf-8')).decode('utf-8')

payload = {
    "BusinessShortCode": shortcode,
    "Password": password,
    "Timestamp": timestamp,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": 1,
    "PartyA": "254743169908",
    "PartyB": shortcode,
    "PhoneNumber": "254743169908",
    "CallBackURL": "https://shop.tookio.co.ke/api/method/tookio_mpesa.utils.stk_callback",
    "AccountReference": "TEST",
    "TransactionDesc": "Test"
}

response = requests.post(
    "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
    json=payload,
    headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

### Test 2: Store Number (9659929)
Same code but change `shortcode = "9659929"`

### Test 3: Till Number (3132055)
Same code but change `shortcode = "3132055"`

## Common Scenarios:

### Scenario A: Using Paybill
If you're using a **Paybill** account:
- Use **Head Office Shortcode** (9659906)
- TransactionType: "CustomerPayBillOnline"

### Scenario B: Using Till (Buy Goods)
If you're using a **Till/Buy Goods** account:
- Use **Store Number** (9659929)
- TransactionType: "CustomerBuyGoodsOnline"

But since you're getting "Merchant does not exist", it's likely you need to use the **Head Office Shortcode**.

## Quick Fix (Most Likely):

**Change Store Number to 9659906:**

1. Open: Tookio Mpesa Settings
2. Change:
   ```
   Store Number: 9659906  ← Changed from 9659929
   Till Number: 3132055   ← Leave as is
   Head Office Shortcode: 9659906  ← Reference
   ```
3. Save
4. Try subscription renewal again

## Still Not Working?

If none of your three numbers work, then:

1. **Login to Daraja Portal**
2. **Screenshot the Business Shortcode** from "Lipa Na M-Pesa Online" section
3. **Use EXACTLY that shortcode**

The shortcode in Daraja might be completely different from all three numbers Safaricom gave you!

## Need Help?

If you're still stuck:
1. Check your Daraja app's Business Shortcode
2. Verify your app has "Lipa Na M-Pesa Online" product enabled
3. Contact Safaricom: apisupport@safaricom.co.ke

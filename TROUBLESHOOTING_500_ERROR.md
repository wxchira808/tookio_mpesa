# M-Pesa 500 Internal Server Error - Troubleshooting Guide

## Error Message
```
STK Push failed: 500 Server Error: Internal Server Error for url: https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest
```

## Common Causes

### 1. Invalid Business Shortcode
**Problem:** The Business Shortcode doesn't match your Daraja app credentials.

**Solution:**
- Go to **Tookio Mpesa Settings**
- Verify **Business Shortcode** matches what's registered in your Daraja portal
- For STK Push, use the **Paybill shortcode** or **Store Number** (not Till Number)

### 2. Incorrect Passkey
**Problem:** The Passkey is wrong or missing.

**Solution:**
- Go to Daraja Portal → Your App → Get your **Lipa Na M-Pesa Online Passkey**
- Copy the ENTIRE passkey (usually 40+ characters)
- Go to **Tookio Mpesa Settings** → Enter in **Passkey** field
- Click **Save**

### 3. Shortcode Not Registered for STK Push
**Problem:** Your shortcode doesn't have the "Lipa Na M-Pesa Online" product enabled.

**Solution:**
- Login to Daraja Portal
- Check your app has **"Lipa Na M-Pesa Online"** product enabled
- If not, add it to your app
- Wait for approval from Safaricom

### 4. Wrong Environment
**Problem:** Using production credentials in sandbox or vice versa.

**Solution:**
- Verify **Environment** setting matches your credentials
- Sandbox credentials won't work in Production
- Production credentials won't work in Sandbox

## Validation Checklist

Run this command in bench console to validate your settings:

```python
from tookio_mpesa.utils import validate_mpesa_production_settings
result = validate_mpesa_production_settings()
print(result)
```

## Step-by-Step Fix

### For Production Environment:

1. **Get Correct Values from Daraja Portal:**
   - Login to https://developer.safaricom.co.ke
   - Go to your Production app
   - Note down:
     - Consumer Key
     - Consumer Secret
     - Business Shortcode (from Lipa Na M-Pesa Online settings)
     - Passkey (from Lipa Na M-Pesa Online settings)

2. **Update Tookio Mpesa Settings:**
   ```
   - Environment: Production
   - Consumer Key: [from Daraja]
   - Consumer Secret: [from Daraja]
   - Business Shortcode: [from Daraja - NOT your till number]
   - Passkey: [from Daraja - full 40+ character string]
   - Is Active: ✓ Checked
   ```

3. **Verify Your Site is HTTPS:**
   - Production M-Pesa requires HTTPS
   - Your callback URL must be publicly accessible
   - Format: `https://yourdomain.com/api/method/tookio_mpesa.utils.stk_callback`

4. **Test the Configuration:**
   ```python
   # In bench console
   from tookio_mpesa.utils import validate_mpesa_production_settings
   validate_mpesa_production_settings()
   ```

### For Sandbox Environment (Testing):

1. **Use Standard Test Credentials:**
   ```
   - Environment: Sandbox
   - Consumer Key: [Your sandbox app key]
   - Consumer Secret: [Your sandbox app secret]
   - Business Shortcode: 174379 (standard test shortcode)
   - Passkey: bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
   ```

2. **Test with Sandbox Phone:**
   - Use test phone: 254712345678 or similar
   - Sandbox may not send actual STK push

## Common Mistakes

1. **Using Till Number for Business Shortcode**
   - ❌ Wrong: Till Number (e.g., 6547212)
   - ✅ Correct: Business Shortcode from Daraja (e.g., 174379 or your paybill)

2. **Wrong Passkey Format**
   - ❌ Wrong: Short password or portal password
   - ✅ Correct: Long passkey from "Lipa Na M-Pesa Online" section (40+ chars)

3. **Missing HTTPS**
   - ❌ Wrong: http://localhost:8000
   - ✅ Correct: https://yourdomain.com

4. **Sandbox Credentials in Production**
   - ❌ Wrong: Using test credentials in production environment
   - ✅ Correct: Use production app credentials for production

## Debug Commands

### Check Current Settings
```python
import frappe
settings = frappe.get_single("Tookio Mpesa Settings")
print(f"Environment: {settings.environment}")
print(f"Business Shortcode: {settings.business_shortcode}")
print(f"Has Passkey: {bool(settings.get_password('passkey'))}")
print(f"Callback URL: {frappe.utils.get_url('/api/method/tookio_mpesa.utils.stk_callback')}")
```

### Test Access Token
```python
from tookio_mpesa.utils import test_mpesa_credentials
result = test_mpesa_credentials()
print(result)
```

### Validate All Settings
```python
from tookio_mpesa.utils import validate_mpesa_production_settings
result = validate_mpesa_production_settings()
import json
print(json.dumps(result, indent=2))
```

## Still Not Working?

1. **Check Error Log in ERPNext:**
   - Go to **Error Log** list
   - Find recent "M-Pesa 500 Error" entries
   - Review the detailed error message

2. **Contact Safaricom:**
   - Email: apisupport@safaricom.co.ke
   - Provide your App details and error

3. **Verify App Status:**
   - Login to Daraja Portal
   - Check your app is approved
   - Check "Lipa Na M-Pesa Online" product is active

## Quick Fix for Common Scenarios

### Scenario 1: Just moved from Sandbox to Production
```
1. Change Environment to "Production"
2. Enter Production Consumer Key & Secret
3. Enter Production Business Shortcode (NOT till number)
4. Enter Production Passkey (get from Daraja)
5. Verify site is HTTPS
6. Test with validate_mpesa_production_settings()
```

### Scenario 2: Using Till Number
```
For STK Push, you MUST use:
- Business Shortcode (from Daraja app)
- NOT the Till Number

Till Number is different from Business Shortcode!
```

### Scenario 3: New Daraja App
```
1. Ensure "Lipa Na M-Pesa Online" product is added
2. Wait for Safaricom approval (can take hours/days)
3. Get Passkey from app's Lipa Na M-Pesa section
4. Use Store Number or Shortcode (not Till)
```

## Need Help?

Check the comprehensive documentation:
- [SUBSCRIPTION_RENEWAL_SETUP.md](../../tookio_shop/SUBSCRIPTION_RENEWAL_SETUP.md)
- [SUBSCRIPTION_RENEWAL_IMPLEMENTATION.md](../../tookio_shop/SUBSCRIPTION_RENEWAL_IMPLEMENTATION.md)

Or run the validation tool to get specific guidance based on your configuration.

# M-Pesa Setup Guide for Tookio

This guide will help you configure M-Pesa payments for your Tookio Shop.

## Understanding Your Safaricom Numbers

Safaricom gives you three different numbers:

1. **STORE NO (Store Number)** - e.g., 9659929
   - This is the **Business Shortcode** for STK Push
   - Use this for "Lipa Na M-Pesa Online" payments

2. **TILL NO (Till Number)** - e.g., 3132055
   - This is your actual till number for receiving payments
   - For reference only

3. **HEAD OFFICE / SHORT CODE** - e.g., 9659906
   - Your main business shortcode
   - For reference only

## Configuration Steps

### Step 1: Get Your Daraja API Credentials

1. Go to https://developer.safaricom.co.ke
2. Login or create an account
3. Create an app (or use existing)
4. Add **"Lipa Na M-Pesa Online"** product to your app
5. Note down:
   - **Consumer Key**
   - **Consumer Secret**
   - **Passkey** (from Lipa Na M-Pesa Online section)

### Step 2: Configure Tookio Mpesa Settings

1. In ERPNext, search for "Tookio Mpesa Settings"
2. Fill in the following:

```
API Credentials:
├── Consumer Key: [Your Daraja Consumer Key]
├── Consumer Secret: [Your Daraja Consumer Secret]
├── Passkey: [Your Daraja Passkey - 40+ characters]
├── Environment: Production
└── Is Active: ✓ Checked

Business Numbers:
├── Store Number: 9659929  ← USE THIS (your actual STORE NO)
├── Till Number: 3132055   ← For reference only
└── Head Office Shortcode: 9659906  ← For reference only

Callback URLs:
└── These are auto-generated (read-only)
```

### Step 3: Important - Use the Correct Number!

⚠️ **Critical: For STK Push, you MUST use your STORE NUMBER (not Till Number)**

```
✅ CORRECT:
Store Number: 9659929

❌ WRONG:
Store Number: 3132055  (This is your Till Number, not Store Number!)
```

The 500 error you encountered was likely because Till Number (3132055) was being used instead of Store Number (9659929).

### Step 4: Verify Your Setup

Run this in bench console to verify:

```bash
cd /home/brian/frappe-bench
bench --site tookio-shop.local console
```

```python
from tookio_mpesa.utils import validate_mpesa_production_settings
result = validate_mpesa_production_settings()
import json
print(json.dumps(result, indent=2))
```

You should see:
```json
{
  "ready_for_production": true,
  "issues": [],
  "warnings": []
}
```

### Step 5: Test STK Push

Test a small payment:

```python
from tookio_mpesa.utils import initiate_stk_push_for_till

result = initiate_stk_push_for_till(
    phone_number="0712345678",  # Your phone number
    amount="5",
    account_reference="TEST-001",
    transaction_desc="Test Payment"
)

print(result)
```

You should receive an STK Push prompt on your phone.

## Troubleshooting

### Error: "500 Internal Server Error"

**Cause:** Wrong Business Shortcode
**Solution:** 
- Make sure you're using **Store Number** (9659929) NOT Till Number (3132055)
- Verify the Store Number matches what's in your Daraja portal

### Error: "Invalid Access Token"

**Cause:** Wrong Consumer Key/Secret
**Solution:**
- Double-check Consumer Key and Consumer Secret from Daraja portal
- Make sure you're using Production credentials (not Sandbox)

### Error: "Invalid Passkey"

**Cause:** Wrong or missing Passkey
**Solution:**
- Go to Daraja Portal → Your App → Lipa Na M-Pesa Online
- Copy the ENTIRE passkey (40+ characters)
- Paste it into Tookio Mpesa Settings → Passkey field

### STK Push Not Received

**Possible Causes:**
1. Phone number format wrong - should be 254XXXXXXXXX or 07XXXXXXXX
2. Store Number not registered for Lipa Na M-Pesa Online
3. Callback URL not HTTPS (production requires HTTPS)

**Solution:**
- Verify Store Number is registered for STK Push in Daraja portal
- Check your site is accessible via HTTPS
- Test with the phone number registered to your Safaricom account

## Settings Reference

### Simplified Settings Fields

The new simplified Tookio Mpesa Settings only includes essential fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Consumer Key | Data | Yes | From Daraja Portal |
| Consumer Secret | Password | Yes | From Daraja Portal |
| Passkey | Password | Yes | 40+ char string from Daraja |
| Environment | Select | Yes | Sandbox or Production |
| Is Active | Check | No | Enable/disable M-Pesa |
| Store Number | Data | Yes | **USE THIS for STK Push** |
| Till Number | Data | No | Reference only |
| Head Office Shortcode | Data | No | Reference only |

### What Changed

Previously, the settings had many confusing fields:
- ❌ business_shortcode
- ❌ paybill_number
- ❌ transaction_type
- ❌ use_till_number
- ❌ organization_name
- ❌ default_currency

Now it's simplified to just the essentials you actually have:
- ✅ Consumer Key, Consumer Secret, Passkey
- ✅ Store Number, Till Number, Head Office Shortcode
- ✅ Environment (Sandbox/Production)

## Your Specific Configuration

Based on your Safaricom details:

```
Store Number: 9659929  ← Use this for STK Push
Till Number: 3132055
Head Office Shortcode: 9659906
Environment: Production
```

Fill in your Daraja credentials and you're good to go!

## Next Steps

Once configured:
1. Test with a small payment (5 KES)
2. Verify the transaction appears in "Mpesa Transaction" list
3. Test subscription renewal feature
4. Monitor error logs if issues arise

## Support

If you still encounter issues:
1. Check Error Log in ERPNext
2. Verify all credentials match Daraja portal
3. Ensure your site is HTTPS in production
4. Contact Safaricom API support: apisupport@safaricom.co.ke

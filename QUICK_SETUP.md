# Quick Configuration - Tookio Mpesa Settings

## Copy-Paste Values

Open: **Tookio Mpesa Settings**

```
API Credentials Section:
───────────────────────
Consumer Key:     [Paste from Daraja]
Consumer Secret:  [Paste from Daraja]
Passkey:          [Paste from Daraja - 40+ characters]
Environment:      Production
Is Active:        ✓ Checked

Business Numbers Section:
────────────────────────
Store Number:             9659929  ← CRITICAL: This is used for STK Push
Till Number:              3132055  ← Reference only
Head Office Shortcode:    9659906  ← Reference only
```

## ⚠️ Common Mistake

**DON'T do this:**
```
Store Number: 3132055  ❌ (This is your Till Number!)
```

**DO this:**
```
Store Number: 9659929  ✅ (Your actual Store Number)
```

## Test Command

```bash
cd /home/brian/frappe-bench
bench --site tookio-shop.local console
```

```python
from tookio_mpesa.utils import initiate_stk_push_for_till
initiate_stk_push_for_till("0743169908", "5", "TEST", "Test Payment")
```

## Verify Settings

```python
from tookio_mpesa.utils import validate_mpesa_production_settings
print(validate_mpesa_production_settings())
```

Should show: `"ready_for_production": true`

---

**That's it!** Now go to Tookio User Subscription and click "Renew Subscription" to test the full flow.

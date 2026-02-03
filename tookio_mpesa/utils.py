# tookio_mpesa/tookio_mpesa/utils.py - FIXED FOR TILL NUMBERS

import frappe
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from datetime import datetime

def get_mpesa_settings():
    return frappe.get_single("Tookio Mpesa Settings")

@frappe.whitelist()
def validate_mpesa_production_settings():
    """Validate M-Pesa production settings before going live"""
    settings = get_mpesa_settings()
    
    issues = []
    warnings = []
    
    # Check environment
    if settings.environment != "Production":
        warnings.append(f"Currently in {settings.environment} mode")
    
    # Get consumer_secret from Password field
    consumer_secret = settings.get_password('consumer_secret') if hasattr(settings, 'consumer_secret') else None
    
    # Check credentials
    if not settings.consumer_key:
        issues.append("Consumer Key is missing")
    if not consumer_secret:
        issues.append("Consumer Secret is missing")
    
    # Check store number
    if not settings.store_number:
        issues.append("Store Number is missing (required for STK Push)")
    
    # Check passkey
    passkey = settings.get_password('passkey') if hasattr(settings, 'passkey') else None
    if not passkey:
        issues.append("Passkey is missing (required for STK Push)")
    else:
        # Passkey should be a long string
        if len(passkey) < 20:
            warnings.append(f"Passkey seems too short (length: {len(passkey)}). Expected 40+ characters")
    
    # Check callback URL
    callback_url = frappe.utils.get_url("/api/method/tookio_mpesa.utils.stk_callback")
    if not callback_url.startswith('https://'):
        issues.append(f"Callback URL must be HTTPS for production: {callback_url}")
    
    # Test credentials if no critical issues
    credential_test = None
    if not issues:
        try:
            token = get_access_token()
            credential_test = {
                "status": "success",
                "message": "✅ Successfully obtained access token",
                "token_preview": f"{token[:10]}..." if token else "None"
            }
        except Exception as e:
            credential_test = {
                "status": "error",
                "message": f"❌ Failed to get access token: {str(e)}"
            }
    
    return {
        "environment": settings.environment,
        "is_active": settings.is_active,
        "issues": issues,
        "warnings": warnings,
        "settings_summary": {
            "consumer_key": f"{settings.consumer_key[:10]}..." if settings.consumer_key else "Not set",
            "store_number": settings.store_number or "Not set",
            "till_number": settings.till_number or "Not set",
            "has_passkey": bool(passkey),
            "callback_url": callback_url
        },
        "credential_test": credential_test,
        "ready_for_production": len(issues) == 0
    }

def get_access_token():
    """Test with your actual sandbox credentials"""
    try:
        # Your actual sandbox credentials
        test_consumer_key = "GNArOqtfcHL31wtVrNBOCZ0eLEstvzWtOBgLzGvhpQbYAFne"
        test_consumer_secret = "O9TfuV3IKVbJLTtlK9qm0GWjjW8HsA8bcFXktd4BGnW9ai8s1S4HrrAxC5mZinZx"

        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        # Strip any accidental whitespace / newlines
        test_consumer_key = test_consumer_key.strip()
        test_consumer_secret = test_consumer_secret.strip()

        frappe.logger().info(f"DEBUG(test_with_your_sandbox_credentials): key={repr(test_consumer_key)} len={len(test_consumer_key)}")
        frappe.logger().info(f"DEBUG(test_with_your_sandbox_credentials): secret repr len={len(test_consumer_secret)}")

        # Use requests' HTTPBasicAuth which handles header encoding reliably
        response = requests.get(url, auth=HTTPBasicAuth(test_consumer_key, test_consumer_secret), timeout=10)

        return {
            "your_credentials": {
                "consumer_key": test_consumer_key,
                "consumer_secret": test_consumer_secret
            },
            "response": {
                "status_code": response.status_code,
                "response_text": response.text,
                "success": response.status_code == 200
            }
        }

    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist()
def test_with_known_sandbox_credentials():
    """Test with known working sandbox credentials"""
    try:
        # These are the standard Safaricom sandbox test credentials
        test_consumer_key = "GNArOqtfcHcX9M7rKQ1lGGKzH3V4y9Gv"
        test_consumer_secret = "AqZqJSlDhxHhgbgg"

        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        test_consumer_key = test_consumer_key.strip()
        test_consumer_secret = test_consumer_secret.strip()
        frappe.logger().info(f"DEBUG(test_with_known_sandbox_credentials): key={repr(test_consumer_key)} len={len(test_consumer_key)}")
        response = requests.get(url, auth=HTTPBasicAuth(test_consumer_key, test_consumer_secret), timeout=10)

        return {
            "test_credentials": {
                "consumer_key": test_consumer_key,
                "consumer_secret": test_consumer_secret
            },
            "response": {
                "status_code": response.status_code,
                "response_text": response.text,
                "success": response.status_code == 200
            }
        }

    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def test_mpesa_credentials():
    """Test M-Pesa credentials and settings"""
    try:
        settings = get_mpesa_settings()

        # Get consumer_secret from Password field
        consumer_secret = settings.get_password('consumer_secret') if hasattr(settings, 'consumer_secret') else None
        
        result = {
            "is_active": settings.is_active,
            "environment": settings.environment,
            "has_consumer_key": bool(settings.consumer_key),
            "has_consumer_secret": bool(consumer_secret),
            "has_till_number": bool(settings.till_number),
            "consumer_key_preview": settings.consumer_key[:10] + "..." if settings.consumer_key else "Not set",
            "consumer_secret_preview": consumer_secret[:10] + "..." if consumer_secret else "Not set"
        }

        # Try to get access token
        if settings.is_active and settings.consumer_key and consumer_secret:
            try:
                url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
                # Strip stored credentials to avoid hidden newlines/spaces
                ck = settings.consumer_key.strip() if settings.consumer_key else ""
                cs = consumer_secret.strip() if consumer_secret else ""
                frappe.logger().info(f"DEBUG(test_mpesa_credentials): ck_repr={repr(ck)} len={len(ck)}")
                frappe.logger().info(f"DEBUG(test_mpesa_credentials): cs_len={len(cs)}")

                response = requests.get(url, auth=HTTPBasicAuth(ck, cs), timeout=10)
                result["auth_test"] = {
                    "status_code": response.status_code,
                    "response_text": response.text[:1000],
                    "success": response.status_code == 200,
                    "headers": dict(response.headers)
                }

            except Exception as auth_error:
                result["auth_test"] = {
                    "error": str(auth_error)
                }

        return result

    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist()
def test_with_your_sandbox_credentials():
    """Test with your actual sandbox credentials"""
    try:
        # Your actual sandbox credentials
        test_consumer_key = "GNArOqtfcHL31wtVrNBOCZ0eLEstvzWtOBgLzGvhpQbYAFne"
        test_consumer_secret = "O9TfuV3IKVbJLTtlK9qm0GWjjW8HsA8bcFXktd4BGnW9ai8s1S4HrrAxC5mZinZx"

        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        # Strip any accidental whitespace / newlines
        test_consumer_key = test_consumer_key.strip()
        test_consumer_secret = test_consumer_secret.strip()

        frappe.logger().info(f"DEBUG(test_with_your_sandbox_credentials): key={repr(test_consumer_key)} len={len(test_consumer_key)}")
        frappe.logger().info(f"DEBUG(test_with_your_sandbox_credentials): secret repr len={len(test_consumer_secret)}")

        # Use requests' HTTPBasicAuth which handles header encoding reliably
        response = requests.get(url, auth=HTTPBasicAuth(test_consumer_key, test_consumer_secret), timeout=10)

        return {
            "your_credentials": {
                "consumer_key": test_consumer_key,
                "consumer_secret": test_consumer_secret
            },
            "response": {
                "status_code": response.status_code,
                "response_text": response.text,
                "success": response.status_code == 200
            }
        }

    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist()
def test_with_known_sandbox_credentials():
    """Test with known working sandbox credentials"""
    try:
        # These are the standard Safaricom sandbox test credentials
        test_consumer_key = "GNArOqtfcHcX9M7rKQ1lGGKzH3V4y9Gv"
        test_consumer_secret = "AqZqJSlDhxHhgbgg"

        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        test_consumer_key = test_consumer_key.strip()
        test_consumer_secret = test_consumer_secret.strip()
        frappe.logger().info(f"DEBUG(test_with_known_sandbox_credentials): key={repr(test_consumer_key)} len={len(test_consumer_key)}")
        response = requests.get(url, auth=HTTPBasicAuth(test_consumer_key, test_consumer_secret), timeout=10)

        return {
            "test_credentials": {
                "consumer_key": test_consumer_key,
                "consumer_secret": test_consumer_secret
            },
            "response": {
                "status_code": response.status_code,
                "response_text": response.text,
                "success": response.status_code == 200
            }
        }

    except Exception as e:
        return {"error": str(e)}

def get_access_token():
    """Get OAuth access token from Daraja API"""
    settings = get_mpesa_settings()
    
    if not settings.is_active:
        frappe.throw("M-Pesa integration is disabled")
    
    # Get consumer_secret from Password field
    consumer_secret = settings.get_password('consumer_secret') if hasattr(settings, 'consumer_secret') else None
    
    if not settings.consumer_key or not consumer_secret:
        frappe.throw("Consumer Key or Consumer Secret is not set in M-Pesa Settings")
    
    # Debug logging and strip credentials to avoid hidden whitespace/newlines
    frappe.logger().info(f"DEBUG: Environment: {settings.environment}")
    ck = settings.consumer_key.strip()
    cs = consumer_secret.strip()
    frappe.logger().info(f"DEBUG: Consumer Key repr: {repr(ck)} len={len(ck)}")
    frappe.logger().info(f"DEBUG: Consumer Secret len={len(cs)} (not printing secret value)")

    # Determine environment
    if settings.environment == "Sandbox":
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    else:
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        frappe.logger().info(f"DEBUG: Making request to: {url}")
        response = requests.get(url, auth=HTTPBasicAuth(ck, cs), timeout=10)
        frappe.logger().info(f"DEBUG: Response status: {response.status_code}")
        frappe.logger().info(f"DEBUG: Response headers: {dict(response.headers)}")
        frappe.logger().info(f"DEBUG: Response text (first 1000 chars): {response.text[:1000]}")

        # Raise for HTTP errors
        response.raise_for_status()

        response_data = response.json()
        access_token = response_data.get("access_token")

        if not access_token:
            frappe.log_error("M-Pesa Auth Error", f"No access token in response: {response_data}")
            frappe.throw("Failed to obtain M-Pesa access token")

        return access_token

    except requests.exceptions.RequestException as e:
        # Build an informative error message including response details when available
        resp = getattr(e, 'response', None)
        status = resp.status_code if resp is not None else 'N/A'
        text = resp.text if resp is not None else ''
        error_msg = f"Failed to get access token: {str(e)} - Status: {status} - Response Text (first 1000): {text[:1000]}"
        frappe.log_error("M-Pesa Auth Error", error_msg)
        frappe.throw(f"M-Pesa authentication failed (status={status}). Check Consumer Key/Secret and environment. See error log for details.")

def format_phone_number(phone):
    """Format phone number to international format"""
    phone = str(phone).strip().replace('+', '').replace(' ', '').replace('-', '')
    
    # Kenyan numbers
    if phone.startswith('07') or phone.startswith('01'):
        return f"254{phone[1:]}"
    elif phone.startswith('7') or phone.startswith('1'):
        return f"254{phone}"
    elif phone.startswith('2547') or phone.startswith('2541'):
        return phone
    else:
        frappe.throw(f"Invalid phone number format: {phone}")

@frappe.whitelist(allow_guest=True)
def stk_callback():
    """Handle STK Push callback from Safaricom"""
    try:
        frappe.set_user("Administrator")
        callback_data = json.loads(frappe.request.data)
        
        frappe.logger().info(f"STK Callback received: {json.dumps(callback_data, indent=2)}")
        
        stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
        merchant_request_id = stk_callback.get("MerchantRequestID")
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        
        frappe.logger().info(f"Looking for transaction with CheckoutRequestID: {checkout_request_id}")
        
        if not frappe.db.exists("Mpesa Transaction", {"checkout_request_id": checkout_request_id}):
            frappe.log_error(f"Transaction not found for CheckoutRequestID: {checkout_request_id}", "STK Callback Error")
            return {"ResultCode": 1, "ResultDesc": "Transaction not found"}
        
        transaction = frappe.get_doc("Mpesa Transaction", {"checkout_request_id": checkout_request_id}, ignore_permissions=True)
        
        frappe.logger().info(f"Found transaction: {transaction.name}")
        
        transaction.result_code = str(result_code)
        transaction.result_desc = result_desc
        transaction.callback_received_at = frappe.utils.now()
        transaction.callback_data = json.dumps(callback_data)
        
        if int(result_code) == 0:
            transaction.status = "Success"
            
            frappe.logger().info(f"Payment successful for transaction {transaction.name}")
            
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            for item in callback_metadata:
                name = item.get("Name")
                value = item.get("Value")
                
                if name == "MpesaReceiptNumber":
                    transaction.mpesa_receipt_number = value
                    frappe.logger().info(f"Receipt Number: {value}")
                elif name == "TransactionDate":
                    if value:
                        transaction.transaction_timestamp = datetime.strptime(str(value), "%Y%m%d%H%M%S")
        else:
            transaction.status = "Failed"
            frappe.logger().info(f"Payment failed for transaction {transaction.name}: {result_desc}")
        
        # Save transaction first before processing subscription
        transaction.save(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.logger().info(f"Transaction {transaction.name} updated to status: {transaction.status}")
        
        # Process subscription upgrade after saving transaction
        if int(result_code) == 0 and transaction.account_reference and "|" in transaction.account_reference:
            try:
                parts = transaction.account_reference.split("|")
                if len(parts) == 2:
                    user_subscription = parts[0]
                    new_subscription = parts[1]
                    
                    frappe.logger().info(f"Processing subscription upgrade for {user_subscription} to {new_subscription}")
                    
                    from tookio_shop.api import process_subscription_upgrade
                    
                    process_subscription_upgrade(user_subscription, new_subscription, transaction.name)
                    frappe.logger().info(f"Subscription upgrade processed successfully")
            except Exception as sub_error:
                frappe.log_error(f"Failed to process subscription upgrade: {str(sub_error)}", "Subscription Upgrade Error")
        
        return {"ResultCode": 0, "ResultDesc": "Success"}
        
    except Exception as e:
        frappe.logger().error(f"STK Callback error: {str(e)}")
        frappe.log_error(f"STK Callback error: {str(e)}\n{frappe.get_traceback()}", "STK Callback Error")
        return {"ResultCode": 1, "ResultDesc": "Internal server error"}

@frappe.whitelist(allow_guest=True)
def timeout_callback():
    """Handle STK Push timeout"""
    try:
        callback_data = json.loads(frappe.request.data)
        
        # Extract timeout info
        checkout_request_id = callback_data.get("CheckoutRequestID")
        
        if checkout_request_id:
            transaction = frappe.get_doc("Mpesa Transaction", {
                "checkout_request_id": checkout_request_id
            })
            
            transaction.status = "Timeout"
            transaction.result_desc = "Transaction timed out"
            transaction.callback_data = json.dumps(callback_data)
            transaction.save()
            frappe.db.commit()
        
        return {"ResultCode": 0, "ResultDesc": "Success"}
        
    except Exception as e:
        frappe.log_error(f"Timeout callback error: {str(e)}")
        return {"ResultCode": 1, "ResultDesc": "Error"}

# --- C2B Simulation for Till (BuyGoods) ---
@frappe.whitelist()
def simulate_c2b_till_payment(phone_number, amount, bill_ref_number=None):
    """Simulate a C2B BuyGoods payment to a Till number (no passkey required)"""
    settings = get_mpesa_settings()
    if not settings.till_number:
        frappe.throw("Till number is not set in Tookio Mpesa Settings")
    access_token = get_access_token()
    # Debug: show token prefix/length and time fetched (do not print full token)
    try:
        frappe.logger().info(f"DEBUG: Fetched access token prefix={access_token[:8]}... len={len(access_token)} at {frappe.utils.now()}")
    except Exception:
        frappe.logger().info("DEBUG: Fetched access token (could not print details)")
    if settings.environment == "Sandbox":
        url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
    else:
        frappe.throw("C2B simulation is only available in Sandbox mode")
    payload = {
        "ShortCode": settings.till_number,
        "CommandID": "CustomerBuyGoodsOnline",
        "Amount": int(float(amount)),
        "Msisdn": format_phone_number(phone_number),
        "BillRefNumber": bill_ref_number or "TILLTEST"
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"C2B Till simulation failed: {str(e)}")
        frappe.throw(f"C2B Till simulation failed: {str(e)}")

@frappe.whitelist()
def test_till_payment(phone_number, amount=1):
    """Test function for Till number payment: uses C2B simulation for BuyGoods (no passkey required)"""
    settings = get_mpesa_settings()
    if not settings.till_number:
        frappe.throw("Till number is not set in Tookio Mpesa Settings")
    return simulate_c2b_till_payment(
        phone_number=phone_number,
        amount=amount,
        bill_ref_number=f"TILL-TEST-{frappe.utils.random_string(5)}"
    )

@frappe.whitelist()
def query_transaction_status(checkout_request_id):
    """Query the status of an STK Push transaction from Safaricom"""
    settings = get_mpesa_settings()
    access_token = get_access_token()
    
    if settings.environment == "Sandbox":
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        business_short_code = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    else:
        url = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        business_short_code = settings.store_number
        passkey = settings.get_password('passkey') if hasattr(settings, 'passkey') else ""

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = f"{business_short_code}{passkey}{timestamp}"
    password = base64.b64encode(password_str.encode('utf-8')).decode('utf-8')

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Update the transaction record based on the query result
        transaction = frappe.get_doc("Mpesa Transaction", {"checkout_request_id": checkout_request_id})
        if transaction:
            result_code = response_data.get("ResultCode")
            result_desc = response_data.get("ResultDesc")
            
            transaction.result_code = result_code
            transaction.result_desc = result_desc
            
            if result_code == "0":  # Success
                transaction.status = "Success"
                # Look for MpesaReceiptNumber in response
                if "MpesaReceiptNumber" in str(response_data):
                    # Extract receipt number from response description or other fields
                    mpesa_receipt = response_data.get("MpesaReceiptNumber")
                    if mpesa_receipt:
                        transaction.mpesa_receipt_number = mpesa_receipt
            else:
                transaction.status = "Failed"
            
            transaction.save()
            frappe.db.commit()
            
            return {
                "success": True,
                "transaction_status": transaction.status,
                "result_code": result_code,
                "result_desc": result_desc,
                "response": response_data
            }
        else:
            return {"success": False, "message": "Transaction not found"}
            
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Transaction status query failed: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def update_pending_transactions():
    """Update all pending STK Push transactions by querying their status"""
    pending_transactions = frappe.get_all(
        "Mpesa Transaction",
        filters={
            "status": "Pending",
            "transaction_type": "STK Push",
            "checkout_request_id": ["!=", ""]
        },
        fields=["name", "checkout_request_id"]
    )
    
    results = []
    for transaction in pending_transactions:
        result = query_transaction_status(transaction.checkout_request_id)
        results.append({
            "transaction_name": transaction.name,
            "checkout_request_id": transaction.checkout_request_id,
            "query_result": result
        })
    
    return results

@frappe.whitelist()
def initiate_stk_push_for_till(phone_number, amount, account_reference, transaction_desc):
    """Initiate STK Push for a Till Number (Buy Goods)."""
    settings = get_mpesa_settings()
    
    # Validate required settings
    if not settings.store_number:
        frappe.throw("Store Number is not set in Tookio Mpesa Settings")
    
    passkey = settings.get_password('passkey') if hasattr(settings, 'passkey') else None
    if not passkey:
        frappe.throw("Passkey is required for STK Push. Please set it in Tookio Mpesa Settings")
    
    frappe.logger().info(f"🔧 STK Push - Store Number: {settings.store_number}, Environment: {settings.environment}")

    access_token = get_access_token()
    
    if settings.environment == "Sandbox":
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        # For sandbox, use the standard test shortcode
        business_short_code = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    else:
        url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        # For production, use store_number for STK Push
        business_short_code = settings.store_number
        passkey = settings.get_password('passkey')

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Use the standard password format: BusinessShortCode + Passkey + Timestamp
    password_str = f"{business_short_code}{passkey}{timestamp}"
    password = base64.b64encode(password_str.encode('utf-8')).decode('utf-8')

    # Ensure callback URL is correctly formed
    if settings.environment == "Sandbox":
        # For sandbox testing, use a valid HTTPS test URL that Safaricom accepts
        # This is a dummy URL for testing - callbacks won't actually reach your local server
        callback_url = "https://mydomain.com/path"  # Safaricom sandbox accepts any valid HTTPS URL format
    else:
        # For production, use your actual site URL (must be HTTPS and publicly accessible)
        callback_url = frappe.utils.get_url("/api/method/tookio_mpesa.utils.stk_callback")
        if not callback_url.startswith('https://'):
            frappe.throw("Production M-Pesa requires HTTPS callback URL. Please configure your site with HTTPS.")
    
    # Determine TransactionType based on environment (matching Navari's implementation)
    if settings.environment == "Sandbox":
        transaction_type = "CustomerPayBillOnline"
        party_b = business_short_code
    else:
        transaction_type = "CustomerBuyGoodsOnline"
        # For Buy Goods (Till), PartyB should be the Till Number
        party_b = settings.till_number if settings.till_number else business_short_code
    
    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": transaction_type,
        "Amount": int(float(amount)),
        "PartyA": format_phone_number(phone_number),
        "PartyB": party_b,
        "PhoneNumber": format_phone_number(phone_number),
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Debug: Log the payload being sent (without sensitive password)
    debug_payload = payload.copy()
    debug_payload['Password'] = f"{debug_payload['Password'][:10]}..." if debug_payload.get('Password') else "None"
    frappe.logger().info(f"DEBUG: STK Payload: {json.dumps(debug_payload, indent=2)}")
    frappe.logger().info(f"DEBUG: STK URL: {url}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        frappe.logger().info(f"📡 M-Pesa Response Status: {response.status_code}")
        frappe.logger().info(f"📡 M-Pesa Response: {response.text[:500]}")
        
        # Handle 500 Internal Server Error
        if response.status_code == 500:
            try:
                error_data = response.json()
                error_code = error_data.get("errorCode", "")
                error_message = error_data.get("errorMessage", "")
                
                if "Merchant does not exist" in error_message or error_code == "500.001.1001":
                    error_msg = f"WRONG BUSINESS SHORTCODE\n\n"
                    error_msg += f"Error: {error_message} (Code: {error_code})\n\n"
                    error_msg += f"The Business Shortcode '{business_short_code}' is NOT registered with your Daraja app.\n\n"
                    error_msg += f"You have these numbers from Safaricom:\n"
                    error_msg += f"   - Store Number: {settings.store_number or 'Not set'}\n"
                    error_msg += f"   - Till Number: {settings.till_number or 'Not set'}\n"
                    error_msg += f"   - Head Office Shortcode: {settings.head_office_shortcode or 'Not set'}\n\n"
                    error_msg += f"SOLUTION:\n"
                    error_msg += f"1. Login to Daraja Portal: https://developer.safaricom.co.ke\n"
                    error_msg += f"2. Go to your PRODUCTION app\n"
                    error_msg += f"3. Find 'Lipa Na M-Pesa Online' section\n"
                    error_msg += f"4. Copy the EXACT Business Shortcode shown there\n"
                    error_msg += f"5. Update 'Store Number' in Tookio Mpesa Settings\n\n"
                    error_msg += f"TIP: For STK Push, you likely need to use HEAD OFFICE SHORTCODE ({settings.head_office_shortcode}),\n"
                    error_msg += f"    NOT the Store Number or Till Number!"
                    
                    frappe.log_error("M-Pesa 500 Error - Wrong Shortcode", error_msg)
                    frappe.throw(
                        f"Wrong Business Shortcode! '{business_short_code}' is not registered with your Daraja app. "
                        f"Try using Head Office Shortcode ({settings.head_office_shortcode}) instead. "
                        f"Check Error Log for detailed instructions."
                    )
                else:
                    # Generic 500 error
                    error_msg = f"M-Pesa API returned 500 Internal Server Error.\n\n"
                    error_msg += f"Response: {response.text}\n\n"
                    error_msg += f"Current Settings:\n"
                    error_msg += f"- Environment: {settings.environment}\n"
                    error_msg += f"- Business Shortcode: {business_short_code}\n"
                    error_msg += f"- Callback URL: {callback_url}\n\n"
                    error_msg += f"Common causes:\n"
                    error_msg += f"1. Invalid Business Shortcode for your credentials\n"
                    error_msg += f"2. Invalid Passkey\n"
                    error_msg += f"3. Shortcode not registered for STK Push"
                    
                    frappe.log_error("M-Pesa 500 Error - Configuration Issue", error_msg)
                    frappe.throw(
                        "M-Pesa payment failed due to configuration error. "
                        "Please check Error Log for details."
                    )
            except json.JSONDecodeError:
                # Couldn't parse JSON response
                error_msg = f"M-Pesa 500 Error - Response: {response.text}"
                frappe.log_error("M-Pesa 500 Error", error_msg)
                frappe.throw("M-Pesa payment failed. Please check Error Log.")
        
        # Handle specific HTTP error codes
        if response.status_code == 404:
            try:
                error_data = response.json()
                error_code = error_data.get("errorCode", "")
                error_message = error_data.get("errorMessage", "")
                
                if "Invalid Access Token" in error_message or error_code == "404.001.03":
                    frappe.log_error("STK Push Configuration Error", 
                        f"STK Push 404 - App likely missing M-Pesa Express product. Error: {error_message}")
                    frappe.throw(
                        "M-Pesa configuration error: Your Daraja app may not have the M-Pesa Express (STK Push) product enabled. "
                        "Please check your Daraja app settings and ensure M-Pesa Express is added to your sandbox app."
                    )
            except json.JSONDecodeError:
                pass
            
            frappe.log_error("STK Push Error", f"STK Push endpoint returned 404: {response.text}")
            frappe.throw("M-Pesa STK Push service is not available. Please check your Daraja app configuration.")
        
        elif response.status_code == 400:
            # Handle 400 Bad Request - usually payload validation errors
            try:
                error_data = response.json()
                error_code = error_data.get("errorCode", "")
                error_message = error_data.get("errorMessage", "")
                request_id = error_data.get("requestId", "")
                
                frappe.log_error("STK Push Validation Error", 
                    f"STK Push 400 - Payload validation failed. Error: {error_message} (Code: {error_code}, RequestID: {request_id})")
                
                # Provide specific guidance based on common errors
                if "Invalid" in error_message and "shortcode" in error_message.lower():
                    frappe.throw(f"M-Pesa Error: Invalid business shortcode. {error_message}")
                elif "Invalid" in error_message and ("phone" in error_message.lower() or "msisdn" in error_message.lower()):
                    frappe.throw(f"M-Pesa Error: Invalid phone number format. {error_message}")
                elif "Invalid" in error_message and "password" in error_message.lower():
                    frappe.throw(f"M-Pesa Error: Invalid password/timestamp. {error_message}")
                else:
                    frappe.throw(f"M-Pesa validation error: {error_message} (Error Code: {error_code})")
                    
            except json.JSONDecodeError:
                frappe.log_error("STK Push Error", f"STK Push 400 with non-JSON response: {response.text}")
                frappe.throw("M-Pesa request validation failed. Please check your configuration.")
        
        response.raise_for_status()
        
        response_data = response.json()
        
        # Create Mpesa Transaction record
        transaction = frappe.new_doc("Mpesa Transaction")
        transaction.transaction_type = "STK Push"
        transaction.amount = int(float(amount))
        transaction.phone_number = format_phone_number(phone_number)
        transaction.account_reference = account_reference
        transaction.transaction_desc = transaction_desc
        transaction.merchant_request_id = response_data.get("MerchantRequestID")
        transaction.checkout_request_id = response_data.get("CheckoutRequestID")
        transaction.response_code = response_data.get("ResponseCode")
        transaction.response_description = response_data.get("ResponseDescription")
        transaction.customer_message = response_data.get("CustomerMessage")
        transaction.status = "Pending"
        transaction.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return response_data
        
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"STK Push failed: {str(e)}")
        frappe.throw(f"STK Push failed: {str(e)}")
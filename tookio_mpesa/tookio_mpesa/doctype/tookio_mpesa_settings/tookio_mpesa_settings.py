import frappe
from frappe.model.document import Document

class TookioMpesaSettings(Document):
    def validate(self):
        # Auto-generate callback URLs
        base_url = frappe.utils.get_url()
        self.callback_url = f"{base_url}/api/method/tookio_mpesa.utils.stk_callback"
        self.timeout_url = f"{base_url}/api/method/tookio_mpesa.utils.timeout_callback" 
        self.result_url = f"{base_url}/api/method/tookio_mpesa.utils.stk_callback"
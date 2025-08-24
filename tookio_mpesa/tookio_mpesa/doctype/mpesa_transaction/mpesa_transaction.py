import frappe
from frappe.model.document import Document
import uuid

class MpesaTransaction(Document):
    def before_insert(self):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())[:12].upper()
    
    def before_save(self):
        # Update timestamps
        if not self.created_at:
            self.created_at = frappe.utils.now()
        self.updated_at = frappe.utils.now()
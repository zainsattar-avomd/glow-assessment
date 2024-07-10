import re
from typing import Optional, Dict, Any

PHONE_PATTERN = re.compile(r'^\d{11}$')
ERROR_INVALID_PHONE = 'Invalid Phone number. Contact should be 11 digits long'
ERROR_INVALID_INDUSTRY = 'This industry cannot be added to the system. Allowed industries: {}'
ERROR_WORKFLOW_COMPLETE = 'Workflow already complete. Current Stage is: {}'
ERROR_ONLY_SALES_APPROVED = 'Only Sales Approved Business can be Won or Lost'
ERROR_INVALID_STAGE = 'Invalid stage.'

class Contact:
    def __init__(self, name: Optional[str] = None, phone: Optional[str] = None):
        self.name = name
        self.phone = phone

    def verify_number(self) -> bool:
        return bool(PHONE_PATTERN.match(self.phone))


class Business:
    valid_industries = ['restaurants', 'stores', 'wholesale', 'services']
    accepted_industries = ['restaurants', 'stores']
    stages = ['New', 'Market Approved', 'Market Declined', 'Sales Approved', 'Won', 'Lost']

    def __init__(self, name: str, fein: str, industry: Optional[str] = None, contact: Optional[Dict[str, str]] = None, stage: str = 'New'):
        self.name = name
        self.fein = fein
        self.industry = industry
        self.contact = Contact(**contact) if contact else Contact()
        self.stage = stage

    def add_to_storage(self, storage: Dict[str, Any]) -> Dict[str, Any]:
        storage[self.fein] = {
            'name': self.name,
            'fein': self.fein,
            'industry': self.industry,
            'contact': {'name': self.contact.name, 'phone': self.contact.phone},
            'stage': self.stage
        }
        return storage

    @staticmethod
    def get_next_step(stage: str) -> Any:
        next_steps = {
            'New': {
                'message': 'Provide a valid industry.',
                'api': '/business/fein_id/industry/',
                'payload': '{"industry": "industry_name"}'
            },
            'Market Approved': {
                'message': 'Provide a valid contact.',
                'api': '/business/fein_id/contact/',
                'payload': '''{"contact":{"name": name, "phone": 11-digit-phone }}'''
            },
            'Sales Approved': {
                'message': 'Move to Won or Lost.',
                'api': '/business/fein_id/complete_process/',
                'payload': '{"stage": "Won|Lost"}'
            },
            'Market Declined': 'No further steps.',
            'Won': 'Workflow complete.',
            'Lost': 'Workflow complete.'
        }
        return next_steps.get(stage, ERROR_INVALID_STAGE)

    def add_industry_and_update_stage(self, industry: str) -> Optional[Dict[str, str]]:
        industry = industry.lower()
        if industry not in self.valid_industries:
            return {'error': ERROR_INVALID_INDUSTRY.format(self.valid_industries)}

        self.industry = industry
        self.stage = 'Market Approved' if industry in self.accepted_industries else 'Market Declined'
        return None

    def add_contact_and_update_stage(self, contact_data: Dict[str, str]) -> Optional[Dict[str, str]]:
        try:
            contact = Contact(**contact_data)
        except TypeError as e:
            return {'error': str(e)}

        self.contact = contact
        if not self.contact.verify_number():
            return {'error': ERROR_INVALID_PHONE}

        if self.stage == 'Market Approved':
            self.stage = 'Sales Approved'
        return None

    def update_stage(self, stage: str) -> Optional[Dict[str, str]]:
        if self.stage in ['Lost', 'Won']:
            return {'error': ERROR_WORKFLOW_COMPLETE.format(self.stage)}

        if self.stage == 'Sales Approved':
            self.stage = stage
        else:
            return {'error': ERROR_ONLY_SALES_APPROVED}
        return None
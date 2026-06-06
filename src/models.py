# src/models.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LeadModel:
    first_name: str
    last_name: str
    company: str
    roles: List[str]
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    street_address: Optional[str] = None
    city: str = "Unknown"
    state: str = "CA"
    linkedin_url: Optional[str] = None

    @property
    def primary_email(self) -> str:
        """Applies business logic to prioritize corporate emails over personal ones."""
        if not self.emails:
            return "no-email@fallback.com"
        
        personal_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        
        # Look for an email that doesn't match a personal domain
        for email in self.emails:
            domain = email.split("@")[-1].lower()
            if domain not in personal_domains:
                return email
                
        # If only personal emails exist, fall back to the first one available
        return self.emails[0]

    @property
    def primary_phone(self) -> str:
        """Returns the first available phone number, or a fallback string."""
        return self.phones[0] if self.phones else "N/A"

    def to_salesforce_payload(self) -> dict:
        """Formats the data model directly into a clean Salesforce REST API dictionary."""
        return {
            "FirstName": self.first_name,
            "LastName": self.last_name,
            "Company": self.company,
            "Title": ", ".join(self.roles),
            "Email": self.primary_email,
            "Phone": self.primary_phone,
            "Street": self.street_address or "N/A",
            "City": self.city,
            "State": self.state,
            "Description": f"Automated Ingestion. LinkedIn: {self.linkedin_url or 'N/A'}"
        }

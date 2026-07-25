from dataclasses import dataclass, asdict


@dataclass
class Business:

    # Google Maps
    name: str = ""
    maps_url: str = ""
    website: str = ""
    phone: str = ""
    address: str = ""

    # Website
    email: str = ""

    # Classification
    business_type: str = "Unknown"
    source: str = "Google Maps"

    # Rule Engine
    rule_score: int = 0

    # Status
    is_open: bool = True
    approved: bool = False
    status: str = "pending"

    def to_dict(self):
        return asdict(self)

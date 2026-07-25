from models.business import Business


class RuleEngine:

    DEALER_KEYWORDS = [
        " bmw of ",
        " mercedes-benz of ",
        " mercedes of ",
        " audi of ",
        " porsche ",
        " lexus of ",
        " toyota of ",
        " honda of ",
        " ford of ",
        " chevrolet ",
        " cadillac ",
        " buick ",
        " gmc ",
        " jeep ",
        " dodge ",
        " chrysler ",
        " ram ",
        " kia ",
        " hyundai ",
        " genesis ",
        " nissan ",
        " infiniti ",
        " acura ",
        " mazda ",
        " subaru ",
        " volkswagen ",
        " volvo ",
        " land rover ",
        " jaguar ",
    ]

    DEALER_WEBSITES = [
        "dealer.com",
        "dealeron.com",
        "autonation.com",
        "group1auto.com",
        "lithia.com",
        "hendrickcars.com",
        "sonicautomotive.com",
        "autoweb.com",
        "driveway.com",
    ]

    @classmethod
    def score(cls, business: Business):

        score = 0

        name = (business.name or "").lower()
        website = (business.website or "").lower()

        if business.website:
            score += 20

        if business.email:
            score += 20

        if business.is_open:
            score += 10

        if any(k in f" {name} " for k in cls.DEALER_KEYWORDS):
            score -= 100

        if any(domain in website for domain in cls.DEALER_WEBSITES):
            score -= 100

        business.rule_score = score

        return score

    @classmethod
    def should_skip(cls, business: Business):

        cls.score(business)

        return business.rule_score < 0

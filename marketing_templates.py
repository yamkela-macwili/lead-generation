"""
Marketing Templates and Sales Automation for Lead Generation System
Based on design_2.md specifications
"""

from config import BUSINESS_CONTACT, PRICES, PACKAGE_LEADS

# WhatsApp Business Template
WHATSAPP_BUSINESS_TEMPLATE = """
*🚀 READY-TO-CONTACT LEADS AVAILABLE!*

Hi {business_name}, I specialize in generating *qualified local leads* for {niche}.

Right now I have *fresh leads* including:
• {lead_count} potential customers in {area}
• Phone numbers & contact details
• People actively looking for your services

*Package Options:*
🥉 BASIC: {basic_leads} leads - R{basic_price}
🥈 STANDARD: {standard_leads} leads - R{standard_price}
🥇 PREMIUM: {premium_leads} leads + analytics - R{premium_price}

*Next Steps:*
1. Reply "SAMPLE" for free sample leads
2. Choose your package
3. Receive leads instantly via WhatsApp

Stop searching for clients - let them find you! 💼

For inquiries: {contact_name} | {contact_phone} | {contact_email}
"""

# Facebook Marketplace Post
FACEBOOK_MARKETPLACE_POST = """
**PROFESSIONAL LEAD LISTS - GET NEW CLIENTS THIS WEEK!**

Tired of spending hours looking for customers? I provide ready-to-contact lead lists for local businesses:

🎯 **SPECIALIZING IN:**
• Real Estate Agents
• Tutors & Coaches
• Plumbers & Electricians
• Home Service Providers

**📦 PACKAGES AVAILABLE:**
• BASIC ({basic_leads} leads) - R{basic_price}
• STANDARD ({standard_leads} leads) - R{standard_price}
• PREMIUM ({premium_leads} leads with analytics) - R{premium_price}

**✅ WHAT YOU GET:**
• Verified phone numbers
• Email addresses
• Location data
• Immediate delivery
• 100% public data (legal & ethical)

**💬 HOW TO ORDER:**
1. Message me your business type
2. Choose your package
3. Make payment via EFT
4. Receive leads instantly!

*"Bought the premium package and got 3 new clients in 2 days!" - Satisfied Customer*

Comment "LEADS" below and I'll send you a free sample! 🚀
"""

# Follow-Up Sequence
FOLLOW_UP_SEQUENCE = [
    {
        'day': 1,
        'message': "Hi {business_name}, thanks for your interest! Here's a free sample of {sample_count} leads for {niche}. Reply with your package choice to get started!"
    },
    {
        'day': 2,
        'message': "Good day {business_name}! Did you get a chance to check the sample leads? Any questions about our packages?"
    },
    {
        'day': 3,
        'message': "Limited time: 10% off your first package! {business_name}, ready to get {lead_count} quality leads?"
    },
    {
        'day': 5,
        'message': "Success story: One of my clients got 5 new customers this week! {business_name}, your turn?"
    },
    {
        'day': 7,
        'message': "Final reminder: {business_name}, don't miss out on fresh leads. Special bonus: Free updates for 1 month!"
    }
]

def get_whatsapp_template(business_name, niche, area, lead_count=50):
    """Generate personalized WhatsApp message."""
    return WHATSAPP_BUSINESS_TEMPLATE.format(
        business_name=business_name,
        niche=niche.replace('_', ' '),
        lead_count=lead_count,
        area=area,
        basic_leads=PACKAGE_LEADS['basic'],
        standard_leads=PACKAGE_LEADS['standard'],
        premium_leads=PACKAGE_LEADS['premium'],
        basic_price=PRICES['basic'],
        standard_price=PRICES['standard'],
        premium_price=PRICES['premium'],
        contact_name=BUSINESS_CONTACT['name'],
        contact_phone=BUSINESS_CONTACT['phone'],
        contact_email=BUSINESS_CONTACT['email']
    )

def get_facebook_post():
    """Get Facebook marketplace post template."""
    return FACEBOOK_MARKETPLACE_POST.format(
        basic_leads=PACKAGE_LEADS['basic'],
        standard_leads=PACKAGE_LEADS['standard'],
        premium_leads=PACKAGE_LEADS['premium'],
        basic_price=PRICES['basic'],
        standard_price=PRICES['standard'],
        premium_price=PRICES['premium']
    )

def get_follow_up_message(day, business_name, niche, lead_count=50, sample_count=5):
    """Get follow-up message for specific day."""
    template = next((msg for msg in FOLLOW_UP_SEQUENCE if msg['day'] == day), None)
    if template:
        return template['message'].format(
            business_name=business_name,
            niche=niche.replace('_', ' '),
            lead_count=lead_count,
            sample_count=sample_count
        )
    return None

# Sample usage
if __name__ == '__main__':
    print("WhatsApp Template:")
    print(get_whatsapp_template("ABC Realty", "real_estate_agents", "Johannesburg"))

    print("\nFacebook Post:")
    print(get_facebook_post())

    print("\nFollow-up Day 1:")
    print(get_follow_up_message(1, "ABC Realty", "real_estate_agents"))

# Configuration for the Lead Generation Project

# Available niches for targeting
NICHE_OPTIONS = {
    'real_estate_agents': 'real estate agents',
    'tutors_education': 'tutors & education',
    'service_providers': 'service providers',
    'healthcare_professionals': 'healthcare professionals'
}

# Selected niche (can be changed when running the script)
SELECTED_NICHE = 'real_estate_agents'  # Default

# Number of leads per package
PACKAGE_LEADS = {
    'basic': 50,
    'standard': 100,  # Updated to match design (100-150, using 100)
    'premium': 200   # Updated to match design (200+)
}

# Pricing (in ZAR)
PRICES = {
    'basic': 300,
    'standard': 500,
    'premium': 800
}

# Target region
TARGET_REGION = 'South Africa'

# Ethical scraping settings
RATE_LIMIT_SECONDS = 2  # 1 request per 2 seconds
RESPECT_ROBOTS_TXT = True
CACHE_ENABLED = True
DESCRIPTIVE_USER_AGENT = 'LeadGenerationBot/1.0 (Educational Research; contact@yamkela-macwili.com)'

# Package features
PACKAGE_FEATURES = {
    'basic': ['PDF report', 'Basic contact info', '3-day freshness'],
    'standard': ['PDF + Excel', 'Enhanced details', 'Lead categorization', '2-day freshness'],
    'premium': ['PDF + Excel + Analytics', 'Response predictions', 'Geographic heat maps', 'Competitor analysis', '24-hour freshness']
}

# Niche-specific data sources
NICHE_SOURCES = {
    'real_estate_agents': [
        {
            'name': 'Property24',
            'url': 'https://www.property24.com',
            'search_path': '/agents/search?sp=s%3D{region}'
        },
        {
            'name': 'Private Property',
            'url': 'https://www.privateproperty.co.za',
            'search_path': '/estate-agents/search?location={region}'
        },
        {
            'name': 'Gumtree Property',
            'url': 'https://www.gumtree.co.za',
            'search_path': '/s-property/v1c9071l3100001'
        }
    ],
    'tutors_education': [
        {
            'name': 'TutorExtra South Africa',
            'url': 'https://www.tutorextra.co.za',
            'search_path': '/tutors/{region}'
        },
        {
            'name': 'SmartKids Tutors',
            'url': 'https://www.smartkids.co.za',
            'search_path': '/find-tutors?location={region}'
        }
    ],
    'service_providers': [
        {
            'name': 'HelloPeter',
            'url': 'https://www.hellopeter.com',
            'search_path': '/search?q={query}&location={region}'
        },
        {
            'name': 'The Blue Pages',
            'url': 'https://www.thebluepages.co.za',
            'search_path': '/search?what={query}&where={region}'
        },
        {
            'name': 'SA Services Guide',
            'url': 'https://www.saservicesguide.co.za',
            'search_path': '/directory/{query}'
        }
    ],
    'healthcare_professionals': [
        {
            'name': 'HelloDoctor',
            'url': 'https://www.hellodoctor.co.za',
            'search_path': '/find-doctors?location={region}'
        },
        {
            'name': 'MedicalAid.co.za',
            'url': 'https://www.medicalaid.co.za',
            'search_path': '/providers/search?location={region}'
        },
        {
            'name': 'Health24 Practitioners',
            'url': 'https://www.health24.com',
            'search_path': '/medical/practitioners/{region}'
        }
    ]
}

# Category mappings for sources that use category IDs (like Yep)
CATEGORY_MAPPINGS = {
    'real_estate': '81517',  # Property & Real Estate
    'car_dealers': '81479',  # Automotive
    'tutors': '81601',       # Education & Training
    'plumbers': '81553',     # Construction & Trades
    'marketers': '81485',    # Business Services
    'home_services': '81561' # Home Services
}

# Minimum leads required per source before moving to next
MIN_LEADS_PER_SOURCE = 10

# Output directories
REPORTS_DIR = 'reports/'
EXPORTS_DIR = 'exports/'

# Contact info for footer
BUSINESS_CONTACT = {
    'name': 'Yamkela Macwili',
    'phone': '+27 12 345 6789', 
    'email': 'leadgen@gmail.com'
}

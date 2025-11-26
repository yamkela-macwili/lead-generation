# Configuration for the Lead Generation Project

# Available niches for targeting
NICHE_OPTIONS = {
    'real_estate': 'real estate agents',
    'car_dealers': 'car dealers',
    'tutors': 'tutors',
    'plumbers': 'plumbers and electricians',
    'marketers': 'marketers',
    'home_services': 'home service providers'
}

# Selected niche (can be changed when running the script)
SELECTED_NICHE = 'real_estate'  # Default

# Number of leads per package
PACKAGE_LEADS = {
    'basic': 50,
    'standard': 150,
    'premium': 250
}

# Pricing (in ZAR)
PRICES = {
    'basic': 300,
    'standard': 500,
    'premium': 800
}

# Target region (e.g., 'Lesotho', 'South Africa')
TARGET_REGION = 'South Africa'

# Multiple South African business directories to try
SCRAPER_SOURCES = [
    {
        'name': 'Yellow Pages SA',
        'url': 'https://www.yellowpages.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'Digital Directory',
        'url': 'https://digitaldirectory.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'South African Listings',
        'url': 'https://southafricanlistings.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'Business Directory SA',
        'url': 'https://businessdirectory.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'SA Business Listings',
        'url': 'https://sabusinesslistings.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'EEZIADS',
        'url': 'https://www.eeziads.co.za',
        'search_path': '/wbusiness.php?what={query}&where={region}'
    },
    {
        'name': 'Niche Market',
        'url': 'https://nichemarket.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'Brabys',
        'url': 'https://brabys.com',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'Hotfrog SA',
        'url': 'https://hotfrog.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'YelloSA',
        'url': 'https://yellosa.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'ShowMe',
        'url': 'https://showme.co.za',
        'search_path': '/search?what={query}&where={region}'
    },
    {
        'name': 'Yep',
        'url': 'https://www.yep.co.za',
        'search_path': '/search?category={category}&place={region}'
    }
]

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

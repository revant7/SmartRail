#!/usr/bin/env python
"""
Setup script to initialize the database with required data for the QRAIL system.
"""
import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qrail.settings_local")
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from django.utils import timezone
from railway.models import RailwayZone, RailwayDivision, RailwayLocation
from parts.models import PartCategory

User = get_user_model()

# Function to create users of different types
def create_users():
    """Create sample users for each user type."""
    users = [
        # Staff user
        {
            'username': 'staff_user',
            'password': 'Staff@123',
            'email': 'staff@qrailway.com',
            'first_name': 'Staff',
            'last_name': 'User',
            'user_type': 'SOFTWARE_STAFF',
            'employee_id': 'STAFF001',
            'phone_number': '+919876543210',
            'department': 'IT',
            'designation': 'System Administrator',
            'is_verified': True,
            'is_staff': True,
        },
        # Railway Authority user
        {
            'username': 'railway_authority',
            'password': 'Authority@123',
            'email': 'authority@qrailway.com',
            'first_name': 'Railway',
            'last_name': 'Authority',
            'user_type': 'RAILWAY_AUTHORITY',
            'employee_id': 'AUTH001',
            'phone_number': '+919876543211',
            'department': 'Railway Management',
            'designation': 'Chief Inspector',
            'is_verified': True,
        },
        # Vendor user
        {
            'username': 'vendor_user',
            'password': 'Vendor@123',
            'email': 'vendor@qrailway.com',
            'first_name': 'Vendor',
            'last_name': 'Company',
            'user_type': 'VENDOR',
            'employee_id': 'VEND001',
            'phone_number': '+919876543212',
            'department': 'Supply Chain',
            'designation': 'Parts Supplier',
            'is_verified': True,
        },
        # Railway Worker user
        {
            'username': 'railway_worker',
            'password': 'Worker@123',
            'email': 'worker@qrailway.com',
            'first_name': 'Railway',
            'last_name': 'Worker',
            'user_type': 'RAILWAY_WORKER',
            'employee_id': 'WORK001',
            'phone_number': '+919876543213',
            'department': 'Maintenance',
            'designation': 'Field Technician',
            'is_verified': True,
        },
    ]
    
    created_users = []
    for user_data in users:
        password = user_data.pop('password')
        user, created = User.objects.update_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        
        # Set password if user was created or updated
        user.set_password(password)
        user.save()
        
        status = "Created" if created else "Updated"
        print(f"{status} user: {user.username} ({user.get_user_type_display()})")
        created_users.append(user)
    
    return created_users


# Function to create railway zones
def create_railway_zones():
    """Create Indian railway zones."""
    zones = [
        {
            'zone_code': 'CR',
            'name': 'Central Railway',
            'headquarters': 'Mumbai',
            'description': 'Covers Maharashtra, parts of MP and Karnataka',
            'jurisdiction': 'Mumbai, Pune, Nagpur, Bhusaval, Solapur divisions',
        },
        {
            'zone_code': 'ER',
            'name': 'Eastern Railway',
            'headquarters': 'Kolkata',
            'description': 'Covers West Bengal and parts of Bihar, Jharkhand',
            'jurisdiction': 'Howrah, Sealdah, Asansol, Malda divisions',
        },
        {
            'zone_code': 'ECR',
            'name': 'East Central Railway',
            'headquarters': 'Hajipur',
            'description': 'Covers Bihar, Jharkhand and parts of UP',
            'jurisdiction': 'Danapur, Dhanbad, Mughalsarai, Samastipur, Sonpur divisions',
        },
        {
            'zone_code': 'ECoR',
            'name': 'East Coast Railway',
            'headquarters': 'Bhubaneswar',
            'description': 'Covers Odisha and parts of Andhra Pradesh',
            'jurisdiction': 'Khurda Road, Sambalpur, Waltair divisions',
        },
        {
            'zone_code': 'NR',
            'name': 'Northern Railway',
            'headquarters': 'New Delhi',
            'description': 'Covers Delhi, Haryana, Punjab, UP and J&K',
            'jurisdiction': 'Delhi, Ambala, Firozpur, Lucknow, Moradabad divisions',
        },
        {
            'zone_code': 'NCR',
            'name': 'North Central Railway',
            'headquarters': 'Prayagraj',
            'description': 'Covers parts of UP and MP',
            'jurisdiction': 'Prayagraj, Agra, Jhansi divisions',
        },
        {
            'zone_code': 'NER',
            'name': 'North Eastern Railway',
            'headquarters': 'Gorakhpur',
            'description': 'Covers northeastern UP and western Bihar',
            'jurisdiction': 'Lucknow, Varanasi, Izzatnagar divisions',
        },
        {
            'zone_code': 'NFR',
            'name': 'Northeast Frontier Railway',
            'headquarters': 'Guwahati',
            'description': 'Covers Northeast India',
            'jurisdiction': 'Katihar, Alipurduar, Rangiya, Lumding, Tinsukia divisions',
        },
        {
            'zone_code': 'NWR',
            'name': 'North Western Railway',
            'headquarters': 'Jaipur',
            'description': 'Covers Rajasthan and parts of Gujarat, Haryana and Punjab',
            'jurisdiction': 'Jaipur, Ajmer, Bikaner, Jodhpur divisions',
        },
        {
            'zone_code': 'SR',
            'name': 'Southern Railway',
            'headquarters': 'Chennai',
            'description': 'Covers Tamil Nadu and parts of Kerala, AP and Karnataka',
            'jurisdiction': 'Chennai, Madurai, Palakkad, Salem, Tiruchchirapalli, Thiruvananthapuram divisions',
        },
        {
            'zone_code': 'SCR',
            'name': 'South Central Railway',
            'headquarters': 'Secunderabad',
            'description': 'Covers Telangana and parts of Maharashtra, Karnataka, AP',
            'jurisdiction': 'Secunderabad, Hyderabad, Vijayawada, Guntakal, Guntur, Nanded divisions',
        },
        {
            'zone_code': 'SER',
            'name': 'South Eastern Railway',
            'headquarters': 'Kolkata',
            'description': 'Covers parts of West Bengal, Jharkhand and Odisha',
            'jurisdiction': 'Adra, Chakradharpur, Kharagpur, Ranchi divisions',
        },
        {
            'zone_code': 'SECR',
            'name': 'South East Central Railway',
            'headquarters': 'Bilaspur',
            'description': 'Covers parts of Chhattisgarh, MP and Maharashtra',
            'jurisdiction': 'Bilaspur, Raipur, Nagpur divisions',
        },
        {
            'zone_code': 'SWR',
            'name': 'South Western Railway',
            'headquarters': 'Hubli',
            'description': 'Covers Karnataka and parts of Goa',
            'jurisdiction': 'Hubli, Bangalore, Mysore divisions',
        },
        {
            'zone_code': 'WR',
            'name': 'Western Railway',
            'headquarters': 'Mumbai',
            'description': 'Covers Gujarat, parts of Rajasthan and Maharashtra',
            'jurisdiction': 'Mumbai Central, Vadodara, Ahmedabad, Rajkot, Bhavnagar, Ratlam divisions',
        },
        {
            'zone_code': 'WCR',
            'name': 'West Central Railway',
            'headquarters': 'Jabalpur',
            'description': 'Covers parts of MP and Maharashtra',
            'jurisdiction': 'Jabalpur, Bhopal, Kota divisions',
        },
    ]
    
    created_zones = []
    for zone_data in zones:
        zone, created = RailwayZone.objects.update_or_create(
            zone_code=zone_data['zone_code'],
            defaults=zone_data
        )
        
        status = "Created" if created else "Updated"
        print(f"{status} railway zone: {zone.name}")
        created_zones.append(zone)
    
    return created_zones


# Function to create railway divisions
def create_railway_divisions(zones):
    """Create railway divisions for each zone."""
    # Dictionary mapping zone codes to their divisions
    zone_divisions = {
        'CR': [
            {'division_code': 'PUNE', 'name': 'Pune Division', 'headquarters': 'Pune'},
            {'division_code': 'NGPR', 'name': 'Nagpur Division', 'headquarters': 'Nagpur'},
            {'division_code': 'BHSL', 'name': 'Bhusaval Division', 'headquarters': 'Bhusaval'},
            {'division_code': 'SLPR', 'name': 'Solapur Division', 'headquarters': 'Solapur'},
            {'division_code': 'MMCT', 'name': 'Mumbai Division', 'headquarters': 'Mumbai'},
        ],
        'NR': [
            {'division_code': 'DLI', 'name': 'Delhi Division', 'headquarters': 'Delhi'},
            {'division_code': 'AMBLA', 'name': 'Ambala Division', 'headquarters': 'Ambala'},
            {'division_code': 'FZR', 'name': 'Firozpur Division', 'headquarters': 'Firozpur'},
            {'division_code': 'LKO', 'name': 'Lucknow Division', 'headquarters': 'Lucknow'},
            {'division_code': 'MB', 'name': 'Moradabad Division', 'headquarters': 'Moradabad'},
        ],
        'SR': [
            {'division_code': 'MAS', 'name': 'Chennai Division', 'headquarters': 'Chennai'},
            {'division_code': 'MDU', 'name': 'Madurai Division', 'headquarters': 'Madurai'},
            {'division_code': 'PGT', 'name': 'Palakkad Division', 'headquarters': 'Palakkad'},
            {'division_code': 'SA', 'name': 'Salem Division', 'headquarters': 'Salem'},
            {'division_code': 'TPJ', 'name': 'Tiruchchirapalli Division', 'headquarters': 'Tiruchchirapalli'},
            {'division_code': 'TVC', 'name': 'Thiruvananthapuram Division', 'headquarters': 'Thiruvananthapuram'},
        ],
    }
    
    created_divisions = []
    # Create divisions for selected zones
    for zone in zones:
        if zone.zone_code in zone_divisions:
            divisions_data = zone_divisions[zone.zone_code]
            for division_data in divisions_data:
                division_data['zone'] = zone
                division_data['jurisdiction'] = f"Jurisdiction of {division_data['name']}"
                
                division, created = RailwayDivision.objects.update_or_create(
                    division_code=division_data['division_code'],
                    defaults=division_data
                )
                
                status = "Created" if created else "Updated"
                print(f"{status} railway division: {division.name} ({zone.name})")
                created_divisions.append(division)
    
    return created_divisions


# Function to create railway locations
def create_railway_locations(divisions):
    """Create railway locations for each division."""
    # Dictionary mapping division codes to their locations
    division_locations = {
        'PUNE': [
            {'location_code': 'PUNE', 'name': 'Pune Railway Station', 'location_type': 'STATION'},
            {'location_code': 'SVJR', 'name': 'Shivajinagar', 'location_type': 'STATION'},
            {'location_code': 'KK', 'name': 'Khadki', 'location_type': 'STATION'},
            {'location_code': 'DAPD', 'name': 'Dapodi', 'location_type': 'STATION'},
            {'location_code': 'PCMC', 'name': 'Pimpri-Chinchwad', 'location_type': 'STATION'},
        ],
        'DLI': [
            {'location_code': 'NDLS', 'name': 'New Delhi Railway Station', 'location_type': 'STATION'},
            {'location_code': 'DLI', 'name': 'Delhi Railway Station', 'location_type': 'STATION'},
            {'location_code': 'NZM', 'name': 'Hazrat Nizamuddin', 'location_type': 'STATION'},
            {'location_code': 'DEC', 'name': 'Delhi Cantt', 'location_type': 'STATION'},
            {'location_code': 'SZM', 'name': 'Sabzi Mandi', 'location_type': 'STATION'},
        ],
        'MAS': [
            {'location_code': 'MAS', 'name': 'Chennai Central', 'location_type': 'STATION'},
            {'location_code': 'MS', 'name': 'Chennai Egmore', 'location_type': 'STATION'},
            {'location_code': 'TBM', 'name': 'Tambaram', 'location_type': 'STATION'},
            {'location_code': 'BBQ', 'name': 'Basin Bridge Junction', 'location_type': 'JUNCTION'},
            {'location_code': 'MASS', 'name': 'Chennai Beach', 'location_type': 'STATION'},
        ],
    }
    
    created_locations = []
    # Create locations for selected divisions
    for division in divisions:
        if division.division_code in division_locations:
            locations_data = division_locations[division.division_code]
            for location_data in locations_data:
                location_data['division'] = division
                
                location, created = RailwayLocation.objects.update_or_create(
                    location_code=location_data['location_code'],
                    defaults=location_data
                )
                
                status = "Created" if created else "Updated"
                print(f"{status} railway location: {location.name} ({division.name})")
                created_locations.append(location)
    
    return created_locations


# Function to create part categories
def create_part_categories():
    """Create railway part categories."""
    categories = [
        {
            'name': 'Liners',
            'description': 'Track liners for railway maintenance',
            'parent_category': None,
        },
        {
            'name': 'Pads',
            'description': 'Rail pads used between rails and sleepers',
            'parent_category': None,
        },
        {
            'name': 'Clips',
            'description': 'Rail clips for fastening rails to sleepers',
            'parent_category': None,
        },
    ]
    
    # First, create all parent categories
    parent_categories = {}
    created_categories = []
    
    # First pass - create parent categories
    for category_data in categories:
        if category_data.get('parent_category') is None and 'parent_category_name' not in category_data:
            category, created = PartCategory.objects.update_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'parent_category': None
                }
            )
            parent_categories[category.name] = category
            
            status = "Created" if created else "Updated"
            print(f"{status} part category: {category.name}")
            created_categories.append(category)
    
    # Second pass - create subcategories
    for category_data in categories:
        if 'parent_category_name' in category_data:
            parent_name = category_data.pop('parent_category_name')
            if parent_name in parent_categories:
                category_data['parent_category'] = parent_categories[parent_name]
                
                category, created = PartCategory.objects.update_or_create(
                    name=category_data['name'],
                    defaults=category_data
                )
                
                status = "Created" if created else "Updated"
                print(f"{status} part subcategory: {category.name} (parent: {parent_name})")
                created_categories.append(category)
    
    return created_categories


# Main execution
if __name__ == "__main__":
    print("Setting up initial data for the QRAIL system...")
    
    # Create users
    print("\nCreating users...")
    users = create_users()
    
    # Create railway zones
    print("\nCreating railway zones...")
    zones = create_railway_zones()
    
    # Create railway divisions
    print("\nCreating railway divisions...")
    divisions = create_railway_divisions(zones)
    
    # Create railway locations
    print("\nCreating railway locations...")
    locations = create_railway_locations(divisions)
    
    # Create part categories
    print("\nCreating part categories...")
    categories = create_part_categories()
    
    print("\nSetup completed successfully!")

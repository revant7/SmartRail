#!/usr/bin/env python
"""
Script to add divisions and locations for NCR (North Central Railway)
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrail.settings')
django.setup()

from railway.models import RailwayZone, RailwayDivision, RailwayLocation

def add_ncr_divisions_and_locations():
    print("Adding NCR Divisions and Locations...")
    
    # Get NCR Zone
    ncr = RailwayZone.objects.filter(zone_code='NCR').first()
    if not ncr:
        print("Error: NCR zone not found. Please create it first.")
        return
    
    # Add Divisions
    divisions = [
        {'code': 'PRYJ', 'name': 'Prayagraj Division'},
        {'code': 'AGC', 'name': 'Agra Division'},
        {'code': 'JHS', 'name': 'Jhansi Division'}
    ]
    
    division_objs = {}
    for div in divisions:
        division, created = RailwayDivision.objects.get_or_create(
            division_code=div['code'],
            defaults={'name': div['name'], 'zone': ncr}
        )
        if created:
            print(f"Created division: {division.name}")
        else:
            print(f"Division {division.name} already exists")
        division_objs[div['code']] = division
    
    # Add Locations
    locations = {
        'PRYJ': [
            {'code': 'PRYJ', 'name': 'Prayagraj Junction'},
            {'code': 'CNB', 'name': 'Kanpur Central'},
            {'code': 'FTP', 'name': 'Fatehpur'},
            {'code': 'ETW', 'name': 'Etawah'},
        ],
        'AGC': [
            {'code': 'AGC', 'name': 'Agra Cantt'},
            {'code': 'MTJ', 'name': 'Mathura Junction'},
            {'code': 'ALJN', 'name': 'Aligarh Junction'},
            {'code': 'TDL', 'name': 'Tundla Junction'},
        ],
        'JHS': [
            {'code': 'JHS', 'name': 'Jhansi Junction'},
            {'code': 'BNDA', 'name': 'Banda Junction'},
            {'code': 'GWL', 'name': 'Gwalior Junction'},
            {'code': 'ORAI', 'name': 'Orai'},
        ],
    }
    
    location_count = 0
    for div_code, locs in locations.items():
        division = division_objs.get(div_code)
        if not division:
            print(f"Error: Division {div_code} not found, skipping its locations")
            continue
            
        for loc in locs:
            location, created = RailwayLocation.objects.get_or_create(
                location_code=loc['code'],
                defaults={'name': loc['name'], 'division': division}
            )
            if created:
                location_count += 1
                print(f"Created location: {location.name} ({location.location_code})")
            else:
                print(f"Location {location.name} already exists")
    
    print(f"Added {len(division_objs)} divisions and {location_count} locations for NCR")

if __name__ == "__main__":
    add_ncr_divisions_and_locations()

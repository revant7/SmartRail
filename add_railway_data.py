#!/usr/bin/env python
"""
Script to add divisions and locations for all major Indian Railway Zones
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrail.settings')
django.setup()

from railway.models import RailwayZone, RailwayDivision, RailwayLocation

def add_railway_divisions_and_locations():
    """Add divisions and locations for all major Indian Railway zones"""
    
    print("Adding Divisions and Locations for all Railway Zones...")
    
    # Dictionary mapping zone codes to their divisions and locations
    railway_data = {
        # Central Railway (CR)
        'CR': {
            'divisions': [
                {'code': 'BB', 'name': 'Mumbai Division'},
                {'code': 'BSL', 'name': 'Bhusaval Division'},
                {'code': 'NGP', 'name': 'Nagpur Division'},
                {'code': 'PA', 'name': 'Pune Division'},
                {'code': 'SUR', 'name': 'Solapur Division'},
            ],
            'locations': {
                'BB': [
                    {'code': 'CSMT', 'name': 'Chhatrapati Shivaji Maharaj Terminus'},
                    {'code': 'DR', 'name': 'Dadar'},
                    {'code': 'KYN', 'name': 'Kalyan Junction'},
                    {'code': 'TNA', 'name': 'Thane'},
                ],
                'BSL': [
                    {'code': 'BSL', 'name': 'Bhusaval Junction'},
                    {'code': 'MMR', 'name': 'Manmad Junction'},
                    {'code': 'JL', 'name': 'Jalgaon Junction'},
                ],
                'NGP': [
                    {'code': 'NGP', 'name': 'Nagpur Junction'},
                    {'code': 'AQ', 'name': 'Ajni'},
                    {'code': 'SEGM', 'name': 'Sewagram Junction'},
                ],
                'PA': [
                    {'code': 'PUNE', 'name': 'Pune Junction'},
                    {'code': 'SVJR', 'name': 'Shivajinagar'},
                    {'code': 'LNL', 'name': 'Lonavala'},
                ],
                'SUR': [
                    {'code': 'SUR', 'name': 'Solapur Junction'},
                    {'code': 'DD', 'name': 'Daund Junction'},
                    {'code': 'KWV', 'name': 'Kurduvadi Junction'},
                ],
            }
        },
        
        # Eastern Railway (ER)
        'ER': {
            'divisions': [
                {'code': 'HWH', 'name': 'Howrah Division'},
                {'code': 'SDAH', 'name': 'Sealdah Division'},
                {'code': 'ASN', 'name': 'Asansol Division'},
                {'code': 'MLDT', 'name': 'Malda Division'},
            ],
            'locations': {
                'HWH': [
                    {'code': 'HWH', 'name': 'Howrah Junction'},
                    {'code': 'BDC', 'name': 'Bandel Junction'},
                    {'code': 'BWN', 'name': 'Barddhaman Junction'},
                ],
                'SDAH': [
                    {'code': 'SDAH', 'name': 'Sealdah'},
                    {'code': 'KOAA', 'name': 'Kolkata'},
                    {'code': 'NH', 'name': 'Naihati Junction'},
                ],
                'ASN': [
                    {'code': 'ASN', 'name': 'Asansol Junction'},
                    {'code': 'DHN', 'name': 'Dhanbad Junction'},
                    {'code': 'UDL', 'name': 'Andal Junction'},
                ],
                'MLDT': [
                    {'code': 'MLDT', 'name': 'Malda Town'},
                    {'code': 'NJP', 'name': 'New Jalpaiguri'},
                    {'code': 'RNI', 'name': 'Rampurhat'},
                ],
            }
        },
        
        # Northern Railway (NR)
        'NR': {
            'divisions': [
                {'code': 'DLI', 'name': 'Delhi Division'},
                {'code': 'FZR', 'name': 'Firozpur Division'},
                {'code': 'LKO', 'name': 'Lucknow Division'},
                {'code': 'MB', 'name': 'Moradabad Division'},
                {'code': 'UMB', 'name': 'Ambala Division'},
            ],
            'locations': {
                'DLI': [
                    {'code': 'NDLS', 'name': 'New Delhi'},
                    {'code': 'DLI', 'name': 'Old Delhi Junction'},
                    {'code': 'NZM', 'name': 'Hazrat Nizamuddin'},
                ],
                'FZR': [
                    {'code': 'FZR', 'name': 'Firozpur Cantt'},
                    {'code': 'ASR', 'name': 'Amritsar Junction'},
                    {'code': 'JUC', 'name': 'Jalandhar City Junction'},
                ],
                'LKO': [
                    {'code': 'LKO', 'name': 'Lucknow Charbagh'},
                    {'code': 'BE', 'name': 'Bareilly Junction'},
                    {'code': 'SRE', 'name': 'Shahjahanpur'},
                ],
                'MB': [
                    {'code': 'MB', 'name': 'Moradabad Junction'},
                    {'code': 'CDG', 'name': 'Chandigarh Junction'},
                    {'code': 'SRE', 'name': 'Saharanpur Junction'},
                ],
                'UMB': [
                    {'code': 'UMB', 'name': 'Ambala Cantt Junction'},
                    {'code': 'KUN', 'name': 'Kalka'},
                    {'code': 'PNP', 'name': 'Panipat Junction'},
                ],
            }
        },
        
        # Southern Railway (SR)
        'SR': {
            'divisions': [
                {'code': 'MAS', 'name': 'Chennai Division'},
                {'code': 'MDU', 'name': 'Madurai Division'},
                {'code': 'PGT', 'name': 'Palakkad Division'},
                {'code': 'SA', 'name': 'Salem Division'},
                {'code': 'TVC', 'name': 'Thiruvananthapuram Division'},
                {'code': 'TPJ', 'name': 'Tiruchchirappalli Division'},
            ],
            'locations': {
                'MAS': [
                    {'code': 'MAS', 'name': 'Chennai Central'},
                    {'code': 'MS', 'name': 'Chennai Egmore'},
                    {'code': 'TBM', 'name': 'Tambaram'},
                ],
                'MDU': [
                    {'code': 'MDU', 'name': 'Madurai Junction'},
                    {'code': 'RMM', 'name': 'Ramanathapuram'},
                    {'code': 'DG', 'name': 'Dindigul Junction'},
                ],
                'PGT': [
                    {'code': 'PGT', 'name': 'Palakkad Junction'},
                    {'code': 'CBE', 'name': 'Coimbatore Junction'},
                    {'code': 'ED', 'name': 'Erode Junction'},
                ],
                'SA': [
                    {'code': 'SA', 'name': 'Salem Junction'},
                    {'code': 'VM', 'name': 'Villupuram Junction'},
                    {'code': 'TPT', 'name': 'Tirupati Main'},
                ],
                'TVC': [
                    {'code': 'TVC', 'name': 'Thiruvananthapuram Central'},
                    {'code': 'QLN', 'name': 'Kollam Junction'},
                    {'code': 'KTYM', 'name': 'Kottayam'},
                ],
                'TPJ': [
                    {'code': 'TPJ', 'name': 'Tiruchchirappalli Junction'},
                    {'code': 'TJ', 'name': 'Thanjavur Junction'},
                    {'code': 'NCJ', 'name': 'Karur Junction'},
                ],
            }
        },
        
        # Western Railway (WR)
        'WR': {
            'divisions': [
                {'code': 'BCT', 'name': 'Mumbai Division'},
                {'code': 'BRC', 'name': 'Vadodara Division'},
                {'code': 'RTM', 'name': 'Ratlam Division'},
                {'code': 'ADI', 'name': 'Ahmedabad Division'},
                {'code': 'RJT', 'name': 'Rajkot Division'},
                {'code': 'BVC', 'name': 'Bhavnagar Division'},
            ],
            'locations': {
                'BCT': [
                    {'code': 'BCT', 'name': 'Mumbai Central'},
                    {'code': 'BDTS', 'name': 'Bandra Terminus'},
                    {'code': 'BVI', 'name': 'Borivali'},
                ],
                'BRC': [
                    {'code': 'BRC', 'name': 'Vadodara Junction'},
                    {'code': 'ST', 'name': 'Surat'},
                    {'code': 'ANND', 'name': 'Anand Junction'},
                ],
                'RTM': [
                    {'code': 'RTM', 'name': 'Ratlam Junction'},
                    {'code': 'INDB', 'name': 'Indore Junction'},
                    {'code': 'UJN', 'name': 'Ujjain Junction'},
                ],
                'ADI': [
                    {'code': 'ADI', 'name': 'Ahmedabad Junction'},
                    {'code': 'MSH', 'name': 'Mahesana Junction'},
                    {'code': 'PNU', 'name': 'Palanpur Junction'},
                ],
                'RJT': [
                    {'code': 'RJT', 'name': 'Rajkot Junction'},
                    {'code': 'JAM', 'name': 'Jamnagar'},
                    {'code': 'HAPA', 'name': 'Hapa'},
                ],
                'BVC': [
                    {'code': 'BVC', 'name': 'Bhavnagar Terminus'},
                    {'code': 'PBR', 'name': 'Porbandar'},
                    {'code': 'OKHA', 'name': 'Okha'},
                ],
            }
        },

        # South Central Railway (SCR)
        'SCR': {
            'divisions': [
                {'code': 'SC', 'name': 'Secunderabad Division'},
                {'code': 'BZA', 'name': 'Vijayawada Division'},
                {'code': 'GTL', 'name': 'Guntakal Division'},
                {'code': 'GNT', 'name': 'Guntur Division'},
                {'code': 'HYB', 'name': 'Hyderabad Division'},
                {'code': 'NED', 'name': 'Nanded Division'},
            ],
            'locations': {
                'SC': [
                    {'code': 'SC', 'name': 'Secunderabad Junction'},
                    {'code': 'KZJ', 'name': 'Kazipet Junction'},
                    {'code': 'WL', 'name': 'Warangal'},
                ],
                'BZA': [
                    {'code': 'BZA', 'name': 'Vijayawada Junction'},
                    {'code': 'RJY', 'name': 'Rajahmundry'},
                    {'code': 'BPP', 'name': 'Bapatla'},
                ],
                'GTL': [
                    {'code': 'GTL', 'name': 'Guntakal Junction'},
                    {'code': 'TPTY', 'name': 'Tirupati'},
                    {'code': 'DMM', 'name': 'Dharmavaram Junction'},
                ],
                'GNT': [
                    {'code': 'GNT', 'name': 'Guntur Junction'},
                    {'code': 'TEL', 'name': 'Tenali Junction'},
                    {'code': 'NLDA', 'name': 'Nellore'},
                ],
                'HYB': [
                    {'code': 'HYB', 'name': 'Hyderabad Deccan Nampally'},
                    {'code': 'KCG', 'name': 'Kacheguda'},
                    {'code': 'MBNR', 'name': 'Mahbubnagar'},
                ],
                'NED': [
                    {'code': 'NED', 'name': 'Nanded'},
                    {'code': 'PAU', 'name': 'Parbhani Junction'},
                    {'code': 'AWB', 'name': 'Aurangabad'},
                ],
            }
        },
        
        # North Central Railway (NCR)
        'NCR': {
            'divisions': [
                {'code': 'PRYJ', 'name': 'Prayagraj Division'},
                {'code': 'AGC', 'name': 'Agra Division'},
                {'code': 'JHS', 'name': 'Jhansi Division'},
            ],
            'locations': {
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
        },
        
        # South Western Railway (SWR)
        'SWR': {
            'divisions': [
                {'code': 'SBC', 'name': 'Bengaluru Division'},
                {'code': 'MYS', 'name': 'Mysuru Division'},
                {'code': 'UBL', 'name': 'Hubballi Division'},
            ],
            'locations': {
                'SBC': [
                    {'code': 'SBC', 'name': 'KSR Bengaluru'},
                    {'code': 'YPR', 'name': 'Yesvantpur Junction'},
                    {'code': 'BNC', 'name': 'Bengaluru Cantt'},
                ],
                'MYS': [
                    {'code': 'MYS', 'name': 'Mysuru Junction'},
                    {'code': 'ASK', 'name': 'Arsikere Junction'},
                    {'code': 'HAS', 'name': 'Hassan'},
                ],
                'UBL': [
                    {'code': 'UBL', 'name': 'Hubballi Junction'},
                    {'code': 'BJP', 'name': 'Vijayapura'},
                    {'code': 'BGM', 'name': 'Belagavi'},
                ],
            }
        },
    }
    
    division_count = 0
    location_count = 0
    
    for zone_code, data in railway_data.items():
        zone = RailwayZone.objects.filter(zone_code=zone_code).first()
        if not zone:
            print(f"Warning: Zone {zone_code} not found, skipping")
            continue
            
        print(f"\nProcessing {zone.name} ({zone_code}):")
        
        # Add divisions
        division_objs = {}
        for div in data['divisions']:
            division, created = RailwayDivision.objects.get_or_create(
                division_code=div['code'],
                defaults={'name': div['name'], 'zone': zone}
            )
            if created:
                division_count += 1
                print(f"  Created division: {division.name} ({division.division_code})")
            else:
                print(f"  Division already exists: {division.name} ({division.division_code})")
                
            division_objs[div['code']] = division
        
        # Add locations for each division
        for div_code, locs in data['locations'].items():
            division = division_objs.get(div_code)
            if not division:
                print(f"  Error: Division {div_code} not found, skipping its locations")
                continue
                
            for loc in locs:
                location, created = RailwayLocation.objects.get_or_create(
                    location_code=loc['code'],
                    defaults={'name': loc['name'], 'division': division}
                )
                if created:
                    location_count += 1
                    print(f"    Created location: {location.name} ({location.location_code})")
                else:
                    print(f"    Location already exists: {location.name} ({location.location_code})")
    
    print(f"\nSummary: Added {division_count} divisions and {location_count} locations across all railway zones")

if __name__ == "__main__":
    add_railway_divisions_and_locations()

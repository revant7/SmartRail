"""
Management command to create initial railway zones and divisions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from railway.models import RailwayZone, RailwayDivision
from notifications.models import NotificationTemplate

User = get_user_model()


class Command(BaseCommand):
    help = 'Create initial railway zones, divisions, and notification templates'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial data...')
        
        # Create Railway Zones
        zones_data = [
            {
                'zone_code': 'SR',
                'name': 'Southern Railway',
                'description': 'Southern Railway Zone covering Tamil Nadu, Kerala, and parts of Karnataka and Andhra Pradesh',
                'headquarters': 'Chennai',
                'jurisdiction': 'Tamil Nadu, Kerala, parts of Karnataka and Andhra Pradesh'
            },
            {
                'zone_code': 'ER',
                'name': 'Eastern Railway',
                'description': 'Eastern Railway Zone covering West Bengal, Bihar, and Jharkhand',
                'headquarters': 'Kolkata',
                'jurisdiction': 'West Bengal, Bihar, Jharkhand'
            },
            {
                'zone_code': 'WR',
                'name': 'Western Railway',
                'description': 'Western Railway Zone covering Maharashtra, Gujarat, and parts of Madhya Pradesh',
                'headquarters': 'Mumbai',
                'jurisdiction': 'Maharashtra, Gujarat, parts of Madhya Pradesh'
            },
            {
                'zone_code': 'NR',
                'name': 'Northern Railway',
                'description': 'Northern Railway Zone covering Delhi, Haryana, Punjab, and parts of Uttar Pradesh',
                'headquarters': 'Delhi',
                'jurisdiction': 'Delhi, Haryana, Punjab, parts of Uttar Pradesh'
            },
            {
                'zone_code': 'CR',
                'name': 'Central Railway',
                'description': 'Central Railway Zone covering Maharashtra and parts of Madhya Pradesh',
                'headquarters': 'Mumbai',
                'jurisdiction': 'Maharashtra, parts of Madhya Pradesh'
            },
            {
                'zone_code': 'NER',
                'name': 'North Eastern Railway',
                'description': 'North Eastern Railway Zone covering Uttar Pradesh and parts of Uttarakhand',
                'headquarters': 'Gorakhpur',
                'jurisdiction': 'Uttar Pradesh, parts of Uttarakhand'
            },
            {
                'zone_code': 'NFR',
                'name': 'Northeast Frontier Railway',
                'description': 'Northeast Frontier Railway Zone covering Assam, Arunachal Pradesh, and other northeastern states',
                'headquarters': 'Guwahati',
                'jurisdiction': 'Assam, Arunachal Pradesh, and other northeastern states'
            },
            {
                'zone_code': 'SECR',
                'name': 'South East Central Railway',
                'description': 'South East Central Railway Zone covering Chhattisgarh and parts of Madhya Pradesh',
                'headquarters': 'Bilaspur',
                'jurisdiction': 'Chhattisgarh, parts of Madhya Pradesh'
            }
        ]
        
        for zone_data in zones_data:
            zone, created = RailwayZone.objects.get_or_create(
                zone_code=zone_data['zone_code'],
                defaults=zone_data
            )
            if created:
                self.stdout.write(f'Created zone: {zone.name}')
            else:
                self.stdout.write(f'Zone already exists: {zone.name}')
        
        # Create Railway Divisions
        divisions_data = [
            # Southern Railway Divisions
            {
                'division_code': 'MAS',
                'name': 'Chennai Division',
                'zone_code': 'SR',
                'headquarters': 'Chennai',
                'jurisdiction': 'Chennai and surrounding areas'
            },
            {
                'division_code': 'SBC',
                'name': 'Bangalore Division',
                'zone_code': 'SR',
                'headquarters': 'Bangalore',
                'jurisdiction': 'Bangalore and surrounding areas'
            },
            {
                'division_code': 'TPTY',
                'name': 'Tirupati Division',
                'zone_code': 'SR',
                'headquarters': 'Tirupati',
                'jurisdiction': 'Tirupati and surrounding areas'
            },
            # Eastern Railway Divisions
            {
                'division_code': 'HWH',
                'name': 'Howrah Division',
                'zone_code': 'ER',
                'headquarters': 'Howrah',
                'jurisdiction': 'Howrah and surrounding areas'
            },
            {
                'division_code': 'ASN',
                'name': 'Asansol Division',
                'zone_code': 'ER',
                'headquarters': 'Asansol',
                'jurisdiction': 'Asansol and surrounding areas'
            },
            # Western Railway Divisions
            {
                'division_code': 'BCT',
                'name': 'Mumbai Central Division',
                'zone_code': 'WR',
                'headquarters': 'Mumbai',
                'jurisdiction': 'Mumbai Central and surrounding areas'
            },
            {
                'division_code': 'ADI',
                'name': 'Ahmedabad Division',
                'zone_code': 'WR',
                'headquarters': 'Ahmedabad',
                'jurisdiction': 'Ahmedabad and surrounding areas'
            },
            # Northern Railway Divisions
            {
                'division_code': 'DLI',
                'name': 'Delhi Division',
                'zone_code': 'NR',
                'headquarters': 'Delhi',
                'jurisdiction': 'Delhi and surrounding areas'
            },
            {
                'division_code': 'LKO',
                'name': 'Lucknow Division',
                'zone_code': 'NR',
                'headquarters': 'Lucknow',
                'jurisdiction': 'Lucknow and surrounding areas'
            }
        ]
        
        for division_data in divisions_data:
            zone = RailwayZone.objects.get(zone_code=division_data['zone_code'])
            division, created = RailwayDivision.objects.get_or_create(
                division_code=division_data['division_code'],
                defaults={
                    'name': division_data['name'],
                    'zone': zone,
                    'headquarters': division_data['headquarters'],
                    'jurisdiction': division_data['jurisdiction']
                }
            )
            if created:
                self.stdout.write(f'Created division: {division.name} ({zone.name})')
            else:
                self.stdout.write(f'Division already exists: {division.name} ({zone.name})')
        
        # Create Notification Templates
        templates_data = [
            {
                'name': 'new_requirement',
                'notification_type': 'NEW_REQUIREMENT',
                'title_template': 'New Requirement: {{ requirement.title }}',
                'message_template': 'A new requirement "{{ requirement.title }}" has been created in {{ zone.name }} - {{ division.name }}. Deadline: {{ requirement.deadline_date|date:"M d, Y" }}.',
                'action_url_template': '/railway/requirements/{{ requirement.id }}/',
                'action_text': 'View Requirement',
                'variables': ['requirement', 'zone', 'division']
            },
            {
                'name': 'requirement_assigned',
                'notification_type': 'STATUS_CHANGE',
                'title_template': 'Requirement Assigned: {{ requirement.title }}',
                'message_template': 'You have been assigned the requirement "{{ requirement.title }}". Please start working on it immediately. Deadline: {{ deadline|date:"M d, Y" }}.',
                'action_url_template': '/railway/requirements/{{ requirement.id }}/',
                'action_text': 'View Requirement',
                'variables': ['requirement', 'deadline']
            },
            {
                'name': 'requirement_assigned_authority',
                'notification_type': 'STATUS_CHANGE',
                'title_template': 'Requirement Assigned: {{ requirement.title }}',
                'message_template': 'The requirement "{{ requirement.title }}" has been assigned to {{ vendor.get_full_name }}.',
                'action_url_template': '/railway/requirements/{{ requirement.id }}/',
                'action_text': 'View Requirement',
                'variables': ['requirement', 'vendor']
            },
            {
                'name': 'deadline_reminder_vendor',
                'notification_type': 'DEADLINE_REMINDER',
                'title_template': 'Deadline Reminder: {{ requirement.title }}',
                'message_template': 'Reminder: The requirement "{{ requirement.title }}" is due in {{ days_remaining }} days. Please ensure timely completion.',
                'action_url_template': '/railway/requirements/{{ requirement.id }}/',
                'action_text': 'View Requirement',
                'variables': ['requirement', 'days_remaining']
            },
            {
                'name': 'deadline_reminder_authority',
                'notification_type': 'DEADLINE_REMINDER',
                'title_template': 'Deadline Reminder: {{ requirement.title }}',
                'message_template': 'Reminder: The requirement "{{ requirement.title }}" is due in {{ days_remaining }} days. Please follow up with the vendor.',
                'action_url_template': '/railway/requirements/{{ requirement.id }}/',
                'action_text': 'View Requirement',
                'variables': ['requirement', 'days_remaining']
            },
            {
                'name': 'status_change_vendor',
                'notification_type': 'STATUS_CHANGE',
                'title_template': 'Status Updated: {{ requirement.title }}',
                'message_template': 'The status of requirement "{{ requirement.title }}" has been changed from {{ old_status }} to {{ new_status }} by {{ changed_by.get_full_name }}.',
                'action_url_template': '/railway/requirements/{{ requirement.id }}/',
                'action_text': 'View Requirement',
                'variables': ['requirement', 'old_status', 'new_status', 'changed_by']
            },
            {
                'name': 'status_change_authority',
                'notification_type': 'STATUS_CHANGE',
                'title_template': 'Status Updated: {{ requirement.title }}',
                'message_template': 'The status of requirement "{{ requirement.title }}" has been changed from {{ old_status }} to {{ new_status }} by {{ changed_by.get_full_name }}.',
                'action_url_template': '/railway/requirements/{{ requirement.id }}/',
                'action_text': 'View Requirement',
                'variables': ['requirement', 'old_status', 'new_status', 'changed_by']
            },
            {
                'name': 'daily_digest',
                'notification_type': 'INFO',
                'title_template': 'Daily Digest - {{ count }} notifications',
                'message_template': 'You have {{ count }} unread notifications from the past 24 hours.',
                'action_url_template': '/notifications/',
                'action_text': 'View All Notifications',
                'variables': ['count']
            },
            {
                'name': 'weekly_digest',
                'notification_type': 'INFO',
                'title_template': 'Weekly Digest - {{ count }} notifications',
                'message_template': 'You have {{ count }} unread notifications from the past week.',
                'action_url_template': '/notifications/',
                'action_text': 'View All Notifications',
                'variables': ['count']
            }
        ]
        
        for template_data in templates_data:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created notification template: {template.name}')
            else:
                self.stdout.write(f'Notification template already exists: {template.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created initial data!')
        )

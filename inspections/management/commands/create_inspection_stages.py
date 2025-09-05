"""
Management command to create default inspection stages.
"""
from django.core.management.base import BaseCommand
from inspections.models import InspectionStage


class Command(BaseCommand):
    help = 'Create default inspection stages for railway manufacturing process'

    def handle(self, *args, **options):
        stages_data = [
            {
                'name': 'Manufacturing Stage',
                'stage_type': 'MANUFACTURING',
                'description': 'Inspection during the manufacturing process of railway equipment',
                'order': 1,
                'requires_vendor': True,
                'requires_railway_auth': True,
            },
            {
                'name': 'Supply Stage',
                'stage_type': 'SUPPLY',
                'description': 'Inspection during the supply chain process before delivery',
                'order': 2,
                'requires_vendor': True,
                'requires_receiver': True,
            },
            {
                'name': 'Receiving Stage',
                'stage_type': 'RECEIVING',
                'description': 'Inspection upon receiving the equipment at railway facility',
                'order': 3,
                'requires_receiver': True,
                'requires_railway_auth': True,
            },
            {
                'name': 'Fitting/Track Installation Stage',
                'stage_type': 'FITTING',
                'description': 'Inspection during fitting and track installation process',
                'order': 4,
                'requires_worker': True,
                'requires_railway_auth': True,
            },
            {
                'name': 'Final Inspection Stage',
                'stage_type': 'FINAL',
                'description': 'Final inspection after complete installation and testing',
                'order': 5,
                'requires_worker': True,
                'requires_railway_auth': True,
            },
        ]

        created_count = 0
        for stage_data in stages_data:
            stage, created = InspectionStage.objects.get_or_create(
                name=stage_data['name'],
                defaults=stage_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created stage: {stage.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Stage already exists: {stage.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} inspection stages')
        )

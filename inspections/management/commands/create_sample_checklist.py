"""
Management command to create sample checklist items for inspection stages.
"""
from django.core.management.base import BaseCommand
from inspections.models import InspectionStage, InspectionChecklist


class Command(BaseCommand):
    help = 'Create sample checklist items for inspection stages'

    def handle(self, *args, **options):
        # Get all stages
        stages = InspectionStage.objects.all()
        
        if not stages.exists():
            self.stdout.write(
                self.style.WARNING('No inspection stages found. Please run create_inspection_stages first.')
            )
            return

        # Sample checklist items for each stage
        checklist_data = {
            'Manufacturing Stage': [
                'Verify material specifications match requirements',
                'Check dimensional accuracy of components',
                'Inspect surface finish quality',
                'Test mechanical properties',
                'Verify welding quality and integrity',
                'Check for surface defects or cracks',
                'Verify component labeling and identification',
                'Test functional performance',
            ],
            'Supply Stage': [
                'Verify packaging integrity',
                'Check shipping documentation',
                'Inspect for damage during transport',
                'Verify quantity matches order',
                'Check temperature and humidity conditions',
                'Verify proper handling procedures',
                'Inspect protective coatings',
                'Check for contamination',
            ],
            'Receiving Stage': [
                'Verify delivery against purchase order',
                'Check for visible damage',
                'Inspect packaging condition',
                'Verify quantity received',
                'Check documentation completeness',
                'Inspect for corrosion or deterioration',
                'Verify storage requirements met',
                'Check for proper labeling',
            ],
            'Fitting/Track Installation Stage': [
                'Verify correct positioning and alignment',
                'Check fastening torque specifications',
                'Inspect joint integrity',
                'Test load bearing capacity',
                'Verify electrical connections (if applicable)',
                'Check for proper clearance',
                'Inspect for stress concentrations',
                'Verify safety requirements met',
            ],
            'Final Inspection Stage': [
                'Perform comprehensive visual inspection',
                'Test all functional requirements',
                'Verify safety compliance',
                'Check performance specifications',
                'Inspect for wear or damage',
                'Verify proper installation',
                'Test under operating conditions',
                'Document final acceptance criteria',
            ],
        }

        created_count = 0
        for stage in stages:
            stage_items = checklist_data.get(stage.name, [])
            
            for i, item_text in enumerate(stage_items, 1):
                item, created = InspectionChecklist.objects.get_or_create(
                    stage=stage,
                    item_text=item_text,
                    defaults={
                        'order': i,
                        'is_required': True,
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created checklist item: {stage.name} - {item_text}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Checklist item already exists: {stage.name} - {item_text}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} checklist items')
        )

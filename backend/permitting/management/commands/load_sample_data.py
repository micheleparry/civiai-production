from django.core.management.base import BaseCommand
from django.db import transaction
from permitting.models import Property, PermitType, PermitApplication, ZoningRule
import uuid


class Command(BaseCommand):
    help = 'Load sample data for Shady Cove CiviAI system'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data for Shady Cove...')
        
        with transaction.atomic():
            # Create sample properties
            self.create_properties()
            
            # Create permit types
            self.create_permit_types()
            
            # Create zoning rules
            self.create_zoning_rules()
            
            # Create sample applications
            self.create_sample_applications()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample data!')
        )

    def create_properties(self):
        """Create sample properties in Shady Cove"""
        properties = [
            {
                'address': '123 Main Street',
                'tax_lot_number': '36-4W-33-1000',
                'latitude': 42.6098,
                'longitude': -122.8120,
                'acres': 0.25,
                'zoning': 'R1',
                'floodplain_overlay': False,
                'riparian_overlay': False,
                'easements': 'Standard utility easements along property lines',
            },
            {
                'address': '456 River Road',
                'tax_lot_number': '36-4W-33-1001',
                'latitude': 42.6089,
                'longitude': -122.8135,
                'acres': 0.50,
                'zoning': 'R1',
                'floodplain_overlay': True,
                'riparian_overlay': True,
                'easements': 'Riparian buffer easement along Rogue River',
                'rights_of_way': 'County road right-of-way 60 feet from centerline',
            },
            {
                'address': '789 Commercial Avenue',
                'tax_lot_number': '36-4W-33-2000',
                'latitude': 42.6105,
                'longitude': -122.8110,
                'acres': 1.0,
                'zoning': 'CG',
                'floodplain_overlay': False,
                'riparian_overlay': False,
                'easements': 'Parking easement for adjacent property',
            },
            {
                'address': '321 Oak Street',
                'tax_lot_number': '36-4W-33-1002',
                'latitude': 42.6092,
                'longitude': -122.8125,
                'acres': 0.18,
                'zoning': 'R2',
                'floodplain_overlay': False,
                'riparian_overlay': False,
            },
            {
                'address': '654 Pine Avenue',
                'tax_lot_number': '36-4W-33-1003',
                'latitude': 42.6101,
                'longitude': -122.8118,
                'acres': 0.33,
                'zoning': 'R1',
                'floodplain_overlay': False,
                'riparian_overlay': False,
            }
        ]
        
        for prop_data in properties:
            property_obj, created = Property.objects.get_or_create(
                tax_lot_number=prop_data['tax_lot_number'],
                defaults=prop_data
            )
            if created:
                self.stdout.write(f'Created property: {property_obj.address}')

    def create_permit_types(self):
        """Create standard permit types for Shady Cove"""
        permit_types = [
            {
                'name': 'Single Family Residence',
                'code': 'SFR',
                'description': 'New single family home construction',
                'base_fee': 500.00,
                'per_square_foot_fee': 0.25,
                'requires_public_notice': True,
                'requires_public_hearing': True,
                'standard_review_days': 30,
                'can_auto_approve': False,
            },
            {
                'name': 'Residential Addition',
                'code': 'ADD',
                'description': 'Addition to existing residential structure',
                'base_fee': 200.00,
                'per_square_foot_fee': 0.15,
                'requires_public_notice': False,
                'requires_public_hearing': False,
                'standard_review_days': 14,
                'can_auto_approve': True,
            },
            {
                'name': 'Deck/Patio',
                'code': 'DECK',
                'description': 'Deck, patio, or similar outdoor structure',
                'base_fee': 75.00,
                'per_square_foot_fee': 0.05,
                'requires_public_notice': False,
                'requires_public_hearing': False,
                'standard_review_days': 7,
                'can_auto_approve': True,
            },
            {
                'name': 'Fence',
                'code': 'FENCE',
                'description': 'Fence installation or replacement',
                'base_fee': 50.00,
                'per_unit_fee': 0.00,
                'requires_public_notice': False,
                'requires_public_hearing': False,
                'standard_review_days': 3,
                'can_auto_approve': True,
            },
            {
                'name': 'Accessory Dwelling Unit',
                'code': 'ADU',
                'description': 'Accessory dwelling unit (ADU) construction',
                'base_fee': 300.00,
                'per_square_foot_fee': 0.20,
                'requires_public_notice': True,
                'requires_public_hearing': False,
                'standard_review_days': 21,
                'can_auto_approve': False,
            },
            {
                'name': 'Commercial Building',
                'code': 'COM',
                'description': 'New commercial building construction',
                'base_fee': 1000.00,
                'per_square_foot_fee': 0.50,
                'requires_public_notice': True,
                'requires_public_hearing': True,
                'standard_review_days': 45,
                'can_auto_approve': False,
            }
        ]
        
        for permit_data in permit_types:
            permit_type, created = PermitType.objects.get_or_create(
                code=permit_data['code'],
                defaults=permit_data
            )
            if created:
                self.stdout.write(f'Created permit type: {permit_type.name}')

    def create_zoning_rules(self):
        """Create zoning rules for Shady Cove"""
        zoning_rules = [
            # R1 - Low Density Residential Rules
            {
                'zoning_district': 'R1',
                'rule_type': 'setback',
                'rule_description': 'Minimum setback requirements for R-1 zone',
                'rule_parameters': {
                    'front': 20,
                    'rear': 10,
                    'side': 5
                }
            },
            {
                'zoning_district': 'R1',
                'rule_type': 'height_limit',
                'rule_description': 'Maximum building height for R-1 zone',
                'rule_parameters': {
                    'max_feet': 35,
                    'max_stories': 2
                }
            },
            {
                'zoning_district': 'R1',
                'rule_type': 'lot_coverage',
                'rule_description': 'Maximum lot coverage for R-1 zone',
                'rule_parameters': {
                    'max_percentage': 40
                }
            },
            
            # R2 - Medium Density Residential Rules
            {
                'zoning_district': 'R2',
                'rule_type': 'setback',
                'rule_description': 'Minimum setback requirements for R-2 zone',
                'rule_parameters': {
                    'front': 15,
                    'rear': 8,
                    'side': 3
                }
            },
            {
                'zoning_district': 'R2',
                'rule_type': 'height_limit',
                'rule_description': 'Maximum building height for R-2 zone',
                'rule_parameters': {
                    'max_feet': 35,
                    'max_stories': 2
                }
            },
            {
                'zoning_district': 'R2',
                'rule_type': 'lot_coverage',
                'rule_description': 'Maximum lot coverage for R-2 zone',
                'rule_parameters': {
                    'max_percentage': 50
                }
            },
            
            # CG - General Commercial Rules
            {
                'zoning_district': 'CG',
                'rule_type': 'setback',
                'rule_description': 'Minimum setback requirements for C-G zone',
                'rule_parameters': {
                    'front': 10,
                    'rear': 5,
                    'side': 0
                }
            },
            {
                'zoning_district': 'CG',
                'rule_type': 'height_limit',
                'rule_description': 'Maximum building height for C-G zone',
                'rule_parameters': {
                    'max_feet': 45,
                    'max_stories': 3
                }
            },
            {
                'zoning_district': 'CG',
                'rule_type': 'lot_coverage',
                'rule_description': 'Maximum lot coverage for C-G zone',
                'rule_parameters': {
                    'max_percentage': 80
                }
            }
        ]
        
        for rule_data in zoning_rules:
            rule, created = ZoningRule.objects.get_or_create(
                zoning_district=rule_data['zoning_district'],
                rule_type=rule_data['rule_type'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f'Created zoning rule: {rule.zoning_district} - {rule.rule_type}')

    def create_sample_applications(self):
        """Create sample permit applications"""
        # Get some properties and permit types
        main_st_property = Property.objects.filter(address__contains='Main Street').first()
        river_rd_property = Property.objects.filter(address__contains='River Road').first()
        
        deck_permit = PermitType.objects.filter(code='DECK').first()
        addition_permit = PermitType.objects.filter(code='ADD').first()
        
        if main_st_property and deck_permit:
            application = PermitApplication.objects.create(
                property=main_st_property,
                permit_type=deck_permit,
                applicant_name='John Smith',
                applicant_email='john.smith@email.com',
                applicant_phone='(541) 555-0123',
                project_description='Building a 12x16 foot deck attached to rear of house',
                project_value=3500.00,
                square_footage=192.00,
                status='SUBMITTED'
            )
            application.calculate_fee()
            application.save()
            self.stdout.write(f'Created sample application: {application.application_id}')
        
        if river_rd_property and addition_permit:
            application = PermitApplication.objects.create(
                property=river_rd_property,
                permit_type=addition_permit,
                applicant_name='Jane Doe',
                applicant_email='jane.doe@email.com',
                applicant_phone='(541) 555-0456',
                project_description='Adding a 200 sq ft bedroom to existing house',
                project_value=25000.00,
                square_footage=200.00,
                status='UNDER_REVIEW'
            )
            application.calculate_fee()
            application.save()
            self.stdout.write(f'Created sample application: {application.application_id}')


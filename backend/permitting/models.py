from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Property(models.Model):
    """
    Represents a property/parcel in Shady Cove
    This is the foundation of the Geo-Spatial Core
    """
    # Unique identifiers
    address = models.CharField(max_length=255, help_text="Street address")
    tax_lot_number = models.CharField(max_length=50, unique=True, help_text="Tax lot number")
    plat_number = models.CharField(max_length=50, blank=True, null=True, help_text="Plat number if applicable")
    
    # Geographic data
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    acres = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    
    # Zoning and overlays
    ZONING_CHOICES = [
        ('R1', 'R-1 Low Density Residential'),
        ('R2', 'R-2 Medium Density Residential'),
        ('R3', 'R-3 High Density Residential'),
        ('CG', 'C-G General Commercial'),
        ('I', 'Industrial'),
        ('A', 'Agriculture'),
        ('PF', 'Public Facilities'),
    ]
    zoning = models.CharField(max_length=10, choices=ZONING_CHOICES, help_text="Current zoning designation")
    
    # Overlay zones (Boolean flags for Shady Cove specific overlays)
    floodplain_overlay = models.BooleanField(default=False, help_text="Property is in FEMA floodplain")
    riparian_overlay = models.BooleanField(default=False, help_text="Property has riparian buffer requirements")
    
    # Constraints
    easements = models.TextField(blank=True, help_text="Description of known easements")
    rights_of_way = models.TextField(blank=True, help_text="Description of rights of way")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['address']
    
    def __str__(self):
        return f"{self.address} (Tax Lot: {self.tax_lot_number})"


class PermitType(models.Model):
    """
    Defines the types of permits available in Shady Cove
    This feeds the "TurboTax-style" guided intake
    """
    name = models.CharField(max_length=100, help_text="Name of permit type")
    code = models.CharField(max_length=20, unique=True, help_text="Short code for permit type")
    description = models.TextField(help_text="Description of when this permit is needed")
    
    # Fee structure
    base_fee = models.DecimalField(max_digits=8, decimal_places=2, help_text="Base application fee")
    per_square_foot_fee = models.DecimalField(max_digits=6, decimal_places=4, default=0, help_text="Additional fee per sq ft")
    per_unit_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Fee per unit (for multi-unit projects)")
    
    # Processing requirements
    requires_public_notice = models.BooleanField(default=False, help_text="Requires public notification")
    requires_public_hearing = models.BooleanField(default=False, help_text="Requires public hearing")
    standard_review_days = models.IntegerField(default=14, help_text="Standard review time in business days")
    
    # Auto-approval settings (for simple permits)
    can_auto_approve = models.BooleanField(default=False, help_text="Can be automatically approved if compliant")
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class PermitApplication(models.Model):
    """
    Represents a permit application submitted through CiviAI
    This is the core of the application tracking system
    """
    # Unique identifier
    application_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Basic information
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='applications')
    permit_type = models.ForeignKey(PermitType, on_delete=models.CASCADE)
    
    # Applicant information
    applicant_name = models.CharField(max_length=200)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=20)
    
    # Project details
    project_description = models.TextField(help_text="Description of proposed work")
    project_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Estimated project value")
    square_footage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Square footage of project")
    
    # Status tracking
    STATUS_CHOICES = [
        ('DRAFT', 'Draft - In Progress'),
        ('SUBMITTED', 'Submitted - Under Review'),
        ('INCOMPLETE', 'Incomplete - Additional Information Required'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('APPROVED_WITH_CONDITIONS', 'Approved with Conditions'),
        ('DENIED', 'Denied'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='DRAFT')
    
    # Fees
    calculated_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fee_paid = models.BooleanField(default=False)
    
    # AI compliance checking results
    compliance_check_passed = models.BooleanField(default=False)
    compliance_issues = models.JSONField(default=list, blank=True, help_text="List of compliance issues found by AI")
    
    # Review tracking
    submitted_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_applications')
    review_completed_at = models.DateTimeField(blank=True, null=True)
    review_notes = models.TextField(blank=True, help_text="Staff review notes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.permit_type.name} - {self.property.address} ({self.get_status_display()})"
    
    def calculate_fee(self):
        """Calculate the total fee for this application"""
        base_fee = self.permit_type.base_fee
        
        additional_fees = 0
        if self.square_footage and self.permit_type.per_square_foot_fee:
            additional_fees += float(self.square_footage) * float(self.permit_type.per_square_foot_fee)
        
        if self.project_value and self.permit_type.per_unit_fee:
            additional_fees += float(self.permit_type.per_unit_fee)
        
        total_fee = float(base_fee) + additional_fees
        self.calculated_fee = total_fee
        return total_fee


class ApplicationDocument(models.Model):
    """
    Stores documents uploaded with permit applications
    """
    application = models.ForeignKey(PermitApplication, on_delete=models.CASCADE, related_name='documents')
    
    DOCUMENT_TYPES = [
        ('SITE_PLAN', 'Site Plan'),
        ('FLOOR_PLAN', 'Floor Plan'),
        ('ELEVATION', 'Elevation Drawing'),
        ('SURVEY', 'Property Survey'),
        ('PHOTOS', 'Site Photos'),
        ('OTHER', 'Other'),
    ]
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    
    file = models.FileField(upload_to='application_documents/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    
    # AI processing results
    ai_processed = models.BooleanField(default=False)
    ai_extracted_data = models.JSONField(default=dict, blank=True, help_text="Data extracted by AI from document")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.application}"


class ZoningRule(models.Model):
    """
    Stores the zoning rules that feed the AI compliance engine
    This is part of the "Permit Configurator" backend
    """
    zoning_district = models.CharField(max_length=10, choices=Property.ZONING_CHOICES)
    rule_type = models.CharField(max_length=50, help_text="Type of rule (e.g., 'setback', 'height_limit', 'lot_coverage')")
    rule_description = models.CharField(max_length=200, help_text="Human-readable description")
    
    # Rule parameters (stored as JSON for flexibility)
    rule_parameters = models.JSONField(help_text="Rule parameters in JSON format")
    
    # Examples:
    # For setbacks: {"front": 20, "rear": 10, "side": 5}
    # For height: {"max_feet": 35, "max_stories": 2}
    # For lot coverage: {"max_percentage": 40}
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['zoning_district', 'rule_type']
    
    def __str__(self):
        return f"{self.zoning_district} - {self.rule_type}"


class ComplianceCheck(models.Model):
    """
    Stores the results of AI compliance checks
    """
    application = models.ForeignKey(PermitApplication, on_delete=models.CASCADE, related_name='compliance_checks')
    
    rule_checked = models.ForeignKey(ZoningRule, on_delete=models.CASCADE)
    
    CHECK_RESULTS = [
        ('PASS', 'Compliant'),
        ('FAIL', 'Non-Compliant'),
        ('WARNING', 'Warning - Needs Review'),
        ('NOT_APPLICABLE', 'Not Applicable'),
    ]
    result = models.CharField(max_length=15, choices=CHECK_RESULTS)
    
    details = models.TextField(help_text="Detailed explanation of the check result")
    suggested_action = models.TextField(blank=True, help_text="Suggested action to resolve issues")
    
    checked_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.application} - {self.rule_checked.rule_type}: {self.get_result_display()}"


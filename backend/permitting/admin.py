from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Property, PermitType, PermitApplication, 
    ApplicationDocument, ZoningRule, ComplianceCheck
)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['address', 'tax_lot_number', 'zoning', 'floodplain_overlay', 'riparian_overlay', 'created_at']
    list_filter = ['zoning', 'floodplain_overlay', 'riparian_overlay']
    search_fields = ['address', 'tax_lot_number', 'plat_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('address', 'tax_lot_number', 'plat_number')
        }),
        ('Geographic Data', {
            'fields': ('latitude', 'longitude', 'acres')
        }),
        ('Zoning & Overlays', {
            'fields': ('zoning', 'floodplain_overlay', 'riparian_overlay')
        }),
        ('Constraints', {
            'fields': ('easements', 'rights_of_way'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PermitType)
class PermitTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'base_fee', 'requires_public_notice', 'can_auto_approve', 'is_active']
    list_filter = ['requires_public_notice', 'requires_public_hearing', 'can_auto_approve', 'is_active']
    search_fields = ['name', 'code', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Fee Structure', {
            'fields': ('base_fee', 'per_square_foot_fee', 'per_unit_fee')
        }),
        ('Processing Requirements', {
            'fields': ('requires_public_notice', 'requires_public_hearing', 'standard_review_days', 'can_auto_approve')
        })
    )


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    readonly_fields = ['file_size', 'uploaded_at', 'ai_processed']


class ComplianceCheckInline(admin.TabularInline):
    model = ComplianceCheck
    extra = 0
    readonly_fields = ['checked_at']


@admin.register(PermitApplication)
class PermitApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_id_short', 'property_address', 'permit_type', 'applicant_name', 'status', 'compliance_status', 'submitted_at']
    list_filter = ['status', 'permit_type', 'compliance_check_passed', 'fee_paid']
    search_fields = ['applicant_name', 'applicant_email', 'property__address', 'project_description']
    readonly_fields = ['application_id', 'calculated_fee', 'created_at', 'updated_at']
    
    inlines = [ApplicationDocumentInline, ComplianceCheckInline]
    
    fieldsets = (
        ('Application Details', {
            'fields': ('application_id', 'property', 'permit_type', 'status')
        }),
        ('Applicant Information', {
            'fields': ('applicant_name', 'applicant_email', 'applicant_phone')
        }),
        ('Project Details', {
            'fields': ('project_description', 'project_value', 'square_footage')
        }),
        ('Fees & Payment', {
            'fields': ('calculated_fee', 'fee_paid')
        }),
        ('AI Compliance', {
            'fields': ('compliance_check_passed', 'compliance_issues'),
            'classes': ('collapse',)
        }),
        ('Review Information', {
            'fields': ('submitted_at', 'reviewed_by', 'review_completed_at', 'review_notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def application_id_short(self, obj):
        return str(obj.application_id)[:8] + "..."
    application_id_short.short_description = "Application ID"
    
    def property_address(self, obj):
        return obj.property.address
    property_address.short_description = "Property Address"
    
    def compliance_status(self, obj):
        if obj.compliance_check_passed:
            return format_html('<span style="color: green;">✓ Compliant</span>')
        else:
            return format_html('<span style="color: red;">✗ Issues Found</span>')
    compliance_status.short_description = "Compliance"
    
    actions = ['calculate_fees', 'run_compliance_check']
    
    def calculate_fees(self, request, queryset):
        for application in queryset:
            application.calculate_fee()
            application.save()
        self.message_user(request, f"Fees calculated for {queryset.count()} applications.")
    calculate_fees.short_description = "Recalculate fees for selected applications"
    
    def run_compliance_check(self, request, queryset):
        # This would trigger the AI compliance check
        # For now, it's a placeholder
        self.message_user(request, f"Compliance check queued for {queryset.count()} applications.")
    run_compliance_check.short_description = "Run AI compliance check"


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'application', 'document_type', 'file_size_mb', 'ai_processed', 'uploaded_at']
    list_filter = ['document_type', 'ai_processed']
    search_fields = ['filename', 'application__applicant_name']
    readonly_fields = ['file_size', 'uploaded_at']
    
    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024*1024):.2f} MB"
    file_size_mb.short_description = "File Size"


@admin.register(ZoningRule)
class ZoningRuleAdmin(admin.ModelAdmin):
    list_display = ['zoning_district', 'rule_type', 'rule_description', 'is_active', 'created_at']
    list_filter = ['zoning_district', 'rule_type', 'is_active']
    search_fields = ['rule_type', 'rule_description']
    
    fieldsets = (
        ('Rule Definition', {
            'fields': ('zoning_district', 'rule_type', 'rule_description', 'is_active')
        }),
        ('Rule Parameters', {
            'fields': ('rule_parameters',),
            'description': 'Enter rule parameters in JSON format. Examples:<br>'
                         'Setbacks: {"front": 20, "rear": 10, "side": 5}<br>'
                         'Height: {"max_feet": 35, "max_stories": 2}<br>'
                         'Lot Coverage: {"max_percentage": 40}'
        })
    )


@admin.register(ComplianceCheck)
class ComplianceCheckAdmin(admin.ModelAdmin):
    list_display = ['application', 'rule_type', 'result', 'checked_at']
    list_filter = ['result', 'rule_checked__rule_type', 'rule_checked__zoning_district']
    search_fields = ['application__applicant_name', 'rule_checked__rule_type']
    readonly_fields = ['checked_at']
    
    def rule_type(self, obj):
        return obj.rule_checked.rule_type
    rule_type.short_description = "Rule Type"


# Customize the admin site header and title
admin.site.site_header = "CiviAI Administration"
admin.site.site_title = "CiviAI Admin"
admin.site.index_title = "Welcome to CiviAI Administration"


from rest_framework import serializers
from .models import Property, PermitType, PermitApplication, ApplicationDocument, ZoningRule, ComplianceCheck


class PropertySerializer(serializers.ModelSerializer):
    zoning_display = serializers.CharField(source='get_zoning_display', read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'address', 'tax_lot_number', 'plat_number',
            'latitude', 'longitude', 'acres',
            'zoning', 'zoning_display',
            'floodplain_overlay', 'riparian_overlay',
            'easements', 'rights_of_way'
        ]


class PermitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermitType
        fields = [
            'id', 'name', 'code', 'description',
            'base_fee', 'per_square_foot_fee', 'per_unit_fee',
            'requires_public_notice', 'requires_public_hearing',
            'standard_review_days', 'can_auto_approve'
        ]


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationDocument
        fields = [
            'id', 'document_type', 'document_type_display',
            'filename', 'file_size', 'file_size_mb',
            'ai_processed', 'uploaded_at'
        ]
    
    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2)


class ZoningRuleSerializer(serializers.ModelSerializer):
    zoning_display = serializers.CharField(source='get_zoning_district_display', read_only=True)
    
    class Meta:
        model = ZoningRule
        fields = [
            'id', 'zoning_district', 'zoning_display',
            'rule_type', 'rule_description', 'rule_parameters'
        ]


class ComplianceCheckSerializer(serializers.ModelSerializer):
    rule_type = serializers.CharField(source='rule_checked.rule_type', read_only=True)
    rule_description = serializers.CharField(source='rule_checked.rule_description', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    
    class Meta:
        model = ComplianceCheck
        fields = [
            'id', 'rule_type', 'rule_description',
            'result', 'result_display', 'details', 'suggested_action',
            'checked_at'
        ]


class PermitApplicationSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    permit_type = PermitTypeSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    documents = ApplicationDocumentSerializer(many=True, read_only=True)
    compliance_checks = ComplianceCheckSerializer(many=True, read_only=True)
    application_id_short = serializers.SerializerMethodField()
    
    class Meta:
        model = PermitApplication
        fields = [
            'application_id', 'application_id_short',
            'property', 'permit_type',
            'applicant_name', 'applicant_email', 'applicant_phone',
            'project_description', 'project_value', 'square_footage',
            'status', 'status_display',
            'calculated_fee', 'fee_paid',
            'compliance_check_passed', 'compliance_issues',
            'submitted_at', 'review_completed_at', 'review_notes',
            'documents', 'compliance_checks',
            'created_at', 'updated_at'
        ]
    
    def get_application_id_short(self, obj):
        return str(obj.application_id)[:8]


class PermitApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new permit applications
    """
    class Meta:
        model = PermitApplication
        fields = [
            'property', 'permit_type',
            'applicant_name', 'applicant_email', 'applicant_phone',
            'project_description', 'project_value', 'square_footage'
        ]
    
    def create(self, validated_data):
        application = PermitApplication.objects.create(**validated_data)
        application.calculate_fee()
        application.save()
        return application


class PropertyLookupSerializer(serializers.Serializer):
    """
    Serializer for property lookup requests
    """
    address = serializers.CharField(required=False, allow_blank=True)
    tax_lot_number = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if not data.get('address') and not data.get('tax_lot_number'):
            raise serializers.ValidationError("Either address or tax_lot_number must be provided")
        return data


class FeeCalculationSerializer(serializers.Serializer):
    """
    Serializer for fee calculation requests
    """
    permit_type_id = serializers.IntegerField()
    project_value = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    square_footage = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)


class ComplianceCheckRequestSerializer(serializers.Serializer):
    """
    Serializer for compliance check requests
    """
    property_id = serializers.IntegerField()
    permit_type_id = serializers.IntegerField()
    project_data = serializers.JSONField(required=False, default=dict)
    
    # Example project_data structure:
    # {
    #     "setbacks": {
    #         "front": 15,
    #         "rear": 8,
    #         "side": 5
    #     },
    #     "height": 25,
    #     "lot_coverage": 35
    # }


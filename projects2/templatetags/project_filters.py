from django import template

register = template.Library()


@register.filter
def in_field_group(value, arg):
    if arg == "specialized_equipment":
        if value in [
            "technical_service_needs",
            "mobilization_needs"
        ]:
            return True
    elif arg == "field":
        if value in [
            "vehicle_needs",
            "ship_needs",
            "coip_reference_id",
            "instrumentation",
            "owner_of_instrumentation",
            "requires_field_staff",
            "field_staff_needs",
        ]:
            return True
    elif arg == "data":
        if value in [
            "data_collected",
            "data_products",
            "open_data_eligible",
            "data_storage_plan",
            "data_management_needs",
        ]:
            return True
    elif arg == "lab":
        if value in [
            "requires_abl_services",
            "requires_lab_space",
            "requires_other_lab_support",
            "other_lab_support_needs",
        ]:
            return True

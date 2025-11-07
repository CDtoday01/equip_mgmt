from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SystemSetting

@api_view(["GET"])
def get_product_check_setting(request):
    enabled = SystemSetting.get_value("ENABLE_PRODUCT_DUPLICATE_CHECK", False)
    return Response({"enabled": enabled})

@api_view(["POST"])
def toggle_product_check_setting(request):
    enabled = bool(request.data.get("enabled", False))
    SystemSetting.set_value("ENABLE_PRODUCT_DUPLICATE_CHECK", enabled)
    return Response({"enabled": enabled})

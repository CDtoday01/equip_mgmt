from rest_framework.response import Response
from rest_framework import status
from .models import Asset, Product, StockTransaction
from people.models import People
from system.models import SystemSetting
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import AssetSerializer
import io, csv

# ================================================================
# 資產列表（GET/POST）
# ================================================================
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assets_list(request):
    if request.method == 'GET':
        assets = Asset.objects.select_related('product', 'owner_user').all()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        created = []
        asset_entries = []

        # -----------------------
        # 判斷是否為 CSV 匯入
        # -----------------------
        is_csv_import = 'file' in request.FILES

        # -----------------------
        # 讀取系統設定：是否啟用產品重複檢查
        # -----------------------
        try:
            check_duplicates = SystemSetting.get_value("ENABLE_PRODUCT_DUPLICATE_CHECK", False)
        except Exception as e:
            print(f"[Warning] 無法讀取系統設定：{e}")
            check_duplicates = False

        # -----------------------
        # 統一處理 CSV 或單筆新增
        # -----------------------
        if is_csv_import:
            file = request.FILES['file']
            decoded_file = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
            for row in reader:
                asset_entries.append({
                    "product_code": row.get('產品代碼'),
                    "name": row.get('名稱'),
                    "type": row.get('種類', ''),
                    "price": float(row.get('價格', 0) or 0),
                    "owner_name": row.get('持有人', None)
                })
        else:
            data = request.data
            asset_entries.append({
                "product_code": data.get('product_code'),
                "name": data.get('name'),
                "type": data.get('type', ''),
                "price": float(data.get('price', 0) or 0),
                "owner_name": data.get('owner_user', None)
            })

        # ============================================================
        # 資產建立處理
        # ============================================================
        for entry in asset_entries:
            product_code = entry.get('product_code')
            name = entry.get('name')
            type_ = entry.get('type')
            price = entry.get('price')
            owner_name = entry.get('owner_name')

            if not product_code:
                return Response({"detail": "產品代碼為必填欄位"}, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------
            # 產品處理邏輯
            # -----------------------
            product = None

            if is_csv_import:
                # 匯入時：不檢查重複，直接建立或取得
                product, _ = Product.objects.get_or_create(
                    code=product_code,
                    defaults={'name': name, 'type': type_, 'price': price}
                )
            else:
                if check_duplicates:
                    # ✅ 系統設定開啟：允許重複 → 若存在直接取用
                    product = Product.objects.filter(code=product_code).first()
                    if not product:
                        product = Product.objects.create(
                            code=product_code,
                            name=name,
                            type=type_,
                            price=price
                        )
                else:
                    # 🚫 關閉檢查：每筆都視為新產品
                    # 若 code 唯一會報錯，交由 unique constraint 處理
                    product, _ = Product.objects.get_or_create(
                        code=product_code,
                        defaults={'name': name, 'type': type_, 'price': price}
                    )

            # -----------------------
            # 找持有人（可模糊比對）
            # -----------------------
            owner_user = None
            if owner_name:
                qs = People.objects.filter(name__icontains=owner_name)
                if qs.count() == 1:
                    owner_user = qs.first()
                elif qs.count() > 1:
                    candidates = [
                        {
                            "id_number": p.id_number,
                            "name": p.name,
                            "department": p.department.name if p.department else None,
                            "email": p.email,
                            "phone": p.phone
                        } for p in qs
                    ]
                    return Response({
                        "detail": f"持有人名稱 {owner_name} 有多個匹配",
                        "candidates": candidates,
                        "asset_data": {
                            "product_code": product_code,
                            "name": name,
                            "type": type_,
                            "price": price
                        }
                    }, status=status.HTTP_409_CONFLICT)

            # -----------------------
            # 建立資產（asset_tag 自動生成）
            # -----------------------
            asset = Asset.objects.create(
                product=product,
                owner_user=owner_user
            )
            created.append(AssetSerializer(asset).data)

        return Response(
            created if len(created) > 1 else created[0],
            status=status.HTTP_201_CREATED
        )


# ================================================================
# 單一資產 CRUD（GET / PUT / DELETE）
# ================================================================
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def asset_detail(request, pk):
    try:
        asset = Asset.objects.get(pk=pk)
    except Asset.DoesNotExist:
        return Response({"error": "Asset not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AssetSerializer(asset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = AssetSerializer(asset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        asset.delete()
        return Response({"message": "Asset deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ================================================================
# 出入庫操作
# ================================================================
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def stock_transaction(request):
    data = request.data
    asset_tag = data.get("asset_tag")
    transaction_type = data.get("transaction_type")
    person_id_number = data.get("person_id")  # 前端選單用 id_number
    remark = data.get("remark", "")

    # 確認資產存在
    try:
        asset = Asset.objects.get(asset_tag=asset_tag)
    except Asset.DoesNotExist:
        return Response({"error": "資產不存在"}, status=status.HTTP_404_NOT_FOUND)

    if transaction_type == "OUT":
        # 已在員工手上
        if asset.owner_user is not None:
            return Response({"error": "該資產已在員工手上"}, status=status.HTTP_400_BAD_REQUEST)

        if not person_id_number:
            return Response({"error": "缺少員工 ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 用 id_number 查找員工
        try:
            person = People.objects.get(id_number=person_id_number)
        except People.DoesNotExist:
            return Response({"error": "員工不存在"}, status=status.HTTP_404_NOT_FOUND)

        asset.owner_user = person
        asset.save()

    elif transaction_type == "IN":
        # 已在倉庫中
        if asset.owner_user is None:
            return Response({"error": "該資產已在倉庫中"}, status=status.HTTP_400_BAD_REQUEST)
        asset.owner_user = None
        asset.save()
    else:
        return Response({"error": "無效交易類型"}, status=status.HTTP_400_BAD_REQUEST)

    # 記錄交易
    StockTransaction.objects.create(
        asset=asset,
        transaction_type=transaction_type,
        remark=remark
    )

    return Response(
        {"success": True, "asset": AssetSerializer(asset).data},
        status=status.HTTP_200_OK
    )


# ================================================================
# 某資產歷史
# ================================================================
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def stock_history(request, asset_tag):
    try:
        asset = Asset.objects.get(asset_tag=asset_tag)
    except Asset.DoesNotExist:
        return Response({"error": "資產不存在"}, status=status.HTTP_404_NOT_FOUND)

    transactions = StockTransaction.objects.filter(asset=asset).order_by("-date")
    data = [{
        "id": t.id,
        "transaction_type": t.transaction_type,
        "date": t.date,
        "remark": t.remark
    } for t in transactions]

    return Response(data, status=status.HTTP_200_OK)

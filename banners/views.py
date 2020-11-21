from rest_framework.decorators import api_view
from rest_framework.response import Response

from banners.models import Banner
from banners.serializers import BannerSerializer


@api_view(['GET'])
def banners_list_api(request):
    banners = Banner.objects.filter(status='show')
    serializer_banners = BannerSerializer(banners, many=True)
    return Response(serializer_banners.data)

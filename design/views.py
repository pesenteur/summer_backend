import re

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from permissions import *
from .serializers import *
from .models import *
import os

class DesignListCreateView(generics.ListCreateAPIView):
    serializer_class = DesignSerializer
    permission_classes = [IsMemberForDesign]

    def get_queryset(self):
        project = self.request.data.get('project') or self.request.query_params.get('project')
        return Design.objects.filter(project=project)

    def perform_create(self, serializer):
        design = serializer.save()
        DesignHistory.objects.create(design=design)

class DesignRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Design.objects.all()
    serializer_class = DesignWithDataSerializer
    permission_classes = [IsMemberForDesign]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class DesignHistoryListCreateView(generics.ListCreateAPIView):
    serializer_class = DesignHistorySerializer
    permission_classes = [IsMemberForDesign]

    def get_queryset(self):
        design = self.request.query_params.get('design')
        return DesignHistory.objects.filter(design=design)

@api_view(['POST'])
@permission_classes([IsMemberForDesign])
def generate_preview_view(request, pk):
    """
    生成原型设计预览
    :param request: 请求
    :param pk: design的id
    :return:
    """
    try:
        design = Design.objects.get(pk=pk)
    except Design.DoesNotExist:
        return Response({'detail': '不存在的原型设计'}, status=status.HTTP_404_NOT_FOUND)

    image_file = request.FILES.get('image')
    if not image_file:
        return Response({'detail': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
    image_file = image_file.open('r')

    os.makedirs('./media/images/design', exist_ok=True)
    with open(f'./media/images/design/{design.id}.png', 'wb') as f:
        f.write(image_file.read())
    design_preview,_ = DesignPreview.objects.update_or_create(
        image=f'media/images/design/{design.id}.png',
        design=design
    )

    return Response(DesignPreviewSerializer(instance=design_preview).data,
                    status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsMemberForDesign])
def cancel_preview_view(request):
    """
    取消原型设计预览
    :param request:
    :return:
    """
    project = request.query_params.get('project')
    design_previews = DesignPreview.objects.filter(design__project=project)
    for design_preview in design_previews:
        if os.path.exists(design_preview.image):
            os.remove(design_preview.image)
        design_preview.delete()

    return Response(None, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([])
def get_preview_view(request):
    """
    获取原型设计预览
    :param request:
    :return:
    """
    project = request.query_params.get('project')
    design_previews = DesignPreview.objects.filter(design__project=project)
    data = DesignPreviewSerializer(instance=design_previews, many=True).data
    path = request.path
    path = re.sub(r'/api/v\d+.*', '/', path)
    print(path)
    for item in data:
        item['image'] = request.build_absolute_uri(path+item['image'])
    return Response(data, status=status.HTTP_200_OK)
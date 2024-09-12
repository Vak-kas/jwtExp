from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class WelcomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 요청한 유저의 이름을 반환
        user = request.user
        return Response({"message": f"{user.name}님, 반갑습니다!"})

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from chats.serializers import ChatSerializer, ChatPreviewSerializer, MessageSerializer, MessagePreviewSerializer
from chats.models import Chat


class ChatCreateAPI(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ChatSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        invited = request.data.get('invited', [])
        chat = serializer.save(creator=request.user, invited=invited)
        return Response({
            'chat': ChatSerializer(chat, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)


class MessageCreateAPI(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = MessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        message = serializer.save(author=request.user, chat_id=kwargs.get('pk'))
        return Response({
            'message': MessageSerializer(message, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)


class ChatHistoryAPI(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = MessagePreviewSerializer

    def list(self, request, *args, **kwargs):
        chat_id = kwargs.get('pk')

        try:
            chat = Chat.objects.get(pk=chat_id)
        except ObjectDoesNotExist:
            return Response('Chat does not exist', status=status.HTTP_404_NOT_FOUND)

        if request.user not in chat.participants.all():
            return Response('Chat does not exist', status=status.HTTP_404_NOT_FOUND)

        serializer = MessagePreviewSerializer(chat.messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatUserAPI(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ChatPreviewSerializer

    def get_queryset(self):
        return self.request.user.chats

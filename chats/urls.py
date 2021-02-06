from django.urls import path

from chats.api import ChatCreateAPI, ChatHistoryAPI, ChatUserAPI, MessageCreateAPI


urlpatterns = [
    path('api/chats/create', ChatCreateAPI.as_view(), name='create-chat'),
    path('api/chats/send_message', MessageCreateAPI.as_view(), name='send-message'),
    path('api/chats/<pk>/history', ChatHistoryAPI.as_view(), name='chat-history'),
    path('api/chats/user', ChatUserAPI.as_view(), name='chat-user')
]
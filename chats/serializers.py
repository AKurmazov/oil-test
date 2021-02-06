import json

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from accounts.serializers import UserSerializer

from chats.models import Chat, Message


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(read_only=True, many=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = '__all__'

    def create(self, validated_data):
        creator = validated_data.get('creator')

        try:
            invited_pks = json.loads(validated_data.get('invited'))
        except json.JSONDecodeError:
            raise serializers.ValidationError('`invited` parameter is a json-like list of integers')
        except TypeError:
            raise serializers.ValidationError('`invited` parameter should not be missing')

        if not isinstance(invited_pks, list):
            raise serializers.ValidationError('`invited` parameter is a list of integers')

        invited_users = [creator, ]
        try:
            for pk in invited_pks:
                if not isinstance(pk, int):
                    raise serializers.ValidationError('An entry of the invited list should be an integer')
                if pk == creator.pk:
                    raise serializers.ValidationError('You cannot invite yourself to a chat')
                invited_users.append(get_user_model().objects.get(pk=pk))
        except ObjectDoesNotExist:
            raise serializers.ValidationError('One or more invited users are not registered yet')

        chat = Chat.objects.create(creator=creator)
        chat.participants.set(invited_users)
        chat.save()

        return chat


class ChatPreviewSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'creator', 'created_at')


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'author', 'text', 'created_at')

    def create(self, validated_data):
        chat_id = validated_data.get('chat_id')
        author = validated_data.get('author')
        text = validated_data.get('text')

        try:
            chat = Chat.objects.get(pk=chat_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Chat does not exist')

        if author not in chat.participants.all():
            raise serializers.ValidationError('Chat does not exist')

        message = Message.objects.create(chat=chat, author=author, text=text)

        return message


class MessagePreviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'author', 'text', 'created_at')

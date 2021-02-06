from django.contrib.auth import get_user_model
from django.db import models


class Chat(models.Model):
    participants = models.ManyToManyField(get_user_model(), related_name='chats')
    creator = models.ForeignKey(get_user_model(), related_name='created_chats', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat: #{self.pk} created by {self.creator}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(get_user_model(), related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message: #{self.pk} | Author: {self.author} | Chat: {self.chat}'
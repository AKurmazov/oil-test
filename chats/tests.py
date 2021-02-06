from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from knox.models import AuthToken


class CreateChatTestCase(APITestCase):

    create_chat_url = reverse('create-chat')

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.token = AuthToken.objects.create(user=self.user)[1]
        self.api_authentication()
        self.mock_user = User.objects.create_user(username='mock', password='mock')

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_create_task_success(self):
        data = {
            'invited': f'[{self.mock_user.pk}]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        chat = response.data['chat']
        self.assertEqual(len(chat['participants']), 2)
        self.assertEqual(chat['participants'][0]['id'], self.user.pk)
        self.assertEqual(chat['participants'][1]['id'], self.mock_user.pk)
        self.assertEqual(chat['creator']['id'], self.user.pk)

    def test_create_task_success_no_invited(self):
        data = {
            'invited': '[]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        chat = response.data['chat']
        self.assertEqual(len(chat['participants']), 1)
        self.assertEqual(chat['participants'][0]['id'], self.user.pk)
        self.assertEqual(chat['creator']['id'], self.user.pk)

    def test_create_task_fail_invalid_json(self):
        data = {
            'invited': '[1,3['
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], '`invited` parameter is a json-like list of integers')

    def test_create_task_fail_not_list(self):
        data = {
            'invited': '{"data": [1, 2]}'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], '`invited` parameter is a list of integers')

    def test_create_task_fail_missing_invited(self):
        data = {}
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], '`invited` parameter should not be missing')

    def test_create_task_fail_invalid_entry(self):
        data = {
            'invited': f'[{self.mock_user.pk}, "a"]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'An entry of the invited list should be an integer')

    def test_create_task_fail_invited_myself(self):
        data = {
            'invited': f'[{self.mock_user.pk}, {self.user.pk}]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'You cannot invite yourself to a chat')

    def test_create_task_fail_not_existing_participant(self):
        data = {
            'invited': f'[0, {self.mock_user.pk}]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'One or more invited users are not registered yet')

    def test_not_authenticated_user_fail(self):
        self.client.credentials(HTTP_AUTHORIZATION='')

        response = self.client.get(self.create_chat_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SendMessageTestCase(APITestCase):

    create_chat_url = reverse('create-chat')

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.token = AuthToken.objects.create(user=self.user)[1]
        self.api_authentication()
        self.mock_user = User.objects.create_user(username='mock', password='mock')
        self.chat = self.test_create_chat()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_create_chat(self):
        data = {
            'invited': f'[{self.mock_user.pk}]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['chat']

    def test_send_message_user_success(self):
        data = {
            'text': 'Hello!'
        }
        response = self.client.post(reverse('send-message', kwargs={'pk': self.chat['id']}), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        message = response.data['message']
        self.assertEqual(message['author']['id'], self.user.pk)
        self.assertEqual(message['text'], data['text'])

    def test_send_message_mock_user_success(self):
        token = AuthToken.objects.create(user=self.mock_user)[1]

        # Change authenticated user to the mock one
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        data = {
            'text': 'Hello!'
        }
        response = self.client.post(reverse('send-message', kwargs={'pk': self.chat['id']}), data=data)
        self.assertEqual(response.status_code, 201)

        message = response.data['message']
        self.assertEqual(message['author']['id'], self.mock_user.pk)
        self.assertEqual(message['text'], data['text'])

        # Go back to the original user
        self.api_authentication()

    def test_send_message_fail_missing_text(self):
        data = {}
        response = self.client.post(reverse('send-message', kwargs={'pk': self.chat['id']}), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_message_fail_not_participant(self):
        fail_user = User.objects.create_user(username='fail_user', password='test')
        token = AuthToken.objects.create(user=fail_user)[1]

        # Change authenticated user to the fail one
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        data = {
            'text': 'Hello!'
        }
        response = self.client.post(reverse('send-message', kwargs={'pk': self.chat['id']}), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'Chat does not exist')

        # Go back to the original user
        self.api_authentication()

    def test_send_message_fail_invalid_chat_id(self):
        data = {
            'text': 'Hello!'
        }
        response = self.client.post(reverse('send-message', kwargs={'pk': 0}), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'Chat does not exist')

    def test_not_authenticated_user_fail(self):
        self.client.credentials(HTTP_AUTHORIZATION='')

        response = self.client.get(reverse('send-message', kwargs={'pk': 0}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChatHistoryTestCase(APITestCase):

    create_chat_url = reverse('create-chat')

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.token = AuthToken.objects.create(user=self.user)[1]
        self.api_authentication()
        self.mock_user = User.objects.create_user(username='mock', password='mock')
        self.chat = self.test_create_chat()
        self.test_create_messages()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_create_chat(self):
        data = {
            'invited': f'[{self.mock_user.pk}]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['chat']

    def test_create_messages(self):
        response = self.client.post(reverse('send-message', kwargs={'pk': self.chat['id']}), data={'text': 'Hey!'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('send-message', kwargs={'pk': self.chat['id']}), data={'text': 'Whats up?'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Change authenticated user to the mock one
        token = AuthToken.objects.create(user=self.mock_user)[1]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.post(reverse('send-message', kwargs={'pk': self.chat['id']}), data={'text': 'Nothing'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Go back to the original user
        self.api_authentication()

    def test_get_history_user_success(self):
        messages = [
            (self.user.pk, 'Hey!'),
            (self.user.pk, 'Whats up?'),
            (self.mock_user.pk, 'Nothing')
        ]

        response = self.client.get(reverse('chat-history', kwargs={'pk': self.chat['id']}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        messages_history = response.data
        self.assertEqual(len(messages), len(messages_history))
        for i, message in enumerate(messages):
            self.assertEqual(message[0], messages_history[i]['author']['id'])
            self.assertEqual(message[1], messages_history[i]['text'])

    def test_get_history_mock_user_success(self):
        messages = [
            (self.user.pk, 'Hey!'),
            (self.user.pk, 'Whats up?'),
            (self.mock_user.pk, 'Nothing')
        ]

        # Change authenticated user to the mock one
        token = AuthToken.objects.create(user=self.mock_user)[1]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.get(reverse('chat-history', kwargs={'pk': self.chat['id']}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        messages_history = response.data
        self.assertEqual(len(messages), len(messages_history))
        for i, message in enumerate(messages):
            self.assertEqual(message[0], messages_history[i]['author']['id'])
            self.assertEqual(message[1], messages_history[i]['text'])

        # Go back to the original user
        self.api_authentication()

    def test_get_history_fail_user(self):
        fail_user = User.objects.create_user(username='fail_user', password='test')
        token = AuthToken.objects.create(user=fail_user)[1]

        # Change authenticated user to the fail one
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.get(reverse('chat-history', kwargs={'pk': self.chat['id']}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, 'Chat does not exist')

        # Go back to the original user
        self.api_authentication()

    def test_get_history_fail_invalid_chat_id(self):
        response = self.client.get(reverse('chat-history', kwargs={'pk': 0}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, 'Chat does not exist')

    def test_not_authenticated_user_fail(self):
        self.client.credentials(HTTP_AUTHORIZATION='')

        response = self.client.get(reverse('chat-history', kwargs={'pk': 0}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserChatsTestCase(APITestCase):

    create_chat_url = reverse('create-chat')
    user_chats_url = reverse('chat-user')

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.token = AuthToken.objects.create(user=self.user)[1]
        self.api_authentication()
        self.mock_user = User.objects.create_user(username='mock', password='mock')
        self.chat1 = self.test_create_chat()
        self.chat2 = self.test_create_chat()
        self.chat3 = self.test_create_chat_another_user()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_create_chat(self):
        data = {
            'invited': f'[{self.mock_user.pk}]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['chat']

    def test_create_chat_another_user(self):
        token = AuthToken.objects.create(user=self.mock_user)[1]

        # Change authenticated user to the mock one
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        data = {
            'invited': '[]'
        }
        response = self.client.post(self.create_chat_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Go back to the original user
        self.api_authentication()

        return response.data['chat']

    def test_user_chats_success(self):
        response = self.client.get(self.user_chats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        chats = response.data
        self.assertEqual(len(chats), 2)
        self.assertEqual(chats[0]['creator']['id'], self.user.pk)
        self.assertEqual(chats[1]['creator']['id'], self.user.pk)

    def test_mock_user_chats_success(self):
        token = AuthToken.objects.create(user=self.mock_user)[1]

        # Change authenticated user to the mock one
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.get(self.user_chats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        chats = response.data
        self.assertEqual(len(chats), 3)
        self.assertEqual(chats[0]['creator']['id'], self.user.pk)
        self.assertEqual(chats[1]['creator']['id'], self.user.pk)
        self.assertEqual(chats[2]['creator']['id'], self.mock_user.pk)

        # Go back to the original user
        self.api_authentication()

    def test_not_authenticated_user_fail(self):
        self.client.credentials(HTTP_AUTHORIZATION='')

        response = self.client.get(self.user_chats_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

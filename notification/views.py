from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from notification.models import ChatMessage
import requests
import json
import time

from .models import ChatMessage
import os


class MistralChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    api_key = os.getenv("API_KEY")
    model = "mistral-large-latest"
    last_request_time = None

    def call_mistral_api(self, message):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an HR assistant. Only respond to HR-related queries such as workplace issues, company policies, stress, and career development. Politely decline unrelated topics."
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        }

        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data
            )

            self.last_request_time = time.time()

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                time.sleep(retry_after)
                return self.call_mistral_api(message)

            response.raise_for_status()

            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            error_msg = f"API Error: {str(e)}"
            if hasattr(e, 'response') and e.response:
                try:
                    error_details = e.response.json()
                    error_msg += f"\nDetails: {json.dumps(error_details, indent=2)}"
                except:
                    error_msg += f"\nStatus: {e.response.status_code}"
            return error_msg
        except Exception as e:
            return f"Unexpected Error: {str(e)}"

    def post(self, request):
        prompt = request.data.get('prompt')
        user = request.user

        if not prompt:
            return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)

        answer = self.call_mistral_api(prompt)

        chat_record = ChatMessage.objects.create(
            user=user,
            conversation=[{"user": prompt}, {"mistral": answer}],
            updated_at=timezone.now()
        )

        return Response({
            "chat_id": chat_record.id,
            "response": answer
        }, status=status.HTTP_200_OK)

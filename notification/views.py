from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django.utils import timezone
from notification.models import ChatMessage
import requests
import json
import time
from notification.serializers import ChatMessageSerializer
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from .models import ChatMessage
import os


# Short summary of the policy that the AI can use for context
POLICY_SUMMARY = (
    "Workwise company policy covers topics like Code of Conduct, Working Hours (9 AM–5 PM), Leave Entitlement "
    "(21 annual days, 10 sick days), Remote Work, Performance Reviews (bi-annual), Anti-Harassment rules, and Exit Process. "
    "The full policy can be downloaded if needed."
)

# class MistralChatView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     api_key = os.getenv("API_KEY")
#     model = "mistral-small-latest"
#     last_request_time = None

#     def call_mistral_api(self, message, user, pdf_link=None, history_limit=5):
#         # Prepare system context
#         if "policy" in message.lower():
#             system_message = (
#                 f"You are an HR assistant for Workwise. Refer to the following company policy summary to help users:\n"
#                 f"{POLICY_SUMMARY}\n"
#                 "Politely offer to share the PDF download link if more detail is requested."
#             )
#         else:
#             system_message = (
#                "You are an HR assistant From WorkWise organization. Only respond to HR-related queries such as workplace issues, company policies, "
#                 "stress, and career development. Politely decline unrelated topics. and stick to WorkWise only  "
#             )

#         # 🧠 Get last N messages by user (latest first, then reverse)
#         history_records = ChatMessage.objects.filter(user=user).order_by('-updated_at')[:history_limit]
#         history_messages = []

#         for record in reversed(history_records):
#             for entry in record.conversation:
#                 if 'user' in entry:
#                     history_messages.append({"role": "user", "content": entry["user"]})
#                 if 'mistral' in entry:
#                     history_messages.append({"role": "assistant", "content": entry["mistral"]})

#         # 👇 Now append current user message
#         history_messages.insert(0, {"role": "system", "content": system_message})
#         history_messages.append({"role": "user", "content": message})

#         # Prepare payload
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }
#         data = {
#             "model": self.model,
#             "messages": history_messages
#         }

#         try:
#             response = requests.post(
#                 "https://api.mistral.ai/v1/chat/completions",
#                 headers=headers,
#                 json=data
#             )

#             self.last_request_time = time.time()

#             if response.status_code == 429:
#                 retry_after = int(response.headers.get('Retry-After', 5))
#                 time.sleep(retry_after)
#                 return self.call_mistral_api(message, user, pdf_link, history_limit)

#             response.raise_for_status()
#             response_data = response.json()
#             reply = response_data["choices"][0]["message"]["content"]

#             if "policy" in message.lower() and pdf_link:
#                 reply += f"\n\n📄 You can download the full company policy here: {pdf_link}"

#             return reply

#         except requests.exceptions.RequestException as e:
#             error_msg = f"API Error: {str(e)}"
#             if hasattr(e, 'response') and e.response:
#                 try:
#                     error_details = e.response.json()
#                     error_msg += f"\nDetails: {json.dumps(error_details, indent=2)}"
#                 except:
#                     error_msg += f"\nStatus: {e.response.status_code}"
#             return error_msg
#         except Exception as e:
#             return f"Unexpected Error: {str(e)}"

#     def post(self, request):
#         prompt = request.data.get('prompt')
#         user = request.user

#         if not prompt:
#             return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)

#         pdf_link = request.build_absolute_uri("/static/Workwise_Company_Policy.pdf")
#         answer = self.call_mistral_api(prompt, user=user, pdf_link=pdf_link)

#         chat_record = ChatMessage.objects.create(
#             user=user,
#             conversation=[{"user": prompt}, {"mistral": answer}],
#             updated_at=timezone.now()
#         )

#         return Response({
#             "chat_id": chat_record.id,
#             "response": answer
#         }, status=status.HTTP_200_OK)

@csrf_exempt
def mistral_chat_view(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get('prompt') or data.get('message')
        user = request.user if request.user.is_authenticated else None

        if not prompt:
            return JsonResponse({'error': 'Prompt is required'}, status=400)
        if not user:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        pdf_link = request.build_absolute_uri("/static/Workwise_Company_Policy.pdf")
        api_key = os.getenv("API_KEY")
        model = "mistral-small-latest"

        # Set up system message
        if "policy" in prompt.lower():
            system_message = (
                f"You are an HR assistant for Workwise. Refer to the following company policy summary to help users:\n"
                f"{POLICY_SUMMARY}\n"
                "Politely offer to share the PDF download link if more detail is requested."
            )
        else:
            system_message = (
               "You are an HR assistant From WorkWise organization. Only respond to HR-related queries such as workplace issues, "
                "company policies, stress, and career development. Politely decline unrelated topics. and stick to WorkWise only."
            )

        # Retrieve recent conversation history
        history_records = ChatMessage.objects.filter(user=user).order_by('-updated_at')[:5]
        history_messages = []

        for record in reversed(history_records):
            for entry in record.conversation:
                if 'user' in entry:
                    history_messages.append({"role": "user", "content": entry["user"]})
                if 'mistral' in entry:
                    history_messages.append({"role": "assistant", "content": entry["mistral"]})

        history_messages.insert(0, {"role": "system", "content": system_message})
        history_messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": history_messages
        }

        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            time.sleep(retry_after)
            response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)

        response.raise_for_status()
        response_data = response.json()
        reply = response_data["choices"][0]["message"]["content"]

        if "policy"or "policies" in prompt.lower():
            reply += f"\n\n📄 You can download the full company policy here: {pdf_link}"

        # Save chat to DB
        chat_record = ChatMessage.objects.create(
            user=user,
            conversation=[{"user": prompt}, {"mistral": reply}],
            updated_at=timezone.now()
        )

        return JsonResponse({
            "chat_id": chat_record.id,
            "response": reply,
            "status": "success"
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
class ChatHistoryViewSet(viewsets.ModelViewSet):
    permission_classes =[permissions.IsAuthenticated]
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    
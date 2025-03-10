from django.http import JsonResponse
from django.shortcuts import render
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import os

# Initialize ChatBot
chatbot = ChatBot('DairyBot')

# Train ChatBot with Dairy FAQs
trainer = ListTrainer(chatbot)

# Load custom training data
training_data_path = "chatbot/training_data/dairy_faq.yml"

if os.path.exists(training_data_path):
    with open(training_data_path, "r", encoding="utf-8") as file:
        import yaml
        training_data = yaml.safe_load(file)

    for conversation in training_data["conversations"]:
        trainer.train(conversation)

# API to process user messages
def chatbot_response(request):
    if request.method == "GET":
        user_message = request.GET.get('message')
        bot_response = chatbot.get_response(user_message)
        return JsonResponse({"response": str(bot_response)})

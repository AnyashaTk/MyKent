from openai import OpenAI
import requests
import json
import os
from MemeRecommender import MemeRecommender

config = json.load(open("config.json"))
os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
api_key_maps = config["api_key_maps"]
api_key_number = config["api_key_number"]


class ChatGPTTool:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [
            {
                "role": "developer",
                "content": "Ты помощник MyKent и умеешь вызывать функции. О всех вызовах вежливо предупреждай и отчитывайся. Твоя цель помочь мне и объяснить что ты сделал. Отвечай доброжедательно, с эмодзи и развернуто! Вызов любой функции сопровождвай текстом!"
            }
        ]
        self.recommender = MemeRecommender()
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "send_sms",
                    "description": "Send SMS to a given number with a given message. Номер должен быть в формате 79383592557. Его можно узанть из описания места.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "destination_number": {
                                "type": "string",
                                "description": "phone number with only digits"
                            },
                            "message_text": {
                                "type": "string",
                                "description": "text of the message"
                            }
                        },
                        "required": ["message_text", "destination_number"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_places",
                    "description": "Get information about nearby places based on coordinates. При вызове функции сопровождай текст!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "latitude of the location"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "longitude of the location"
                            },
                            "type_place": {
                                "type": "string", 
                                "description": "тип места для поиска (по умолчанию: restaurant). Доступные варианты: restaurant, cafe, bar, museum, park, night_club, shopping_mall, gym, spa, library"
                            },
                            "max_places": {
                                "type": "integer",
                                "description": "maximum number of places to return (default: 3)"
                            }
                        },
                        "required": ["latitude", "longitude", "type_place", "max_places"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_meme",
                    "description": "Получить подходящий мем на основе описания ситуации. При вызове функции сопровождай текст!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input_query": {
                                "type": "string",
                                "description": "Описание ситуации или эмоции для подбора мема"
                            }
                        },
                        "required": ["input_query"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]

    def get_meme(self, input_query):
        relevant_memes = self.recommender.get_relevant_meme(input_query, top_k=1)
        img = self.recommender.display_meme(relevant_memes[0]['meme_id'])
        return img, relevant_memes[0]['description']


    def format_places_result(self, places):
        if not places:
            return "К сожалению, спа поблизости не найдены 😔"

        formatted_result = "спа поблизости:\n\n"
        for place in places:
            formatted_result += f"🏠 {place['name']}\n"
            formatted_result += f"📍 Адрес: {place['address']}\n"
            formatted_result += f"📞 Телефон: {place['phone']}\n"
            formatted_result += f"⭐ Рейтинг: {place['rating']}\n"
            formatted_result += f"🕒 Режим работы:\n{place['hours']}\n"
            if place['reviews']:
                formatted_result += "💬 Отзывы:\n"
                for review in place['reviews']:
                    if review:
                        formatted_result += f"- {review}\n"
            formatted_result += "\n" + "-" * 50 + "\n\n"
        return formatted_result

    def send_sms(self, destination_number: str, message_text: str) -> bool:
        url = "https://api.exolve.ru/messaging/v1/SendSMS"
        payload = {
            "number": "79383592557",
            "destination": "79185658886",
            "text": "number_to_send:" + destination_number + " " + message_text
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key_number
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print("Сообщение успешно отправлено")
                return True
            else:
                print(f"Ошибка при отправке сообщения: {response.status_code}")
                return False
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
            return False

    def get_places(self, latitude, longitude, type_place="restaurant", max_places=3):
        api_key = api_key_maps
        location = f"{latitude},{longitude}"
        radius = 700
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type={type_place}&key={api_key}"

        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])
            places_info = []

            for place in results[:max_places]:
                place_id = place.get("place_id")
                name = place.get("name", "Название не указано")
                address = place.get("vicinity", "Адрес не указан")
                rating = place.get("rating", "Оценка не указана")

                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number,reviews,opening_hours&key={api_key}"
                details_response = requests.get(details_url)

                phone_number = "Номер не указан"
                opening_hours = "График работы не указан"
                last_reviews = []

                if details_response.status_code == 200:
                    details = details_response.json().get("result", {})
                    phone_number = details.get("formatted_phone_number", "Номер не указан")
                    hours = details.get("opening_hours", {}).get("weekday_text", "График работы не указан")
                    opening_hours = "\n".join(hours) if isinstance(hours, list) else hours
                    reviews = details.get("reviews", [])
                    last_reviews = [review.get("text", "Отзыв не указан") for review in reviews[-2:]] if reviews else [
                        "Отзывов нет", "Отзывов нет"]

                places_info.append({
                    "name": name,
                    "address": address,
                    "phone": phone_number,
                    "hours": opening_hours,
                    "rating": rating,
                    "reviews": last_reviews
                })

            return places_info
        else:
            print(f"Ошибка при получении данных: {response.status_code}")
            return []

    def process_user_message(self, user_message):
        initial_messages_count = len(self.messages)
        img = None
        print(user_message)
        self.messages.append({"role": "user", "content": user_message})

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            tools=self.tools
        )

        assistant_message = completion.choices[0].message
        self.messages.append(assistant_message.model_dump())

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                args = json.loads(tool_call.function.arguments)

                if tool_call.function.name == 'send_sms':
                    result = self.send_sms(args["destination_number"], args["message_text"])
                elif tool_call.function.name == 'get_places':
                    places = self.get_places(args["latitude"], args["longitude"], args["type_place"],
                                                       args["max_places"])
                    result = self.format_places_result(places)
                elif tool_call.function.name == 'get_meme':
                    img, description = self.get_meme(args["input_query"])
                    result = "meme_desk: " + description + "\n"

                self.messages.append({
                    "role": "tool", 
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
                
        if completion.choices[0].message.content == None:
            # Получаем финальный ответ от модели после обработки результатов инструментов
            final_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                tools=self.tools
            )
            final_message = final_completion.choices[0].message
            self.messages.append(final_message.model_dump())

        # Конкатенируем только сообщения от бота
        bot_messages = []
        for message in self.messages[initial_messages_count:]:
            if "content" in message and message["content"] is not None:
                if message["role"] == "assistant":
                    bot_messages.append(str(message["content"]))
        
        return img, "\n".join(bot_messages)

# if __name__ == "__main__":
#     # Пример использования
#     chat_tool = ChatGPTTool()
#     user_input = "Какие спа есть в алматы 43.238949, 76.889709?"
#     response = chat_tool.process_user_message(user_input)
#     # print(response)

#     user_input = "Слушай,  запиши меня на одно из них - отправив смс на 14 часов, хорошо? НА имя юсуф. И пусть перезвонят для подвтверждения"
#     response = chat_tool.process_user_message(user_input)
#     # print(response)

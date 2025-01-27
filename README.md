# MyKent

## MyKent - is an LLM agent who helps you find the most interesting and delicious places in the area and book a table at the coolest of them.

### 🗂️ Table of Contents

1. ✨ [About](#✨About)
2. [Features](#Features)
3. [Usecase](#Usecase)
4. [Installation](#Installation)
5. [How to Use](#How-to-Use)
6. [Architecture](#Architecture)
7. [Try it](#Try-it)

### ✨About
MyKent - it is guided by your location, thanks to which it finds great places with the most delicious and interesting dishes. If you want, you can choose where exactly you will go, and if you do not want to think, then boldly trust and go where the agent decides

### Features

1. get a list of locations on demand or periodically
2. search for good places
3. if there is a special place or it is lunchtime or other time, it can offer you to eat somewhere
4. Sends a notification to the cafe that guests are coming to them,
5. If there is information, it specifies the number of people
6. He understands all this by listening to your voice messages


## Usecase

<image src="/docs/images/usecase" alt="Usecase scheme">

 
### Installation

* git clone <>
* cd ./MyKent


### How to Use

* Создайте TELEGRAM_BOT_API переменную среды
* uvicorn main:app --host 127.0.0.1 --port 8000 --reload

### Architecture

<image src="/docs/images/architecture" alt="Architecture scheme">


### Try it

Try to talk with pur bot: 

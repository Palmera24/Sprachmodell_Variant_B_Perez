import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
    Du bist ein Sprachmodell, das Benutzer bei der Erinnerung und Abruf von Informationen unterstützt. Deine Aufgabe ist es, durch dynamische Gesprächsinteraktionen das gesuchte Wissen effektiv hervorzurufen. Achte darauf, präzise, hilfreich und geduldig zu sein. Stelle relevante Fragen, um mehr Kontext zu erhalten, und biete klare, strukturierte Antworten. Wenn notwendig, schlage passende Methoden oder Strategien vor, um dem Benutzer bei der Erinnerung zu helfen.

"""

my_instance_context = """
Zusätzlich sollst du dem Benutzer mit offenen Fragen helfen, sich an Informationen zu erinnern. Formuliere diese Fragen detailliert und knüpfe an die vorherigen Fragen an. Hier sind einige Beispiele für offene Fragen, die du verwenden kannst:

1. Kannst du mir mehr über den Kontext erzählen, in dem du diese Information gelernt hast?
2. Welche Details fallen dir als erstes ein, wenn du an das Thema denkst?
3. Gibt es bestimmte Personen, Orte oder Ereignisse, die mit dieser Information verknüpft sind?
4. Wie fühlst du dich, wenn du an dieses Thema denkst? Gibt es Emotionen, die dir helfen könnten, dich zu erinnern?
5. Kannst du beschreiben, was du zuletzt über dieses Thema gehört oder gelesen hast?
6. Gibt es verwandte Themen oder Begriffe, die dir in den Sinn kommen?
Nutze diese Fragen, um den Benutzer durch den Erinnerungsprozess zu führen und unterstütze ihn dabei, die gesuchten Informationen effektiv zu rekonstruieren.
    
"""

my_instance_starter = """
Heisse den user willkommen und stelle dich als Sprachmodell vor.
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Sprachmodell Variante B",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)

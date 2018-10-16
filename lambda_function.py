import json
import sys
import urllib
import urlparse
from urllib2 import HTTPError
from urllib2 import URLError
from alexa_response import get_session_attributes, get_response, give_response

def lambda_handler(event, context):
    # print event
    if event["session"]["new"]:
        on_session_started(event["session"])
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def get_welcome_response():
    response_text = "Hi! I am Ginger, I can help you correct your english. Try me by saying correct the statement"
    response = get_response(outputSpeech_text = response_text, shouldEndSession = False)
    session_attributes = get_session_attributes()
    return give_response(response = response, session_attributes = session_attributes)

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    if intent_name == "sentenceIntent":
        if intent_request["dialogState"] not in ("COMPLETED", "IN_PROGRESS"):
            return { "version": "1.0", "response": { "shouldEndSession": False, "directives": [ { "type": "Dialog.Delegate" } ]}}
        else:
            return statement(intent["slots"]["query_statement"]["value"])
    elif intent_name == "AMAZON.CancelIntent":
        return get_cancel_instructions()
    elif intent_name == "AMAZON.StopIntent":
        return get_cancel_instructions()
    elif intent_name == "AMAZON.HelpIntent":
        return get_helping_instructions()

def session_end_greetings():
    outputSpeech_text = "I hope you got your answer"
    return get_response(outputSpeech_text = outputSpeech_text), get_session_attributes()

def get_cancel_instructions():
    response, session_attributes = session_end_greetings()
    return give_response(response = response, session_attributes = session_attributes)

def get_helping_instructions():
    outputSpeech_text = "I can help you correct your english. Try me by saying correct the statement"
    response = get_response(outputSpeech_text = outputSpeech_text, shouldEndSession = False)
    session_attributes = get_session_attributes()
    return give_response(response = response, session_attributes = session_attributes)
    
def get_ginger_url(text):
    """Get URL for checking grammar using Ginger.
    @param text English text
    @return URL
    """
    API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"

    scheme = "http"
    netloc = "services.gingersoftware.com"
    path = "/Ginger/correct/json/GingerTheText"
    params = ""
    query = urllib.urlencode([
        ("lang", "US"),
        ("clientVersion", "2.0"),
        ("apiKey", API_KEY),
        ("text", text)])
    fragment = ""

    return(urlparse.urlunparse((scheme, netloc, path, params, query, fragment)))


def get_ginger_result(text):
    """Get a result of checking grammar.
    @param text English text
    @return result of grammar check by Ginger
    """
    url = get_ginger_url(text)

    try:
        response = urllib.urlopen(url)
    except HTTPError as e:
            print("HTTP Error:", e.code)
            quit()
    except URLError as e:
            print("URL Error:", e.reason)
            quit()

    try:
        result = json.loads(response.read().decode('utf-8'))
    except ValueError:
        print("Value Error: Invalid server response.")
        quit()

    return(result)


def statement(original_text):
    """main function"""
    # original_text = " ".join(sys.argv[1:])
    if len(original_text) > 600:
        print("You can't check more than 600 characters at a time.")
        outputSpeech_text = "You can't check more than 600 characters at a time."
        response = get_response(outputSpeech_text)
        session_attributes = get_session_attributes()
        return give_response(response = response, session_attributes = session_attributes)
        # quit()
    fixed_text = original_text
    correct_statement = original_text
    results = get_ginger_result(original_text)

    # Correct grammar
    if(not results["LightGingerTheTextResult"]):
        print("Good English :)")
        outputSpeech_text = "Good English"
        response = get_response(outputSpeech_text)
        session_attributes = get_session_attributes()
        return give_response(response = response, session_attributes = session_attributes)
        # quit()

    # Incorrect grammar
    gap, fixed_gap = 0, 0
    mistake_text = ""
    card_mistake_text = ""
    for result in results["LightGingerTheTextResult"]:
        # print result
        if(result["Suggestions"]):
            from_index = result["From"] + gap
            to_index = result["To"] + 1 + gap
            suggest = result["Suggestions"][0]["Text"]
            mistake = result["Mistakes"][0]["Definition"]

            # Colorize text
            # colored_incorrect = ColoredText.colorize(original_text[from_index:to_index], 'red')[0]
            # colored_suggest, gap = ColoredText.colorize(suggest, 'green')
            # correct_statement = fixed_text[:from_index-fixed_gap] + suggest + fixed_text[to_index-fixed_gap:]
            mistake_phrase = original_text[from_index:to_index]
            original_text = original_text[:from_index] + '"' + original_text[from_index:to_index] + '"' + original_text[to_index:]
            fixed_text = fixed_text[:from_index-fixed_gap] + '"' + suggest + '"' + fixed_text[to_index-fixed_gap:]
            correct_statement = correct_statement[:from_index-fixed_gap-gap] + suggest + correct_statement[to_index-fixed_gap-gap:]

            gap += 2
            fixed_gap += to_index-from_index-len(suggest)
            mistake_text += mistake_phrase + " is converted to " + suggest + " reason " + mistake + "."
            card_mistake_text += mistake_phrase + " - " + suggest + " : " + mistake + "\n"

    print("original_text: " + original_text)
    print("fixed_text:   " + fixed_text)
    print("final: " + correct_statement)
    print card_mistake_text
    print mistake_text
    outputSpeech_text = "The correct statement is " + correct_statement
    card_text = "original_text: " + original_text + "\n" + "fixed_text:   " + fixed_text + '\n' + card_mistake_text
    response = get_response(outputSpeech_text, outputSpeech_type = "PlainText", card_type = "Standard", card_title = "Ginger English", card_text = card_text)
    session_attributes = get_session_attributes(original_text = original_text, fixed_text = fixed_text)
    return give_response(response = response, session_attributes = session_attributes)


if __name__ == '__main__':
    original_text = " ".join(sys.argv[1:])
    statement(original_text)

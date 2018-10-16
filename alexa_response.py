def get_session_attributes(original_text = "", fixed_text = ""):
    sessionAttributes = {}
    sessionAttributes["original_statement"] = original_text
    sessionAttributes["fixed_statement"] = fixed_text
    return sessionAttributes

def get_outputSpeech(outputSpeech_type, outputSpeech_text):
    outputSpeech = {}
    outputSpeech["type"] = outputSpeech_type
    outputSpeech["text"] = outputSpeech_text
    return outputSpeech

def get_card(card_type, card_title, card_content, card_text):
    card = {}
    card["type"] = card_type
    card["title"] = card_title
    card["content"] = card_content
    card["text"] = card_text
    return card

def get_repromt(repromt_outputSpeech_type, repromt_outputSpeech_text):
    reprompt = {}
    reprompt["outputSpeech"] = get_outputSpeech(repromt_outputSpeech_type, repromt_outputSpeech_text)
    return reprompt

def get_response(outputSpeech_text, outputSpeech_type = "PlainText", card_type = "Standard", card_title = "", card_content = "", card_text = "", repromt_outputSpeech_type = "PlainText", repromt_outputSpeech_text = "", shouldEndSession = True):
    response = {}
    response["outputSpeech"] = get_outputSpeech(outputSpeech_type, outputSpeech_text)
    if card_title != "":
        response["card"] = get_card(card_type, card_title, card_content, card_text)
    if repromt_outputSpeech_text != "":
        response["reprompt"] = get_repromt(repromt_outputSpeech_type, repromt_outputSpeech_text)
    response["shouldEndSession"] = shouldEndSession
    return response

def give_response(response, session_attributes = {}):
    lambda_response = {}
    lambda_response["version"] = "string"
    if session_attributes != {}:
        lambda_response["sessionAttributes"] = session_attributes
    lambda_response["response"] = response
    return lambda_response
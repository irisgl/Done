from models.sms import SmsMessage

def extract_sms_data(request_body, context):
    """
    Extract SMS message data and update the context dictionary.
    
    :param request_body: The raw request body containing the SMS message data.
    :param context: The context dictionary to update with extracted information.
    :return: The sms_sid and the recipient's WhatsApp number.
    """
    print("hello from extract sms data")
    sms_message = SmsMessage(request_body)
    context['user_message'] = sms_message.Body if sms_message.Body is not None else ""
    context['user_phone'] = sms_message.WaId or "Unknown"
    context['profile_name'] = sms_message.ProfileName or "Unknown"
    sms_sid = sms_message.SmsSid
    to_whatsapp_number = 'whatsapp:' + context['user_phone']
    
    print(f"Extracted sms_message: {sms_message}, sms_sid: {sms_sid}, to_whatsapp_number: {to_whatsapp_number}")
    
    return sms_message,sms_sid, to_whatsapp_number

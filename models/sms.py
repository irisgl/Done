import urllib.parse

def convert_phone_number(phone_number):
    if phone_number.startswith('+'):
        phone_number = phone_number[1:]  # Remove the '+'
    if phone_number.startswith('0'):
        return '972' + phone_number[1:]
    return phone_number

class SmsMessage:
    required_fields = {
        'SmsMessageSid': str,
        'NumMedia': int,
        'ProfileName': str,
        'MessageType': str,
        'SmsSid': str,
        'WaId': str,
        'SmsStatus': str,
        'To': str,
        'NumSegments': int,
        'ReferralNumMedia': int,
        'MessageSid': str,
        'AccountSid': str,
        'From': str,
        'ApiVersion': str
    }

    optional_fields = ['Body']  # Body can be optional

    def __init__(self, byte_string):
        decoded_string = byte_string.decode('utf-8')
        parsed_data = urllib.parse.parse_qs(decoded_string)
        data_dict = {k: v[0] for k, v in parsed_data.items()}

        self._validate(data_dict)

        for field in self.required_fields:
            setattr(self, field, data_dict.get(field, "Unknown"))

        # Handle optional Body field
        self.Body = data_dict.get('Body', "")  # Default to empty string if Body is missing

    def _validate(self, data):
        # Ensure required fields are present, except Body if NumMedia > 0
        num_media = int(data.get('NumMedia', '0'))
        required_checks = self.required_fields.keys() if num_media == 0 else self.required_fields.keys() - set(self.optional_fields)
        for field in required_checks:
            if field not in data:
                raise ValueError(f'Missing or None value for required field: {field}')
            if isinstance(self.required_fields[field], int) and not data[field].isdigit():
                raise ValueError(f'Field {field} should be of type int and a valid integer')

    def __repr__(self):
        return (f'SmsMessage(SmsMessageSid={self.SmsMessageSid}, NumMedia={self.NumMedia}, '
                f'ProfileName={self.ProfileName}, MessageType={self.MessageType}, SmsSid={self.SmsSid}, '
                f'WaId={self.WaId}, SmsStatus={self.SmsStatus}, Body={self.Body}, To={self.To}, '
                f'NumSegments={self.NumSegments}, ReferralNumMedia={self.ReferralNumMedia}, '
                f'MessageSid={self.MessageSid}, AccountSid={self.AccountSid}, From={self.From}, '
                f'ApiVersion={self.ApiVersion})')

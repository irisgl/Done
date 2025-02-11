from models.database import UserMessage
from datetime import datetime
from models.database import AsanaTask


def store_user_message(session, message_type, context, results=None, sms_message=None):
    """
    Store a user message in the database.

    :param session: The database session
    :param message_type: Type of the message (e.g., "NORMAL", "WHATSAPP")
    :param context: The context dictionary containing user information
    :param results: (Optional) The result of processing the user message
    :param sms_message: (Optional) The SMS message object
    :return: The stored UserMessage object
    """
    new_user_message = UserMessage(
        type=message_type,
        message=context['user_message'] if not sms_message else None,
        smsbody={
            "SmsMessageSid": sms_message.SmsMessageSid,
            "NumMedia": sms_message.NumMedia,
            "ProfileName": sms_message.ProfileName,
            "messageType": sms_message.MessageType,
            "body": sms_message.Body,
            "From": sms_message.From,
            "to": sms_message.To,
            "NumMedia": sms_message.NumMedia,
            "MessageSid": sms_message.MessageSid,
            "AccountSid": sms_message.AccountSid,
            "ApiVersion": sms_message.ApiVersion
        } if sms_message else {},
        from_phone=context['user_phone'],
        to_phone=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        thread_result=results
    )
    session.add(new_user_message)
    session.commit()
    return new_user_message

def store_asana_task(session, task, settings, task_name, task_notes, user_message_id):
    """
    Store an Asana task in the database.

    :param session: The database session
    :param task: The Asana task data
    :param settings: The settings object containing configuration values
    :param task_name: Name of the task
    :param task_notes: Notes for the task
    :param user_message_id: ID of the related UserMessage
    :return: The stored AsanaTask object
    """
    new_asana_task = AsanaTask(
        task_id=task["gid"],
        workspace_id=settings.WORKSPACE_ID,
        project_id=settings.PROJECT_ID,
        task_name=task_name,
        task_notes=task_notes,
        user_message_id=user_message_id
    )
    session.add(new_asana_task)
    session.commit()
    return new_asana_task
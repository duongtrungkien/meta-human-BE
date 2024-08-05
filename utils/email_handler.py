import smtplib, ssl
import sys

def send_email(host_email, visitor):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "aimetahuman2802@gmail.com"  
    receiver_email = host_email
    password = "qngo akhs makh tqoh"
    # message = """\
    # Subject: Invitor arrived. DO NOT REPLY

    # Your visitor {} are waiting at the reception.
    # """.format(visitor)

    toaddr = host_email
    fromaddr = "aimetahuman2802@gmail.com"
    message_subject = "Invitor arrived. DO NOT REPLY"
    message_text = "Your visitor {} are waiting at the reception.".format(visitor)
    message = "From: %s\r\n"%fromaddr + "To: %s\r\n"%toaddr + "Subject: %s\r\n"%message_subject + "\r\n" + message_text


    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

if __name__ == "__main__":
    send_email(sys.argv[1], sys.argv[2])
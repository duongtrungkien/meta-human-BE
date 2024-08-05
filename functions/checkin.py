
from utils.email_handler import send_email

class CheckinHandler:
    def __init__(self):
        self.dummy_data = [
            {
                "id": 1,
                "name": "Kien Duong",
                "email": "kien.duong@elisa.fi",
                "visitors": [
                    {"name": "Hien Truong", "email": "hien.truong@elisa.fi", "checkedin": False},
                    {"name": "Santeri", "email": "kien.duong@elisa.fi", "checkedin": False}
                ]
            }
        ]
    
    def get_host_list(self):
        return self.dummy_data

    def get_host_data_by_id(self, id):
        return next((host for host in self.dummy_data if host["id"] == id), None)

    def update_visitor_checkin_status(self):
        return

    def inform_host(self, host_email, visitor_name):
        try:
            # host_info = self.get_host_data_by_id(host_id)
            # host_email = host_info["email"]
            send_email(host_email, visitor_name)
            return "Thank you! I sent the notification to the host. He/She will come shortly. You can ask me anything about Elisa while waiting?"
        except:
            return "There is something wrong. Please try again"



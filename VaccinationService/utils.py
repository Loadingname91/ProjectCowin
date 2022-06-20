from VaccinationService.models import Certificate
from datetime import datetime

def write_data_for_email(data):
    preset = "##################### CERTIFICATE ###############\n"
    prefield = "####################"
    response_data = preset
    for each in data:
        if each['status'] == "second_dose":
            response_data += prefield + "SECOND DOSE DATA"
        else:
            response_data = prefield + "FIRST DOSE DATA"

        response_data += prefield + "Username" + each["user"] + "\n"
        response_data += prefield + "DATE GIVEN: " + each['date_given'].strftime("%Y-%m-%d") + "\n"
        response_data += prefield + "DATE OF EXPIRY: " + each['date_expiry'].strftime("%Y-%m-%d") + "\n"
        response_data += prefield + "CENTER GIVEN: " + each['center'] + "\n"

    response_list = [i.user.email for i in
                     Certificate.objects.filter(user__username=data[0]['user'])
                     ]
    return response_data, response_list

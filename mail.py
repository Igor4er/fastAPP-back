import resend
from config import CONFIG


resend.api_key = CONFIG.resend_token.get_secret_value()

msg_f = "Вітаю, перейдіть за посиланням для входу: {link}"

def make_link_msg(fmt: str, key: str):
    link = fmt.format(key=key)
    fmtd_link = msg_f.format(link=link)
    return fmtd_link

def send_conf_mail_to(to: str, msg: str):
    params = {
        "from": "fastAPP <noreply@mail.ig4er.link>",
        "to": [to],
        "subject": "fastAPP login",
        "html": msg
    }
    try:
        _ = resend.Emails.send(params)
    except Exception as E:
        print(E)
        return False
    return True
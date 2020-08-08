from bottle import route, run, template, request

@route('/')
def index():
    return ('<b>Hi</b>!')
#to test point: http://localhost:8080/

@route('/about')
def about():
    return ('<b>About Page</b>!')
    #to test point: http://localhost:8080/about

@route('/secrets')
def secret():
    try:
        key = request.headers["AUTHENTICATION"]
        page_info = secretchecker(key)
        return (page_info)
    except KeyError:
        msg = ("<b> You'll need permission to be here.</b>")
        return msg
#to test point: http://localhost:8080/secrets

def secretchecker(lock):
    if lock == '11':
        msg = ("<b> Unlimited powah. </b><br> You're an unlimited user. Here's your unlimited info </b><br> <br> Huzza!</br>")
    elif lock == '22':
        msg = ("<b> You are limited. </b><br> You're a limited user. Seeing limited info </b>")
    else:
        msg = ("<b> You need the right keys. </b>")

    return msg

run(reloader=True, debug=True, host='localhost', port=8080)
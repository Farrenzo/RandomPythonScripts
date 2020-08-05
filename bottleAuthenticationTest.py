from bottle import route, run, template

@route('/')
def index():
    return ('<b>Hello</b>')
#to test point: http://localhost:8080/about

@route('/about')
def about():
    return ('<b>About Page</b>!')
#to test point: http://localhost:8080/about

def secretchecker(sk):
    accesstoken = 0

    secret_key  = 'limiteduser-limitedinfo' 
    secret_key1 = 'unlimiteduser-unlimitedinfo' 

    # point to: http://localhost:8080/secrets/limiteduser-limitedinfo
    # point to: http://localhost:8080/secrets/unlimiteduser-unlimitedinfo
    # point to: http://localhost:8080/secrets/wrong-wrong

    if sk == secret_key:
        accesstoken = 1
    elif sk == secret_key1:
        accesstoken = 2
    else:
        pass

    return accesstoken

@route('/secrets/<key_access>')
def secret(key_access):
    key_access = secretchecker(key_access)
    if key_access == 1:
        msg = "<b> You are limited. </b>"
    elif key_access == 2:
        msg = "<b> Unlimited powah. </b>"
    elif key_access == 0:
        msg = "<b> You shouldn't have come here. </b>"
        
    return (msg)

run(host='localhost', port=8080)
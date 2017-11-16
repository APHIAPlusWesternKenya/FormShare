from pyramid.security import authenticated_userid
from ..config.auth import getUserData
from pyramid.httpexceptions import HTTPFound
from pyramid.session import check_csrf_token
from pyramid.httpexceptions import HTTPNotFound
from formencode.variabledecode import variable_decode
from pyramid.response import Response
from hashlib import md5
import uuid

#ODKView is a Digest Authorization view. It automates all the Digest work
class odkView(object):
    def __init__(self, request):
        self.request = request
        self._ = self.request.translate
        self.nonce = md5(str(uuid.uuid4())).hexdigest()
        self.opaque = request.registry.settings['auth.opaque']
        self.realm = request.registry.settings['auth.realm']
        self.authHeader = {}
        self.user = ""

    def getAuthDict(self):
        authheader = self.request.headers["Authorization"].replace(", ", ",")
        authheader = authheader.replace('"', "")
        autharray = authheader.split(",")
        for e in autharray:
            t = e.split("=")
            self.authHeader[t[0]] = t[1]

    def authorize(self,correctPassword):
        HA1 = ""
        HA2 = ""
        if self.authHeader["qop"] == 'auth':
            HA1 = md5(self.user + ":" + self.realm + ":" + correctPassword)
            HA2 = md5(self.request.method + ":" + self.authHeader["uri"])
        if self.authHeader["qop"] == 'auth-int':
            HA1 = md5(self.user + ":" + self.realm + ":" + correctPassword)
            MD5Body = md5(self.request.body).hexdigest()
            HA2 = md5(self.request.method + ":" + self.authHeader["uri"] + ":" + MD5Body)
        if HA1 == "":
            HA1 = md5(self.user + ":" + self.realm + ":" + correctPassword)
            HA2 = md5(self.request.method + ":" + self.authHeader["uri"])

        authLine = ":".join(
            [HA1.hexdigest(), self.authHeader["nonce"], self.authHeader["nc"], self.authHeader["cnonce"], self.authHeader["qop"], HA2.hexdigest()])

        resp = md5(authLine)
        if resp.hexdigest() == self.authHeader["response"]:
            return True
        else:
            return False

    def askForCredentials(self):
        headers = [('WWW-Authenticate',
                    'Digest realm="' + self.realm + '",qop="auth,auth-int",nonce="' + self.nonce + '",opaque="' + self.opaque + '"')]
        reponse = Response(status=401, headerlist=headers)
        return reponse

    def createXMLResponse(self,XMLData):
        headers = [('Content-Type', 'text/xml; charset=utf-8'), ('X-OpenRosa-Accept-Content-Length', '10000000'),
                   ('Content-Language', self.request.locale_name), ('Vary', 'Accept-Language,Cookie,Accept-Encoding'),
                   ('X-OpenRosa-Version', '1.0'), ('Allow', 'GET, HEAD, OPTIONS')]
        response = Response(headerlist=headers, status=200)
        response.text = unicode(XMLData, "utf-8")
        return response


    def __call__(self):
        if "Authorization" in self.request.headers:
            self.getAuthDict()
            self.user = self.authHeader["Digest username"]
            return self.processView()
        else:
            headers = [('WWW-Authenticate',
                        'Digest realm="' + self.realm + '",qop="auth,auth-int",nonce="' + self.nonce + '",opaque="' + self.opaque + '"')]
            reponse = Response(status=401, headerlist=headers)
            return reponse

    def processView(self):
        #At this point children of odkView have:
        # self.user which us the user requesting ODK data
        # authorize(self,correctPassword) which checks if the password in the authorization is correct
        # askForCredentials(self) which return a response to ask again for the credentials
        # createXMLResponse(self,XMLData) that can be used to return XML data to ODK with the required headers
        return {}

#This is the most basic public view. Used for 404 and 500. But then used for others more advanced classes
class publicView(object):
    def __init__(self, request):
        self.request = request
        self._ = self.request.translate

    def __call__(self):
        return self.processView()

    def processView(self):
        return {}

    def getPostDict(self):
        dct = variable_decode(self.request.POST)
        return dct

class privateView(object):
    def __init__(self, request):
        self.request = request
        self.user = None
        self._ = self.request.translate

    def __call__(self):
        login = authenticated_userid(self.request)
        self.user = getUserData(login,self.request)
        if (self.user == None):
            return HTTPFound(location=self.request.route_url('login'))

        if self.request.method == 'POST':
            safe = check_csrf_token(self.request,raises=False)
            if not safe:
                return HTTPNotFound()

        return self.processView()

    def processView(self):
        return {'activeUser': self.user}

    def getPostDict(self):
        dct = variable_decode(self.request.POST)
        return dct
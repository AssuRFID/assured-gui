import os
import requests

class RestClient():
    def __init__(self, url):
        self.api_url = url
    
    def make_req(self, path, method=requests.get):
        resp = method(os.path.join(self.api_url, path))
        if resp.status_code != 200:
            raise ApiError('GET {} {}'.format(path, resp.status_code))
        return resp.json()

    def make_req_json(self, path, data, method=requests.get):
        resp = method(os.path.join(self.api_url, path), json=data)
        if resp.status_code != 200:
            raise ApiError('GET {} {}'.format(path, resp.status_code))
        return resp.json()

    def tags_list(self):
        return self.make_req('tags')['tags']

    def auth_tag(self, uid):
        json = {"uid": uid}
        return self.make_req_json('tags/auth', json)

    def tag_move(self, uid):
        previous = self.auth_tag(uid)['tag']
        json = {"inside_room1": not previous['inside_room1']}
        self.make_req_json('tags/{}'.format(previous['id']),
                           json,
                           requests.put)

class ApiError(Exception):
    pass

#!/usr/bin/env python

import json
import uuid
import pprint
from SimpleXMLRPCServer import SimpleXMLRPCServer

import frontmatter

# h/t <https://gist.github.com/brentsimmons/9398899>
# h/t <http://1998.xmlrpc.com/metaWeblogApi.html>

class Site(object):
    def __init__(self, site_id):
        self.site_id = site_id
        self.site_root = "/Users/eric/Dropbox (Personal)/Websites/%s/" % (site_id,)

    def NewPost(self, struct, publish):
        guid = self.GeneratePostID()
        struct['postid'] = guid
        (blog_id, post_id) = guid.split(':')
        with open(post_id, 'w') as fp:
            json.dump(struct, fp)
        return guid

    def GetPost(self, post_id):
        with open(post_id) as fp:
            return json.load(fp)

    def GeneratePostID(self):
        return "%s:%s.md" % (self.site_id, uuid.uuid4())

class MetaWeblogAPI(object):
    def NewPost(self, site_id, username, password, struct, publish):
        site = Site(site_id)
        return site.NewPost(struct, publish)

    def GetPost(self, guid, username, password):
        (site_id, post_id) = guid.split(':')
        site = Site(site_id)
        return site.GetPost(post_id)

def main(args):
    server = SimpleXMLRPCServer(('localhost', 1894))
    server.register_introspection_functions()

    metaweblog = MetaWeblogAPI()
    server.register_function(metaweblog.NewPost, 'metaWeblog.newPost')
    server.register_function(metaweblog.GetPost, 'metaWeblog.getPost')
    server.serve_forever()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)

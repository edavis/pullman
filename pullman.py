#!/usr/bin/env python

import frontmatter
from itertools import count
from SimpleXMLRPCServer import SimpleXMLRPCServer

# h/t <https://gist.github.com/brentsimmons/9398899>
# h/t <http://1998.xmlrpc.com/metaWeblogApi.html>
class MetaWeblogAPI(object):
    def __init__(self):
        self.post_id_counter = count(1)
        self.posts = {}

    def getRecentPosts(self, blog_id, username, password, post_count):
        recent_posts = []
        for post_id in self.posts.keys():
            recent_posts.append(self.posts[post_id])
        return recent_posts

    def getCategories(self, blog_id, username, password):
        return []

    def getPost(self, post_id, username, password):
        return self.posts[post_id]

    def newPost(self, blog_id, username, password, struct, publish):
        post_id = next(self.post_id_counter)
        struct.update({'postid': post_id})
        self.posts[post_id] = struct
        return post_id

    def editPost(self, post_id, username, password, struct, publish):
        self.posts[post_id] = struct
        return True

    def deletePost(self, appkey, post_id, username, password, publish):
        del self.posts[int(post_id)]
        return True

    # h/t <https://micro.blog/elliot/217975>
    # getUserInfo

def main(args):
    server = SimpleXMLRPCServer(('localhost', 1894))
    server.register_introspection_functions()

    mwa = MetaWeblogAPI()
    server.register_function(mwa.newPost, 'metaWeblog.newPost')
    server.register_function(mwa.getPost, 'metaWeblog.getPost')
    server.register_function(mwa.editPost, 'metaWeblog.editPost')
    server.register_function(mwa.deletePost, 'blogger.deletePost')
    server.register_function(mwa.getRecentPosts, 'metaWeblog.getRecentPosts')
    server.register_function(mwa.getCategories, 'metaWeblog.getCategories')

    server.serve_forever()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)

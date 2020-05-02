#!/usr/bin/env python

import os
import re
import pytz
import json
import frontmatter
from datetime import datetime
from SimpleXMLRPCServer import SimpleXMLRPCServer

# h/t <https://gist.github.com/brentsimmons/9398899>
# h/t <http://1998.xmlrpc.com/metaWeblogApi.html>

class Site(object):
    def __init__(self, site_id):
        self.site_id = site_id

    def ExtractSlug(self, now, struct):
        slug = None

        for item in struct.get('custom_fields', []):
            if item['key'] == 'slug':
                slug = item['value']
                break

        if not slug and struct['title']:
            title = struct['title']
            slug = re.sub(r'[\W_]+', '-', title.lower())

        if not slug and not struct['title']:
            now = now.replace(microsecond=0)
            slug = re.sub(r'[\W_]+', '-', str(now))

        return slug

    def AddToManifest(self, post_id):
        if not os.path.exists('manifest.json'):
            manifest = []
        else:
            manifest = json.load(open('manifest.json'))

        manifest.insert(0, post_id)

        json.dump(manifest, open('manifest.json', 'w'))

    def NewPost(self, struct, publish):
        # Create the YYYY/MM folder the content will live in
        now = datetime.now(pytz.timezone('US/Pacific'))
        content_root = '%d/%02d' % (now.year, now.month)
        if not os.path.isdir(content_root):
            os.makedirs(content_root)

        # Grab or create the slug and build the postid
        slug = self.ExtractSlug(now, struct)
        guid = "%s:%s/%s.md" % (self.site_id, content_root, slug)
        struct['postid'] = guid

        (blog_id, post_id) = guid.split(':')

        # Write the post to disk
        with open(post_id, 'w') as fp:
            post = frontmatter.Post(struct['description'])
            post['title'] = struct['title']
            post['guid'] = struct['postid']

            for item in struct.get('custom_fields', []):
                post[item['key']] = item['value']

            frontmatter.dump(post, fp)

        # Add the post to the site manifest
        self.AddToManifest(post_id)

        return guid

    def GetPost(self, post_id):
        with open(post_id) as fp:
            post = frontmatter.load(fp)
        struct = post.metadata.copy()
        struct['postid'] = post['guid']
        struct['description'] = post.content
        return struct

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

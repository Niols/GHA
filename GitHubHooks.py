#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import loads
from FrontBot import C
from Prnt import V

class GithubHooks:

    def handle (self, headers, body):
        if 'X-Github-Event' in headers.keys():
            return getattr(self, headers['X-Github-Event']) (headers, loads(body))
        return ''

    def commit_comment (self, headers, body):
        return '[%s] %s commented on commit %s. (%s)' % ( C.Pink( body['repository']['full_name'] ),
                                                          C.Cyan( body['comment']['user'] ),
                                                          C.Gray( body['comment']['commit_id'][:7] ),
                                                          C.Blue( body['comment']['html_url'], False ) ) # miniurl

    def create (self, headers, body):
        if body['ref_type'] == 'repository':
            return '[%s] %s created a repository. (%s)' % ( C.Pink( body['repository']['full_name'] ),
                                                            C.Cyan( body['sender']['login'] ),
                                                            C.Blue( body['repository']['html_url'], False ) ) # miniurl
        else:
            return '[%s] %s created the %s %s.' % ( C.Pink( body['repository']['full_name'] ),
                                                    C.Cyan( body['sender']['login'] )
                                                    body['ref_type'],
                                                    C.Red( body['ref'] ) )

    def delete (self, headers, body):
        return '[%s] %s deleted the %s %s.' % ( C.Pink( body['repository']['full_name'] ),
                                                C.Cyan( body['sender']['login'] ),
                                                body['ref_type'],
                                                C.Red( body['ref'] ) )

    def deployment (self, headers, body):
        V.prnt( 'GithubHooks.deployment', V.ERROR )
        return '[%s] The %s environment has been deployed. (~)' % ( C.Pink( body['repository']['full_name'] ),
                                                                    C.Bold( body['deployment']['environment'] ) )

    def deployment_status (self, headers, body):
        V.prnt( 'GithubHooks.deployment', V.ERROR )
        return '[%s] The %s environment has been deployed with %s.' % ( C.Pink( body['repository']['full_name'] ),
                                                                        C.Bold( body['deployment']['environment'] ),
                                                                        C.Bold( body['deployment_status']['state'] ) )

    def download (self, headers, body):
        V.prnt( 'GithubHooks.download', V.ERROR )
        return ''

    def follow (self, headers, body):
        V.prnt( 'GithubHooks.follow', V.ERROR )
        return ''

    def fork (self, headers, body):
        return '[%s] %s forked to %s.' % ( C.Pink( body['repository']['full_name'] ),
                                           C.Cyan( body['sender']['login'] ),
                                           C.Pink( body['forkee']['full_name'] ) )

    def fork_apply (self, headers, body):
        V.prnt( 'GithubHooks.fork_apply', V.ERROR )
        return ''

    def gist (self, headers, body):
        V.prnt( 'GithubHooks.gist', V.ERROR )
        return ''

    def gollum (self, headers, body):
        string = '[%s] %s updated the wiki. (%s)' % ( C.Pink( body['repository']['full_name'] ),
                                                      C.Cyan( body['sender']['login'] ),
                                                      C.Blue( body['repository']['html_url']+'/wiki', False ) ) # miniurl
        for page in body['pages']:
            string += '\n%s %s %s. (%s)' % ( C.Gray( page['sha'][:7] ), # Really 7 for pages sha ?
                                             page['action'],
                                             C.Bold( page['page_name'] ),
                                             C.Blue( page['html_url'], False ) )
        return string

    def issue_comment (self, headers, body):
        return '[%s] %s comment issue %s. (%s)' % ( C.Pink( body['repository']['full_name'] ),
                                                    C.Cyan( body['comment']['user']['login'] ),
                                                    C.Gray( '#'+body['issue']['number'] ),
                                                    C.Blue( body['issue']['url'], False ) ) # miniurl

    def issues (self, headers, body):
        string = '[%s] %s %s ' % ( C.Pink( body['repository']['full_name'] ),
                                   C.Cyan( body['sender']['login'] ),
                                   body['action'] )
        if body['action'] in ['assigned', 'unassigned']:
            string += '%s on ' % ( C.Cyan( body['assignee']['login'] ), )
        string += 'issue %s. (%s)' % ( C.Gray( '#'+body['issue']['number'] ),
                                       C.Blue( body['issue']['url'], False ) )
        return string

    def member (self, headers, body):
        return '[%s] %s added %s as collaborator.' % ( C.Pink( body['repository']['full_name'] ),
                                                       C.Cyan( body['sender']['login'] ),
                                                       C.Cyan( body['member']['octocat'] ) )

    def page_build (self, headers, body):
        V.prnt( 'GithubHooks.page_build', V.ERROR )
        return ''

    def public (self, headers, body):
        return '[%s] %s made this repository public.' % ( C.Pink( body['repository']['full_name'] ),
                                                          C.Cyan( body['sender']['login'] ) )

    def pull_request (self, headers, body):
        string = '[%s] %s %s ' % ( C.Pink( body['repository']['full_name'] ),
                                   C.Cyan( body['sender']['login'] ),
                                   body['action'] )
        if body['action'] in ['assigned', 'unassigned']:
            string += '%s on ' % ( C.Cyan( body['assignee']['login'] ), )
        string += 'pull request %s. (%s)' % ( C.Gray( '#'+body['pull_request']['number'] ),
                                              C.Blue( body['pull_request']['html_url'], False ) )

    def pull_request_review_comment (self, headers, body):
        return '[%s] %s commented pull request %s. (%s)' % ( C.Pink( body['repository']['full_name'] ),
                                                             C.Cyan( body['comment']['user']['login'] ),
                                                             C.Gray( '#'+body['pull_request']['number'] ),
                                                             C.Blue( body['comment']['html_url'], False ) )

    def push (self, headers, body):
        string = '[%s] %s pushed %s commits to %s. (%s)' % ( C.Pink( body['repository']['full_name'] ),
                                                             C.Cyan( body['pusher']['name'] ),
                                                             C.Bold( len(body['commits']) ),
                                                             C.Red( body['ref'].split('/')[-1] ),
                                                             C.Blue( body['compare'], False ) ) # miniurl
        for commit in body['commits']:
            string += '\n%s %s: %s' % ( C.Gray( commit['id'][:7] ),
                                        C.Cyan( commit['committer']['username'] ),
                                        commit['message'].split('\n')[0] )
        return string

    def release (self, headers, body):
        V.prnt( 'GithubHooks.release', V.ERROR )
        return ''


GithubHooks = GithubHooks ()

from __future__ import unicode_literals

from json import dumps
from base64 import b64encode
from ..decorators import requires_auth
from ..events import Event
from ..git import Blob, Commit, Reference, Tag, Tree
from ..issues import issue_params, Issue
from ..issues.event import IssueEvent
from ..issues.label import Label
from ..issues.milestone import Milestone
from ..models import GitHubCore
from ..notifications import Subscription, Thread
from ..pulls import PullRequest
from .branch import Branch
from .comment import RepoComment
from .commit import RepoCommit
from .comparison import Comparison
from .contents import Contents, validate_commmitter
from .deployment import Deployment
from .hook import Hook
from .issue_import import ImportedIssue
from ..licenses import License
from .pages import PagesBuild, PagesInfo
from .status import Status
from .stats import ContributorStats
from .release import Release, Asset
from .tag import RepoTag
from ..users import User, Key
from ..utils import stream_response_to_file, timestamp_parameter
from uritemplate import URITemplate


class Repository(GitHubCore):


    STAR_HEADERS = {
        'Accept': 'application/vnd.github.v3.star+json'
    }

    def _update_attributes(self, repo):
        self.clone_url = repo.get('clone_url', '')
        self.created_at = self._strptime(repo.get('created_at'))
        self.description = repo.get('description', '')

        self.forks_count = repo.get('forks_count')
        self.fork_count = self.forks_count

        self.fork = repo.get('fork')

        self.full_name = repo.get('full_name', '')

        self.git_url = repo.get('git_url', '')
        self.has_downloads = repo.get('has_downloads')
        self.has_issues = repo.get('has_issues')
        self.has_wiki = repo.get('has_wiki')

        self.homepage = repo.get('homepage', '')

        self.diff_url = repo.get('diff_url', '')

        self.patch_url = repo.get('patch_url', '')

        self.issue_url = repo.get('issue_url', '')

        self.html_url = repo.get('html_url', '')
        self.id = repo.get('id', 0)
        self.language = repo.get('language', '')
        self.mirror_url = repo.get('mirror_url', '')

        self.name = repo.get('name', '')

        self.open_issues = repo.get('open_issues', 0)

        self.open_issues_count = repo.get('open_issues_count')

        self.owner = User(repo.get('owner', {}), self)

        self.private = repo.get('private')

        self.permissions = repo.get('permissions')

        self.pushed_at = self._strptime(repo.get('pushed_at'))
        self.size = repo.get('size', 0)

        self.stargazers_count = repo.get('stargazers_count', 0)

        self.starred_at = self._strptime(repo.get('starred_at'))

        self.ssh_url = repo.get('ssh_url', '')
        self.svn_url = repo.get('svn_url', '')
        self.updated_at = self._strptime(repo.get('updated_at'))
        self._api = repo.get('url', '')

        self.watchers = repo.get('watchers', 0)

        self.source = repo.get('source')
        if self.source:
            self.source = Repository(self.source, self)

        self.parent = repo.get('parent')
        if self.parent:
            self.parent = Repository(self.parent, self)

        self.default_branch = repo.get('default_branch', '')

        self.master_branch = repo.get('master_branch', '')

        self.teams_url = repo.get('teams_url', '')

        self.hooks_url = repo.get('hooks_url', '')

        self.events_url = repo.get('events_url', '')

        self.tags_url = repo.get('tags_url', '')

        self.languages_url = repo.get('languages_url', '')

        self.stargazers_url = repo.get('stargazers_url', '')

        self.contributors_url = repo.get('contributors_url', '')

        self.subscribers_url = repo.get('subscribers_url', '')

        self.subscription_url = repo.get('subscription_url', '')

        self.merges_url = repo.get('merges_url', '')

        self.download_url = repo.get('downloads_url', '')

        ie_url_t = repo.get('issue_events_url')
        self.issue_events_urlt = URITemplate(ie_url_t) if ie_url_t else None

        assignees = repo.get('assignees_url')
        self.assignees_urlt = URITemplate(assignees) if assignees else None

        branches = repo.get('branches_url')
        self.branches_urlt = URITemplate(branches) if branches else None

        blobs = repo.get('blobs_url')
        self.blobs_urlt = URITemplate(blobs) if blobs else None

        git_tags = repo.get('git_tags_url')
        self.git_tags_urlt = URITemplate(git_tags) if git_tags else None

        git_refs = repo.get('git_refs_url')
        self.git_refs_urlt = URITemplate(git_refs) if git_refs else None

        trees = repo.get('trees_url')
        self.trees_urlt = URITemplate(trees) if trees else None

        statuses = repo.get('statuses_url')
        self.statuses_urlt = URITemplate(statuses) if statuses else None

        commits = repo.get('commits_url')
        self.commits_urlt = URITemplate(commits) if commits else None

        commits = repo.get('git_commits_url')
        self.git_commits_urlt = URITemplate(commits) if commits else None

        comments = repo.get('comments_url')
        self.comments_urlt = URITemplate(comments) if comments else None

        comments = repo.get('review_comments_url')
        self.review_comments_url = URITemplate(comments) if comments else None

        comments = repo.get('review_comment_url')
        self.review_comment_urlt = URITemplate(comments) if comments else None

        comments = repo.get('issue_comment_url')
        self.issue_comment_urlt = URITemplate(comments) if comments else None

        contents = repo.get('contents_url')
        self.contents_urlt = URITemplate(contents) if contents else None

        compare = repo.get('compare_url')
        self.compare_urlt = URITemplate(compare) if compare else None

        archive = repo.get('archive_url')
        self.archive_urlt = URITemplate(archive) if archive else None

        issues = repo.get('issues_url')
        self.issues_urlt = URITemplate(issues) if issues else None

        pulls = repo.get('pulls_url')
        self.pulls_urlt = URITemplate(pulls) if issues else None

        miles = repo.get('milestones_url')
        self.milestones_urlt = URITemplate(miles) if miles else None

        notif = repo.get('notifications_url')
        self.notifications_urlt = URITemplate(notif) if notif else None

        labels = repo.get('labels_url')
        self.labels_urlt = URITemplate(labels) if labels else None

    def _repr(self):
        return '<Repository [{0}]>'.format(self)

    def __str__(self):
        return self.full_name

    def _create_pull(self, data):
        self._remove_none(data)
        json = None
        if data:
            url = self._build_url('pulls', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(PullRequest, json)

    @requires_auth
    def add_collaborator(self, username):
        if not username:
            return False
        url = self._build_url('collaborators', str(username),
                              base_url=self._api)
        return self._boolean(self._put(url), 204, 404)

    def archive(self, format, path='', ref='master'):
        resp = None
        if format in ('tarball', 'zipball'):
            url = self._build_url(format, ref, base_url=self._api)
            resp = self._get(url, allow_redirects=True, stream=True)

        if resp and self._boolean(resp, 200, 404):
            stream_response_to_file(resp, path)
            return True
        return False

    def asset(self, id):
        data = None
        if int(id) > 0:
            url = self._build_url('releases', 'assets', str(id),
                                  base_url=self._api)
            data = self._json(self._get(url, headers=Release.CUSTOM_HEADERS),
                              200)
        return self._instance_or_null(Asset, data)

    def assignees(self, number=-1, etag=None):
        url = self._build_url('assignees', base_url=self._api)
        return self._iter(int(number), url, User, etag=etag)

    def blob(self, sha):
        url = self._build_url('git', 'blobs', sha, base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(Blob, json)

    def branch(self, name):
        json = None
        if name:
            url = self._build_url('branches', name, base_url=self._api)
            json = self._json(self._get(url, headers=Branch.PREVIEW_HEADERS),
                              200)
        return self._instance_or_null(Branch, json)

    def branches(self, number=-1, protected=False, etag=None):
        url = self._build_url('branches', base_url=self._api)
        params = {'protected': '1'} if protected else None
        return self._iter(int(number), url, Branch, params, etag=etag,
                          headers=Branch.PREVIEW_HEADERS)

    def code_frequency(self, number=-1, etag=None):
        url = self._build_url('stats', 'code_frequency', base_url=self._api)
        return self._iter(int(number), url, list, etag=etag)

    def collaborators(self, number=-1, etag=None):
        url = self._build_url('collaborators', base_url=self._api)
        return self._iter(int(number), url, User, etag=etag)

    def comments(self, number=-1, etag=None):
        url = self._build_url('comments', base_url=self._api)
        return self._iter(int(number), url, RepoComment, etag=etag)

    def commit(self, sha):
        url = self._build_url('commits', sha, base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(RepoCommit, json)

    def commit_activity(self, number=-1, etag=None):
        url = self._build_url('stats', 'commit_activity', base_url=self._api)
        return self._iter(int(number), url, dict, etag=etag)

    def commit_comment(self, comment_id):
        url = self._build_url('comments', str(comment_id), base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(RepoComment, json)

    def commits(self, sha=None, path=None, author=None, number=-1, etag=None,
                since=None, until=None):
        params = {'sha': sha, 'path': path, 'author': author,
                  'since': timestamp_parameter(since),
                  'until': timestamp_parameter(until)}

        self._remove_none(params)
        url = self._build_url('commits', base_url=self._api)
        return self._iter(int(number), url, RepoCommit, params, etag)

    def compare_commits(self, base, head):
        url = self._build_url('compare', base + '...' + head,
                              base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(Comparison, json)

    def contributor_statistics(self, number=-1, etag=None):
        url = self._build_url('stats', 'contributors', base_url=self._api)
        return self._iter(int(number), url, ContributorStats, etag=etag)

    def contributors(self, anon=False, number=-1, etag=None):
        url = self._build_url('contributors', base_url=self._api)
        params = {}
        if anon:
            params = {'anon': 'true'}
        return self._iter(int(number), url, User, params, etag)

    @requires_auth
    def create_blob(self, content, encoding):
        sha = ''
        if encoding in ('base64', 'utf-8'):
            url = self._build_url('git', 'blobs', base_url=self._api)
            data = {'content': content, 'encoding': encoding}
            json = self._json(self._post(url, data=data), 201)
            if json:
                sha = json.get('sha')
        return sha

    @requires_auth
    def create_comment(self, body, sha, path=None, position=None, line=1):
        json = None
        if body and sha and (line and int(line) > 0):
            data = {'body': body, 'line': line, 'path': path,
                    'position': position}
            self._remove_none(data)
            url = self._build_url('commits', sha, 'comments',
                                  base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(RepoComment, json)

    @requires_auth
    def create_commit(self, message, tree, parents, author=None,
                      committer=None):
        json = None
        if message and tree and isinstance(parents, list):
            url = self._build_url('git', 'commits', base_url=self._api)
            data = {'message': message, 'tree': tree, 'parents': parents,
                    'author': author, 'committer': committer}
            self._remove_none(data)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(Commit, json)

    @requires_auth
    def create_deployment(self, ref, force=False, payload='',
                          auto_merge=False, description='', environment=None):
        json = None
        if ref:
            url = self._build_url('deployments', base_url=self._api)
            data = {'ref': ref, 'force': force, 'payload': payload,
                    'auto_merge': auto_merge, 'description': description,
                    'environment': environment}
            self._remove_none(data)
            json = self._json(self._post(url, data=data),
                              201)
        return self._instance_or_null(Deployment, json)

    @requires_auth
    def create_file(self, path, message, content, branch=None,
                    committer=None, author=None):
        if content and not isinstance(content, bytes):
            raise ValueError(  # (No coverage)
                'content must be a bytes object')  # (No coverage)

        json = None
        if path and message and content:
            url = self._build_url('contents', path, base_url=self._api)
            content = b64encode(content).decode('utf-8')
            data = {'message': message, 'content': content, 'branch': branch,
                    'committer': validate_commmitter(committer),
                    'author': validate_commmitter(author)}
            self._remove_none(data)
            json = self._json(self._put(url, data=dumps(data)), 201)
            if json and 'content' in json and 'commit' in json:
                json['content'] = Contents(json['content'], self)
                json['commit'] = Commit(json['commit'], self)
        return json

    @requires_auth
    def create_fork(self, organization=None):
        url = self._build_url('forks', base_url=self._api)
        if organization:
            resp = self._post(url, data={'organization': organization})
        else:
            resp = self._post(url)

        json = self._json(resp, 202)
        return self._instance_or_null(Repository, json)

    @requires_auth
    def create_hook(self, name, config, events=['push'], active=True):
        json = None
        if name and config and isinstance(config, dict):
            url = self._build_url('hooks', base_url=self._api)
            data = {'name': name, 'config': config, 'events': events,
                    'active': active}
            json = self._json(self._post(url, data=data), 201)
        return Hook(json, self) if json else None

    @requires_auth
    def create_issue(self,
                     title,
                     body=None,
                     assignee=None,
                     milestone=None,
                     labels=None):
        issue = {'title': title, 'body': body, 'assignee': assignee,
                 'milestone': milestone, 'labels': labels}
        self._remove_none(issue)
        json = None

        if issue:
            url = self._build_url('issues', base_url=self._api)
            json = self._json(self._post(url, data=issue), 201)

        return self._instance_or_null(Issue, json)

    @requires_auth
    def create_key(self, title, key, read_only=False):
        json = None
        if title and key:
            data = {'title': title, 'key': key, 'read_only': read_only}
            url = self._build_url('keys', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(Key, json)

    @requires_auth
    def create_label(self, name, color):
        json = None
        if name and color:
            data = {'name': name, 'color': color.strip('#')}
            url = self._build_url('labels', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(Label, json)

    @requires_auth
    def create_milestone(self, title, state=None, description=None,
                         due_on=None):
        url = self._build_url('milestones', base_url=self._api)
        if state not in ('open', 'closed'):
            state = None
        data = {'title': title, 'state': state,
                'description': description, 'due_on': due_on}
        self._remove_none(data)
        json = None
        if data:
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(Milestone, json)

    @requires_auth
    def create_pull(self, title, base, head, body=None):
        data = {'title': title, 'body': body, 'base': base,
                'head': head}
        return self._create_pull(data)

    @requires_auth
    def create_pull_from_issue(self, issue, base, head):
        if int(issue) > 0:
            data = {'issue': issue, 'base': base, 'head': head}
            return self._create_pull(data)
        return None

    @requires_auth
    def create_ref(self, ref, sha):
        json = None
        if ref and ref.startswith('refs') and ref.count('/') >= 2 and sha:
            data = {'ref': ref, 'sha': sha}
            url = self._build_url('git', 'refs', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(Reference, json)

    @requires_auth
    def create_release(self, tag_name, target_commitish=None, name=None,
                       body=None, draft=False, prerelease=False):
        data = {'tag_name': str(tag_name),
                'target_commitish': target_commitish,
                'name': name,
                'body': body,
                'draft': draft,
                'prerelease': prerelease
                }
        self._remove_none(data)

        url = self._build_url('releases', base_url=self._api)
        json = self._json(self._post(
            url, data=data, headers=Release.CUSTOM_HEADERS
            ), 201)
        return self._instance_or_null(Release, json)

    @requires_auth
    def create_status(self, sha, state, target_url=None, description=None,
                      context='default'):
        json = None
        if sha and state:
            data = {'state': state, 'target_url': target_url,
                    'description': description, 'context': context}
            url = self._build_url('statuses', sha, base_url=self._api)
            self._remove_none(data)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(Status, json)

    @requires_auth
    def create_tag(self, tag, message, sha, obj_type, tagger,
                   lightweight=False):
        if lightweight and tag and sha:
            return self.create_ref('refs/tags/' + tag, sha)

        json = None
        if tag and message and sha and obj_type and len(tagger) == 3:
            data = {'tag': tag, 'message': message, 'object': sha,
                    'type': obj_type, 'tagger': tagger}
            url = self._build_url('git', 'tags', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
            if json:
                self.create_ref('refs/tags/' + tag, json.get('sha'))
        return self._instance_or_null(Tag, json)

    @requires_auth
    def create_tree(self, tree, base_tree=None):
        json = None
        if tree and isinstance(tree, list):
            data = {'tree': tree}
            if base_tree:
                data['base_tree'] = base_tree
            url = self._build_url('git', 'trees', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(Tree, json)

    @requires_auth
    def delete(self):
        return self._boolean(self._delete(self._api), 204, 404)

    @requires_auth
    def delete_key(self, key_id):
        if int(key_id) <= 0:
            return False
        url = self._build_url('keys', str(key_id), base_url=self._api)
        return self._boolean(self._delete(url), 204, 404)

    @requires_auth
    def delete_subscription(self):
        url = self._build_url('subscription', base_url=self._api)
        return self._boolean(self._delete(url), 204, 404)

    def deployment(self, id):
        json = None
        if int(id) > 0:
            url = self._build_url('deployments', str(id), base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Deployment, json)

    def deployments(self, number=-1, etag=None):
        url = self._build_url('deployments', base_url=self._api)
        i = self._iter(int(number), url, Deployment, etag=etag)
        return i

    def directory_contents(self, directory_path, ref=None, return_as=list):
        url = self._build_url('contents', directory_path, base_url=self._api)
        json = self._json(self._get(url, params={'ref': ref}), 200) or []
        return return_as((j.get('name'), Contents(j, self)) for j in json)

    @requires_auth
    def edit(self, name, description=None, homepage=None, private=None,
             has_issues=None, has_wiki=None, has_downloads=None,
             default_branch=None):
        edit = {'name': name, 'description': description, 'homepage': homepage,
                'private': private, 'has_issues': has_issues,
                'has_wiki': has_wiki, 'has_downloads': has_downloads,
                'default_branch': default_branch}
        self._remove_none(edit)
        json = None
        if edit:
            json = self._json(self._patch(self._api, data=dumps(edit)), 200)
            self._update_attributes(json)
            return True
        return False

    def events(self, number=-1, etag=None):
        url = self._build_url('events', base_url=self._api)
        return self._iter(int(number), url, Event, etag=etag)

    def file_contents(self, path, ref=None):
        url = self._build_url('contents', path, base_url=self._api)
        json = self._json(self._get(url, params={'ref': ref}), 200)
        return self._instance_or_null(Contents, json)

    def forks(self, sort='', number=-1, etag=None):
        url = self._build_url('forks', base_url=self._api)
        params = {}
        if sort in ('newest', 'oldest', 'watchers'):
            params = {'sort': sort}
        return self._iter(int(number), url, Repository, params, etag)

    def git_commit(self, sha):
        json = {}
        if sha:
            url = self._build_url('git', 'commits', sha, base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Commit, json)

    @requires_auth
    def hook(self, hook_id):
        json = None
        if int(hook_id) > 0:
            url = self._build_url('hooks', str(hook_id), base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Hook, json)

    @requires_auth
    def hooks(self, number=-1, etag=None):
        url = self._build_url('hooks', base_url=self._api)
        return self._iter(int(number), url, Hook, etag=etag)

    @requires_auth
    def ignore(self):
        url = self._build_url('subscription', base_url=self._api)
        json = self._json(self._put(url, data=dumps({'ignored': True})), 200)
        return self._instance_or_null(Subscription, json)

    @requires_auth
    def imported_issue(self, imported_issue_id):
        url = self._build_url('import/issues', imported_issue_id,
                              base_url=self._api)
        data = self._get(url, headers=ImportedIssue.IMPORT_CUSTOM_HEADERS)
        json = self._json(data, 200)
        return self._instance_or_null(ImportedIssue, json)

    @requires_auth
    def imported_issues(self, number=-1, since=None, etag=None):

        data = {
            'since': timestamp_parameter(since)
        }

        self._remove_none(data)
        url = self._build_url('import/issues', base_url=self._api)

        return self._iter(int(number), url, ImportedIssue, etag=etag,
                          params=data,
                          headers=ImportedIssue.IMPORT_CUSTOM_HEADERS)

    @requires_auth
    def import_issue(self, title, body, created_at, assignee=None,
                     milestone=None, closed=None, labels=None, comments=None):

        issue = {
            'issue': {
                'title': title,
                'body': body,
                'created_at': created_at,
                'assignee': assignee,
                'milestone': milestone,
                'closed': closed,
                'labels': labels,
            },
            'comments': comments
        }

        self._remove_none(issue)
        self._remove_none(issue['issue'])
        url = self._build_url('import/issues', base_url=self._api)

        data = self._post(url, data=issue,
                          headers=ImportedIssue.IMPORT_CUSTOM_HEADERS)

        json = self._json(data, 200)
        return self._instance_or_null(ImportedIssue, json)

    def is_assignee(self, username):
        if not username:
            return False
        url = self._build_url('assignees', str(username), base_url=self._api)
        return self._boolean(self._get(url), 204, 404)

    @requires_auth
    def is_collaborator(self, username):
        if not username:
            return False
        url = self._build_url('collaborators', str(username),
                              base_url=self._api)
        return self._boolean(self._get(url), 204, 404)

    def issue(self, number):
        json = None
        if int(number) > 0:
            url = self._build_url('issues', str(number), base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Issue, json)

    def issue_events(self, number=-1, etag=None):
        url = self._build_url('issues', 'events', base_url=self._api)
        return self._iter(int(number), url, IssueEvent, etag=etag)

    def issues(self, milestone=None, state=None, assignee=None, mentioned=None,
               labels=None, sort=None, direction=None, since=None, number=-1,
               etag=None):
        url = self._build_url('issues', base_url=self._api)

        params = repo_issue_params(milestone, state, assignee, mentioned,
                                   labels, sort, direction, since)

        return self._iter(int(number), url, Issue, params, etag)

    @requires_auth
    def key(self, id_num):
        json = None
        if int(id_num) > 0:
            url = self._build_url('keys', str(id_num), base_url=self._api)
            json = self._json(self._get(url), 200)
        return Key(json, self) if json else None

    @requires_auth
    def keys(self, number=-1, etag=None):
        url = self._build_url('keys', base_url=self._api)
        return self._iter(int(number), url, Key, etag=etag)

    def label(self, name):
        json = None
        if name:
            url = self._build_url('labels', name, base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Label, json)

    def labels(self, number=-1, etag=None):
        url = self._build_url('labels', base_url=self._api)
        return self._iter(int(number), url, Label, etag=etag)

    def languages(self, number=-1, etag=None):
        url = self._build_url('languages', base_url=self._api)
        return self._iter(int(number), url, tuple, etag=etag)

    @requires_auth
    def latest_pages_build(self):
        url = self._build_url('pages', 'builds', 'latest', base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(PagesBuild, json)

    def latest_release(self):
        url = self._build_url('releases', 'latest', base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(Release, json)

    def license(self):
        url = self._build_url('license', base_url=self._api)
        json = self._json(self._get(url, headers=License.CUSTOM_HEADERS), 200)
        return self._instance_or_null(License, json)

    @requires_auth
    def mark_notifications(self, last_read=''):
        url = self._build_url('notifications', base_url=self._api)
        mark = {'read': True}
        if last_read:
            mark['last_read_at'] = last_read
        return self._boolean(self._put(url, data=dumps(mark)),
                             205, 404)

    @requires_auth
    def merge(self, base, head, message=''):
        url = self._build_url('merges', base_url=self._api)
        data = {'base': base, 'head': head}
        if message:
            data['commit_message'] = message
        json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(RepoCommit, json)

    def milestone(self, number):
        json = None
        if int(number) > 0:
            url = self._build_url('milestones', str(number),
                                  base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Milestone, json)

    def milestones(self, state=None, sort=None, direction=None, number=-1,
                   etag=None):
        url = self._build_url('milestones', base_url=self._api)
        accepted = {'state': ('open', 'closed'),
                    'sort': ('due_date', 'completeness'),
                    'direction': ('asc', 'desc')}
        params = {'state': state, 'sort': sort, 'direction': direction}
        for (k, v) in list(params.items()):
            if not (v and (v in accepted[k])):  # e.g., '' or None
                del params[k]
        if not params:
            params = None
        return self._iter(int(number), url, Milestone, params, etag)

    def network_events(self, number=-1, etag=None):
        base = self._api.replace('repos', 'networks', 1)
        url = self._build_url('events', base_url=base)
        return self._iter(int(number), url, Event, etag)

    @requires_auth
    def notifications(self, all=False, participating=False, since=None,
                      number=-1, etag=None):
        url = self._build_url('notifications', base_url=self._api)
        params = {
            'all': str(all).lower(),
            'participating': str(participating).lower(),
            'since': timestamp_parameter(since)
        }
        self._remove_none(params)
        return self._iter(int(number), url, Thread, params, etag)

    @requires_auth
    def pages(self):
        url = self._build_url('pages', base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(PagesInfo, json)

    @requires_auth
    def pages_builds(self, number=-1, etag=None):
        url = self._build_url('pages', 'builds', base_url=self._api)
        return self._iter(int(number), url, PagesBuild, etag=etag)

    def pull_request(self, number):
        json = None
        if int(number) > 0:
            url = self._build_url('pulls', str(number), base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(PullRequest, json)

    def pull_requests(self, state=None, head=None, base=None, sort='created',
                      direction='desc', number=-1, etag=None):
        url = self._build_url('pulls', base_url=self._api)
        params = {}

        if state:
            state = state.lower()
            if state in ('all', 'open', 'closed'):
                params['state'] = state

        params.update(head=head, base=base, sort=sort, direction=direction)
        self._remove_none(params)
        return self._iter(int(number), url, PullRequest, params, etag)

    def readme(self):
        url = self._build_url('readme', base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(Contents, json)

    def ref(self, ref):
        json = None
        if ref:
            url = self._build_url('git', 'refs', ref, base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Reference, json)

    def refs(self, subspace='', number=-1, etag=None):
        if subspace:
            args = ('git', 'refs', subspace)
        else:
            args = ('git', 'refs')
        url = self._build_url(*args, base_url=self._api)
        return self._iter(int(number), url, Reference, etag=etag)

    def release(self, id):
        json = None
        if int(id) > 0:
            url = self._build_url('releases', str(id), base_url=self._api)
            json = self._json(self._get(url), 200)
        return self._instance_or_null(Release, json)

    def release_from_tag(self, tag_name):
        url = self._build_url('releases', 'tags', tag_name,
                              base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(Release, json)

    def releases(self, number=-1, etag=None):
        url = self._build_url('releases', base_url=self._api)
        iterator = self._iter(int(number), url, Release, etag=etag)
        reveal_type(iterator.headers)
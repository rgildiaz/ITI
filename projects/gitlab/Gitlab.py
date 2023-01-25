import gitlab
import secrets

# store the secrets dictionary
# personal access token is required
s = secrets.secrets

class Gitlab:
    '''
    The GitLab API.
    '''
    def __init__(self, config):
        # config file as formatted in ./config.py
        self.config = config
        # the python-gitlab API object
        self.gl = None
        self.groups = None

        # sets gl object and fetches groups
        self.setup()

    def setup(self):
        '''
        Finish initialization of the Gitlab object. 
        '''
        # convenience, switch between personal and ITI gitlab
        if "code.iti.illinois.edu" in self.config.url:
            self.gl = gitlab.Gitlab(self.config.url, private_token=s['gl-pat-le'])
        else:
            self.gl = gitlab.Gitlab(private_token=s['gl-pat-personal'])
        
        self.groups = self.read_groups(self.config.group_ids)

    def get_gl(self):
        '''
        Return the python-gitlab API object.
        '''
        return self.gl

    def get_config(self):
        return self.config

    def get_groups(self):
        return self.groups

    def read_groups(self, group_ids: list) -> list:
        groups = []
        for id in group_ids:
            group = self.gl.groups.get(id)

            members = []
            for member in group.members.list():
                members.append({
                    'username': member.username,
                    'user_id': member.id,
                })

            groups.append({
                'group_name': group.name,
                'group_id': group.id,
                'members': members,
            })

        return groups
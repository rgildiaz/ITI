from gl.Gitlab import Gitlab
import config
import secrets

def main():
    '''
    Mediator script. 
    1. Fetch data about AD groups from ad.<name>. 
    2. Compare to existing GitLab groups with gl.Gitlab. 
    3. Add and remove GitLab groups to match AD groups.

    config data is stored in ./config.py
    PAT's are stored in ./secrets.py
    '''
    # Fetch data about AD groups
    ...

    # Fetch Gitlab data
    gl = Gitlab(secrets.pat_personal, config.url_pub)
    print("Groups found in GitLab: ", gl.get_groups()[0]['object'].members.list())

    # Compare and update gitlab
    ...

if __name__ == "__main__":
    main()
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
    parent_id = gl.get_groups()[0]['group_id']
    print("parent id:", parent_id)

    # remove all non-root groups
    for group in gl.get_groups():
        group = group['object']
        if group.parent_id is not None:
            print(group)
            group.delete()

    # make a group
    group = gl.create_group("group1", "group1", parent_id)
    print(group.id)

    # delete it.
    group.delete()

    gl.create_group("group1", "group1", parent_id)

    # Compare and update gitlab
    ...

if __name__ == "__main__":
    main()
    # gl = Gitlab(secrets.pat_personal, config.url_pub)  
    # print(gl.get_groups())
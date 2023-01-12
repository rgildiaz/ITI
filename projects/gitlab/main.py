import gitlab
import secrets
import config

s = secrets.secrets

# url and access token are in secrets.py
# gl = gitlab.Gitlab(url=s['gl-url'], private_token=s['gl-pat-le'])
gl = gitlab.Gitlab(private_token=s['gl-pat-personal'])


def main():
    all_groups = read_groups(config.group_ids)
    print(all_groups)
    

def read_groups(group_ids: list) -> list:
    groups = []
    for id in group_ids:
        group = gl.groups.get(id)

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


if __name__ == "__main__":
    main()
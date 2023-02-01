from Gitlab import Gitlab
import config
import secrets

# store the secrets dictionary
# personal access token is required
s = secrets.secrets

def main():
    gl = Gitlab(s['gl-pat-personal'], config.url)
    print(gl)
    print(gl.groups)


if __name__ == "__main__":
    main()
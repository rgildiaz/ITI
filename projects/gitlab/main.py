from Gitlab import Gitlab
import config
import secrets

def main():
    gl = Gitlab(secrets.pat_personal, config.url)
    print(gl)
    print(gl.groups)


if __name__ == "__main__":
    main()
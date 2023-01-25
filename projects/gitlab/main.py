from Gitlab import Gitlab
import config

def main():
    gl = Gitlab(config)
    print(gl.get_groups())
    print(gl)


if __name__ == "__main__":
    main()
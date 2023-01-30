from Gitlab import Gitlab
import config

def main():
    gl = Gitlab(config)
    print(gl.get_config())
    print(gl)


if __name__ == "__main__":
    main()
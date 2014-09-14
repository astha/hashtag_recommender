import subprocess
import sys

def main(argv):
	subprocess.Popen("cat " + argv[0] + " | sed 's/^ [^ ]* //' > group_tweets", shell=True)
	subprocess.Popen("cut -d' ' -f2 " + argv[0] + " | sed 's/^/#/g' > group_tags", shell=True)

if __name__ == "__main__":
    main(sys.argv[1:])
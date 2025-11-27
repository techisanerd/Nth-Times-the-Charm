from pathlib import Path
from pydriller import Repository

for commit in Repository("https://github.com/techisanerd/Nth-Times-the-Charm.git").traverse_commits():
    for file in commit.modified_files:
        print('Author {} modified {} in commit {}'.format(commit.author.name, file.filename, commit.hash))

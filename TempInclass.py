repo = Path(__file__).resolve().parent
for commit in Repository('repo').traverse_commits():
    for file in commit.modified_files:
        print('Author {} modified {} in commit {}'.format(commit.author.name, file.filename, commit.hash))

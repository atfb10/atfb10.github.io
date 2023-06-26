'''
Adam Forestier
June 26, 2023
Automatically Create Blog Posts & post to my github.io page
'''

# D:\coding\udemy\openai_blog_app


# Imports
import openai

from git import Repo
from pathlib import Path

# Local
from key import git_path
from key import key as openai_key

# Set api key
openai.api_key = openai_key

# File paths
PATH_TO_REPO = Path(git_path)
PATH_TO_BLOG = PATH_TO_REPO.parent
PATH_TO_CONTENT = PATH_TO_BLOG/"content"
PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

# Automate and push changes to blog

def update(commit_msg='Updates Blog') -> None:
    '''
    arguments: commit message for git
    returns: None
    description: update pushes updates to the github repository
    '''
    repo = Repo(PATH_TO_REPO)
    repo.git.add(all=True)
    repo.index.commit(commit_msg)
    origin = repo.remote(name='origin')
    origin.push()

rand_txt = 'akjdfslkajs;dfajs'
with open(PATH_TO_BLOG/"index.html", 'w') as f:
    f.write(rand_txt)

update()
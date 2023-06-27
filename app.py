'''
Adam Forestier
June 26, 2023
Automatically Create Blog Posts & post to my github.io page
'''

# D:\coding\udemy\openai_blog_app


# Imports
import openai
import os
import requests
import shutil as sh

from bs4 import BeautifulSoup as Soup
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

def update_blog(commit_msg='Updates Blog') -> None:
    '''
    arguments: commit message for git
    returns: None
    description: update pushes updates to the github repository
    '''
    repo = Repo(PATH_TO_REPO)
    repo.git.add(all=True)
    repo.index.commit(commit_msg)
    origin = repo.remote(name='origin')
    origin.push(refspec='main:main')
    return

def create_new_blog(title: str, content: str, cover_image: str) -> str:
    '''
    arguments: blog title, its text and image
    returns: file path to the new content
    description: create_new_blog creates a new blog post utilizing content and an image created by the API
    '''
    cover_image = Path(cover_image)
    files = len(list(PATH_TO_CONTENT.glob("*.html")))
    new_title = f"{files + 1}.html"
    path_to_new_content = PATH_TO_CONTENT/new_title
    sh.copy(cover_image, PATH_TO_CONTENT)

    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content, "w") as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n")
            f.write("<head>\n")
            f.write(f"<title> {title} </title>")
            f.write("</head>\n")

            f.write("<body>\n")
            f.write(f"<img srg='{cover_image.name}' alt='Cover Image'> <br />\n")
            f.write(f"<h1> {title} </h1>")
            f.write(content.replace("\n", "<br />\n"))
            f.write("</body>\n")
            f.write("</html>\n")
            return path_to_new_content
    else:
        raise FileExistsError("File Already Exists - Aborting")
    
def check_dup_links(path_to_new_content: str, links: list) -> str:
    '''
    arguments: filepath to content, links to files
    returns: the path to content
    description: check_dup_links ensures that there are not duplicate links
    '''
    urls = [str(link.get("href")) for link in links]
    content_path = str(Path(*path_to_new_content.parts[-2:]))
    return content_path in urls

def write_to_index(path_to_new_content: str) -> None:
    '''
    arguments: path to the new blog content
    returns: None
    description: write_to_index adds link to index page for each new blog post
    '''
    with open(PATH_TO_BLOG/'index.html') as index:
        soup = Soup(index.read())
    links = soup.find_all('a')
    last_link = links[-1]
    
    if check_dup_links(path_to_new_content=path_to_new_content, links=links):
        raise ValueError("Link already exists!")
    
    link_to_new_blog = soup.new_tag("a", href=Path(*path_to_new_content.parts[-2:]))
    link_to_new_blog.string = path_to_new_content.name.split('.')[0]
    last_link.insert_after(link_to_new_blog)

    with open(PATH_TO_BLOG/'index.html', 'w') as f:
        f.write(str(soup.prettify(formatter='html')))

    return

def create_prompt(title: str) -> str:
    '''
    arguments: name of blog
    returns: prompt to API 
    description: prompt to feed to OpenAi API
    '''
    prompt = """
    Biography: My name is Adam. I am passionate about rock climbing and ski mountaineering. During my down time I like to watch Premier League Soccer. My favorite places in the world are Yosemite National Park, the Sierra Nevada Mountains, the Skykomish Valley, North Cascades National Park, Siurana, Margalef, and the New River Gorge. For work, I am a software developer, who mainly writes in the Python Language. I worked primarily as a full-stack developer, but as of late have focused primarily on machine learning. I have also spent time working as a National Park Ranger in Yosemite National Park, and working on mountaineering trips in the Sierra Nevada Mountains. I am a first generation college student. I was born and raised on a farm in Central Illinois.

    Blog
    Title: {}
    tags: work-life balance, personal exploration, following your dreams
    Summary: I talk about what it is like to go out of your comfort zone, try new things, do your absolute best, and dream big
    Full Text: """.format(title)
    return prompt

def img_prompt(title: str) -> str:
    '''
    arguments: title of art
    returns: prompt
    description: create prompt for image creation using openai api
    '''
    prompt = f"A photorealistic image showing {title}" 
    return prompt

def save_img(image_url: str, file_name: str) -> int:
    '''
    arguments: image url, name of file
    returns: status code
    description: save_img saves the image
    ''' 
    image_res = requests.get(image_url, stream=True)

    if image_res.status_code == 200:
        with open(file_name, 'wb') as f:
            sh.copyfileobj(image_res.raw, f)
    else:
        print('Error Downloading Image')
    
    return image_res.status_code

# Create the blog post
title = "Doing Hard Things"
response = openai.Completion.create(
    model='text-davinci-003',
    prompt=create_prompt(title),
    max_tokens=1000,
    temperature=.75
)
blog_content = response['choices'][0]['text']
img_response = openai.Image.create(prompt=img_prompt('Alpine Rock Climbing'), n =1, size="1024x1024")
img_url = img_response['data'][0]['url']
save_img(image_url=img_url, file_name='title.png')

path_to_new_content = create_new_blog(title=title, content=blog_content, cover_image='title.png')
write_to_index(path_to_new_content=path_to_new_content)
update_blog()
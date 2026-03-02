from bs4 import BeautifulSoup as bs, element

file = open("log.html", "r", encoding="utf-8")
soup = bs(file, "html.parser")
file.close()

def replace_tag(content, tag):
    content = str(content)
    in_tag = 0
    tag_open = 0
    content_splitted = []
    for i, char in enumerate(content):
        if i == len(content)-1:
            content_splitted.append(content[in_tag:])
        if char == '<':
            tag_open = i
            if in_tag != i:
                content_splitted.append(content[in_tag:i])
        elif char == '>':
            content_splitted.append(content[tag_open:i+1])
            in_tag = i+1
    return content_splitted
            

for msg_group in soup.find_all("div", {"class": "chatlog__message-group"}):
    avatar = msg_group.find("img", class_="chatlog__avatar")["src"]
    name = msg_group.find("span", class_="chatlog__author").text
    print(name, avatar)
    for msg in msg_group.find_all("div", class_="chatlog__message-primary"): 
        md = msg.find("span", class_="chatlog__markdown-preserve")
        msg_text = ""
        if (md):
            for i in md.contents:
                if type(i) == element.Tag:
                    msg_text += str(replace_tag(i, "br"))
                else:
                    msg_text += i.text
        elif msg.find("div", class_="chatlog__attachment"):
            msg_text += msg.find("img", class_="chatlog__attachment-media")["src"]
        else:
            pass

        print(msg_text)

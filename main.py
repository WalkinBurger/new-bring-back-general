from bs4 import BeautifulSoup as bs, element
import fileinput
import time
import datetime
import json

start = time.time()

def msg_format(i):
    # print(f"--{i}")
    temp_nested_msg = ""
    msg_text = ""
    if type(i) == element.Tag:
        for j in i.children:
            if type(j) == element.Tag:
                temp_nested_msg = msg_format(j)
        msg_attrs = i.attrs
        if msg_attrs.get("class"):
            if "chatlog__emoji" in msg_attrs["class"]:
                if i["src"][12] == 'd':
                    msg_text += f"<:{i["title"]}:{i["src"].split('.')[2][11:]}>"
                else: 
                    msg_text += f":{i["title"]}:"
            elif "chatlog__markdown-mention" in msg_attrs["class"]:
                msg_text += f"i.text "
            elif "chatlog__markdown-spoiler" in msg_attrs["class"]:
                msg_text += f"||{i.text}||"
            elif i.name == "code":
                msg_text += f"```{i.text if temp_nested_msg == "" else temp_nested_msg}```"
            elif "chatlog__markdown-timestamp" in msg_attrs["class"]:
                try:
                    msg_text += f"<t:{int(time.mktime(datetime.datetime.strptime(i.text, "%d-%b-%y %I:%M %p").timetuple()))}"
                except:
                    msg_text += "`Invalid date`"
            elif "chatlog__markdown-quote" in msg_attrs["class"]:
                msg_text += f"> {i.text if temp_nested_msg == "" else temp_nested_msg}"
        elif msg_attrs.get("href"):
            msg_text += str(msg_attrs["href"])
        elif i.name == "strong":
            msg_text += f"**{i.text if temp_nested_msg == "" else temp_nested_msg}**"
        elif i.name == "s":
            msg_text += f"~~{i.text if temp_nested_msg == "" else temp_nested_msg}~~"
        elif i.name == "em":
            msg_text += f"~~{i.text if temp_nested_msg == "" else temp_nested_msg}~~"
        elif i.name == "U":
            msg_text += f"__{i.text if temp_nested_msg == "" else temp_nested_msg}__"
    elif type(i) == element.NavigableString:
        msg_text += i.text
    
    return msg_text

# file starts at 8 & ends at 166080
LINE_START = 8
LINE_END = 18

line_count = 0
msg_count = 0
msg_group_count = 0
potential_error_lines = {}
error_lines = {}
cleared = True
last_progress = 0
progress = 0
msgs = []
all_msgs = {}
multiline_buffer = ""
with open("errorLog.html", 'w') as error_log:
    error_log.write('')
for i in range(10):
    with open(f"output/log{i}.json", 'w') as output:
        output.write('')

try:
    for msg_group in fileinput.input(["fullLog.html"], encoding="utf-8", mode='r'):
        line_count += 1
        if line_count < LINE_START:
            continue

        if len(msg_group) <= 16 or msg_group[-2] != '>' or msg_group[-3] != 'v':
            multiline_buffer += msg_group
            continue
        
        if multiline_buffer != "":
            msg_group = multiline_buffer + msg_group
            multiline_buffer = ""

        msg_group_count += 1
        msgs = []

        progress = line_count / 166080 
        if progress - last_progress > 0.1:
            print(f"{int(progress * 100)}% - {line_count} / 166080")
            last_progress = progress
            all_msgs = {}

        inner_msg_count = 0
        soup = bs(msg_group, "html.parser")
        try:
            avatar = soup.find("img", class_="chatlog__avatar")["src"]
        except TypeError:
            if soup.find("span", class_="chatlog__system-notification-author"):
                continue
            else:
                raise
        name = soup.find("span", class_="chatlog__author").text

        try:
            reply = soup.find("span", class_="chatlog__reference-link")
            reply_id = str(reply["onclick"]).split("'")[1]
            reply_author = soup.find("div", class_="chatlog__reference-author").text
            reply_text = f"> {reply_author}: \n> {all_msgs[reply_id]}\n"
        except TypeError:
            reply_text = ""

        for msg in soup.find_all("div", class_="chatlog__message-primary"): 
            inner_msg_count += 1
            msg_count += 1
            msg_id = msg.parent.parent["data-message-id"]
            md = msg.find("span", class_="chatlog__markdown-preserve")
            links = msg.find_all("img", {"class": ["chatlog__attachment-media", "chatlog__embed-generic-image", "chatlog__sticker--media"]}) + msg.find_all("source", {"alt": ["Video attachment", "Embedded video", "Audio attachment"]})
            midi = msg.find_all("div", class_="chatlog__attachment-generic-name")
            msg_text = reply_text
            stickers = msg.find_all("div", class_="chatlog__sticker--media")

            if md:
                for i in md:
                    msg_text += f" {msg_format(i)}"
            else:
                embed = msg.find_all("a", class_="chatlog__embed-image-link")
                md = msg.find_all("div", class_="chatlog__markdown-preserve")
                if md:
                    for i in md:
                        for j in i:
                            msg_text += msg_format(j)
                    links += msg.find_all("img", class_="chatlog__embed-image-link")
                if embed:
                    for i in embed:
                        msg_text += f" {i["href"]}"
            if midi:
                for i in midi:
                    msg_text += f" {i.contents[0]["href"]}"
            if links:
                for i in links:
                    msg_text += f" {i["src"]}"
            if stickers:
                for i in stickers:
                    msg_text += f"Sticker: {i.parent["title"]}"
            # print(msg_text)
            if len(msg_text) != 0 and msg_text[0] == ' ':
                msg_text = msg_text[1:]
            msgs.append(msg_text)
            all_msgs[msg_id] = msg_text
            if msg_text == "":
                try:
                    soup.find("span", class_="chatlog__bot-label")
                    potential_error_lines[line_count] = inner_msg_count
                except:
                    error_lines[line_count] = inner_msg_count
            with open("errorLog.html", 'a') as error_log:
                error_log.write(soup.prettify())
                error_log.writelines("\n\n")

        with open(f"output/log{int(progress * 10)}.json", 'a', encoding="utf-8") as output:
            json.dump({
                msg_group_count: {
                    "name": str(name),
                    "avatar": str(avatar),
                    "msgs": msgs
                }
            }, output, indent=4, ensure_ascii=False)

        if line_count >= LINE_END:
            # print(f"Last message: {msg_group}")
            break
except Exception as e:
    with open("errorLog.html", 'a') as error_log:
        error_log.write(soup.prettify())
    print(f"\nEXCEPTION ERROR: {line_count, inner_msg_count}")
    print(e)
    print(msg)
    cleared = False

end = time.time()
print(f"\nRuntime: {end - start}")
print(f"Potential errors: {potential_error_lines}")
print(f"Errors: {error_lines}")
print(f"Messages count: {msg_count}")
print(f"Message goups count: {msg_group_count}")
if len(error_lines) == 0 and cleared:
    print("\n\n====✅ ALL CLEARED====\n\n")

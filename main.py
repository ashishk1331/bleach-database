import requests
import ast
from bs4 import BeautifulSoup
import re
import json
from rich import print
from rich.progress import track


def sanitize(original_string: str) -> str:
    """Cleans the text for excessive space and special characters.

    Args:
        original_string: Original string which is to be processed
    
    Returns:
        Cleaned and sanitized string.
    """
    cleaned_string = re.sub(r"[\t\n\s]+", " ", original_string)
    cleaned_string = re.sub(r"\[\d+\]$", "", cleaned_string)
    cleaned_string = re.sub(r" +", " ", cleaned_string).strip()
    cleaned_string = re.sub(
        r"\\u([0-9a-fA-F]{4})", lambda x: chr(int(x.group(1), 16)), cleaned_string
    )
    return cleaned_string


def parse_quote(quote: str, gender: str ="male") -> (str, str):
    text = re.findall(r'"([^"]*)"', quote)
    if text:
        text = text[0]
    else:
        text = quote
    text = re.sub(r"\(.+\)", "", text)
    text = re.sub(r"\[\d+\]", "", text)

    recepient = re.findall(r"\((?:To )?([^)]*)\)", quote)
    recepient = (
        recepient[0] if recepient else ("Himself" if gender == "male" else "Herself")
    )

    return text, recepient


def get_text(element):
    return sanitize(element.get_text())


data = None
with open("data.json", "r") as file:
    data = json.loads(file.read())


def get_data(links, log=[], title=""):
    characters = []

    for link in track(links, description=f"Processing {title}..."):
        r = requests.get(link)
        soup = BeautifulSoup(r.content, "html5lib")

        title = soup.find("meta", attrs={"property": "og:title"})
        if title:
            title = title["content"]
        else:
            title = get_text(soup.find(id="firstHeading"))

        aside = soup.find("aside")

        images = soup.find_all("img")
        media = []
        for img in images:
            source = img["src"]
            if source.startswith("https://static.wikia.nocookie.net/bleach"):
                source = re.sub(r"\/scale-to-width-down\/\d+", "", source)

                alt = img["alt"]
                parent = img.find_parent("a")
                if parent:
                    parent = parent.find_parent("figure")
                    if parent:
                        parent = parent.find("figcaption")
                        if parent:
                            alt = get_text(parent)

                if len(alt) > 0 and not alt.startswith("Bleach Wiki"):
                    media.append({"source": source, "alt": alt})

        sections = aside.find_all("section")

        map = {}
        for sec in sections:
            header = sec.find("h2")
            if header:
                header = get_text(header)
                map[header] = {}
            for div in sec.find_all("div"):
                heading = div.find("h3")
                value = []
                for i in div.find_all("a"):
                    text = get_text(i)
                    if text:
                        value.append(text)
                if len(value) == 1:
                    value = value[0]

                if heading:
                    if not value:
                        value = get_text(div.find("div"))
                    heading = get_text(heading).lower()
                    if header:
                        map[header][heading] = value
                    else:
                        map[heading] = value

        images = aside.find_all("img", attrs={"class": "pi-image-thumbnail"})
        src = []
        for img in images:
            src.append(re.sub(r"\/scale-to-width-down\/\d+", "", img["src"]))

        stats = {"id": title.lower().replace(" ", "_"), "name": title}

        description = soup.find("meta", attrs={"property": "og:description"})
        if description:
            d = description["content"]
            stats["description"] = d[: d.rindex(".") + 1]
            token = re.findall(r"\(.+\)", d)
            if token and token[0].rfind(",") > -1:
                token = token[0]
                kanji, romaji = (
                    token[1 : token.rindex(",")],
                    token[token.rindex(",") + 1 : -1],
                )
                stats["name"] = {
                    "english": sanitize(title),
                    "kanji": sanitize(kanji),
                    "romaji": sanitize(romaji),
                }

        stats["avatar"] = src[0] if len(src) == 1 else src
        stats["stats"] = map
        stats["media"] = media

        quotes = soup.find(id="Quotes")
        if quotes:
            quotes = quotes.find_parent("h2").find_next_siblings("ul")
            capture_quotes = []
            for q in quotes:
                ref = q.find("sup", attrs={"class": "reference"})
                reference = None
                quote = None
                if ref:
                    ref_id = ref.find("a")["href"][1:]
                    cite_ref = soup.find(id=ref_id)
                    if cite_ref:
                        reference = get_text(cite_ref)
                        reference = reference[reference.index(" ") + 1 :]

                quote = get_text(q)
                (aba, to) = parse_quote(quote, stats["stats"]["gender"])

                capture_quotes.append({"quote": aba, "to": to, "reference": reference})

            stats["quotes"] = capture_quotes

        characters.append(stats)
        log.append(title)
        print(f"[green]√[/green] [italic]{title}[/italic] is recorded.")

    return characters


log = {}

for key, links in data.items():
    g = []
    chrs = get_data(links, g, title=key)
    log[key] = g

    with open(f"data/{key}.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(chrs, indent=4, ensure_ascii=False))
        print(
            f"\n[green]√[/green] file written for [italic green]{key}[/italic green]\n"
        )

with open(f"data/log.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(log, indent=4, ensure_ascii=False))
    print(f"\n[green]√[/green] file written for [italic green]log[/italic green]\n")

# get_data(["https://bleach.fandom.com/wiki/Kisuke_Urahara"])
# print(json.dumps(get_data(["https://bleach.fandom.com/wiki/Kisuke_Urahara"]), indent=4, ensure_ascii=False))

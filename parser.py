import pymupdf
import re
import json
from io import StringIO

def handle_packet(data, debug=False):
    reader = pymupdf.Document(stream=data)

    fake_file = StringIO()
    for page in reader:
        text = page.get_text()
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:
            for l in b["lines"]:
                for s in l["spans"]:
                    if(s["flags"] & 2 ** 0):
                        fake_file.write("<sup>")
                    fake_file.write(s["text"])
                    if(s["flags"] & 2 ** 0):
                        fake_file.write("</sup>")
                fake_file.write("\n")
        fake_file.write("\n")

    pset = re.sub(r'</sup><sup>','',fake_file.getvalue())

    #f = open("demo.txt", "w", encoding="utf-8")
    #f.write(repr(pset))
    #f.close()
    #return

    regex_q = r"(?P<weight>TOSS-UP|BONUS)(?:\s)*\d+\)(?:\s)*(?P<category>[\s\S]*?)(?:\s*-*‒*–*—*―*\s*)(?P<type>Short Answer|Multiple Choice)(?:\s)*(?P<question>[\s\S]*?)(?:\s)*ANSWER:"
    matches_q = re.finditer(regex_q, pset, re.MULTILINE)

    regex_a = r"ANSWER: (?P<answer>[\s\S]*?)(?:\Z|\n[ ]*(?:BONUS|_|\n))"
    matches_a = re.finditer(regex_a, pset, re.MULTILINE)

    packet = {
        "weights": [],
        "categories": [],
        "types": [],
        "questions": [],
        "choices": [],
        "answers": []
    }

    count = 0

    for _, match in enumerate(matches_q, start=1):
        packet["weights"].append(re.sub(r'\s+',' ',match.group('weight')))
        packet["categories"].append(re.sub(r'\s+',' ',match.group('category')))
        packet["types"].append(re.sub(r'\s+',' ',match.group('type')))
        if packet["types"][count] == "Short Answer":
            packet["questions"].append(re.sub(r'\s+',' ',match.group('question')))
            packet["choices"].append(None)
        else:
            regex_mc = r"(?P<main>[\s\S]*?)(?:\s)*W\)(?:\s)*(?P<w>[\s\S]*?)(?:\s)*X\)(?:\s)*(?P<x>[\s\S]*?)(?:\s)*Y\)(?:\s)*(?P<y>[\s\S]*?)(?:\s)*Z\)(?:\s)*(?P<z>[\s\S]*?)(?:\s)*\Z"
            matches_mc = re.finditer(regex_mc, match.group('question'), re.MULTILINE)
            for _, submatch in enumerate(matches_mc, start=1):
                packet["questions"].append(re.sub(r'\s+',' ',submatch.group('main')))
                packet["choices"].append([re.sub(r'\s+',' ',submatch.group('w')), re.sub(r'\s+',' ',submatch.group('x')), re.sub(r'\s+',' ',submatch.group('y')), re.sub(r'\s+',' ',submatch.group('z'))])
        count += 1

    for matchNum, match in enumerate(matches_a, start=1):
        tmp = re.sub(r'\s+',' ',match.group('answer'))
        if tmp[0] == ' ':
            tmp = tmp[1:]
        if len(tmp) > 0 and tmp[len(tmp) - 1] == ' ':
            tmp = tmp[:-1]
        packet["answers"].append(tmp)
        

    if(debug):
        for i in range(0,count):
            print(packet["weights"][i])
            print(packet["categories"][i])
            print(packet["types"][i])
            print(packet["questions"][i])
            print(packet["choices"][i])
            print(packet["answers"][i])
            print("----------------------------------------------")

    return json.dumps(packet, indent = 4)

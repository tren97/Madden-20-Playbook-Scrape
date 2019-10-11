from datetime import datetime
import xlsxwriter
import csv
import requests
import bs4
import re

#Capitalizes all words in the lists that contain information about playbooks
def capitalList(thelist):
    newList = []
    for val in thelist:
        if not val:
            newList.append(val)
        elif val[0].isalpha:
            newList.append(val.title())
        else:
            newList.append(val)
    return newList

#figures out whether playbook is offense or defense
def OorD(thelist):
    for i in thelist:
        if i == "Offense":
            return "Offense"
        if i == "Defense":
            return "Defense"
    return

#Use on initial list to get the name of the playbook
def getPlaybookName(thelist):
    name = ""
    for i in thelist[4:]:
        if i == "Offense" or i == "Defense":
            break
        else:
            name+=i
    name = re.sub(r"(\w)([A-Z])", r"\1 \2", name)
    return name

#finds formation from the URL
def getFormation(thelist):
    start = 0
    magicIndex = 1000
    formation = ""
    prevWord = ""
    while start < len(thelist):
        if thelist[start] == "Offense" or thelist[start] == "Defense":
            magicIndex = start + 2
        if start >= magicIndex:
            if prevWord == "Dime" or prevWord == "Quarter" or prevWord == "Dollar" or \
                    prevWord == "Wide" or prevWord == "Nickel" or prevWord == "Line" or prevWord == "Return" \
                    or prevWord == "A" or prevWord == "Block":
                formation += " " + (thelist[start])
            elif thelist[start] == "Hb" or thelist[start] == "Te":
                formation += (thelist[start]).upper()
            elif thelist[start] == "Y":
                formation += (thelist[start]) + " "
            else:
                formation+=(thelist[start])
        prevWord = thelist[start]
        start+=1
    formation = re.sub(r"(\w)([A-Z])", r"\1 \2", formation)
    return formation

#Adds playbooks and formations to spredsheet
def populateSpreadsheet():
    myWorkbook = xlsxwriter.Workbook('madden20formations.xlsx')
    OffenseWS = myWorkbook.add_worksheet('Offense')
    DefenseWS = myWorkbook.add_worksheet('Defense')
    site = requests.get("https://www.playbook.gg/20/playbooks/")
    src = site.content
    soup = bs4.BeautifulSoup(src, 'lxml')
    allList = soup.find_all("div", {"class": "pbdb-list-item"})
    for i,val in enumerate(allList):
        tempSite = requests.get("https://www.playbook.gg" + allList[i].a["href"])
        tempSrc = tempSite.content
        tempSoup = bs4.BeautifulSoup(tempSrc, 'lxml')
        tempAllList = tempSoup.find_all("div", {"class": "pbdb-list-item"})
        tempInfoList = capitalList(re.split('\W+', allList[i].a["href"]))
        if OorD(tempInfoList) == "Offense":
            OffenseWS.write(0, i, allList[i].a.get_text())
        elif OorD(tempInfoList) == "Defense":
            DefenseWS.write(0, i-40, allList[i].a.get_text())
        for j, val in enumerate(tempAllList):
            tempInfoList2 = capitalList(re.split('\W+', tempAllList[j].a["href"]))
            if OorD(tempInfoList2) == "Offense":

                OffenseWS.write(j+1, i, getFormation(tempInfoList2))
            elif OorD(tempInfoList2) == "Defense":
                DefenseWS.write(j+1, i-40, getFormation(tempInfoList2))
    myWorkbook.close()


def main():

    populateSpreadsheet()


    site = requests.get("https://www.playbook.gg/20/playbooks/")
    src = site.content
    soup = bs4.BeautifulSoup(src, 'lxml')
    allList = soup.find_all("div", {"class": "pbdb-list-item"})
    temp = allList[5].a.get_text()
    infoList = capitalList(re.split('\W+', temp))
    print(getFormation(infoList))
    print(temp)

if __name__ == "__main__":
    main()
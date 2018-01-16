import os.path #Kontrollib, kas fail on olemas
import json #Teeb dictionary oma stringiks, et seda faili panna
import requests #Lingi saamiseks
import smtplib #Emaili saatmine ja mingi hookuspookus
import urllib.parse #Parsib urli tükkideks
import re #Uurib Youtube otsingu tulemusi
from bs4 import BeautifulSoup #Aitab html koodi lugeda
from email.mime.text import MIMEText #Emaili saatmine -> kirja pealkiri
from email.mime.multipart import MIMEMultipart #Paneb kirja pealkirja ja sisu kokku
 
def kontrolliFilmiDicti(failinimi):
    if os.path.exists(failinimi):
        fail = open(failinimi, 'r',encoding='utf-8')
        filmiDict = json.loads(fail.read())
        fail.close()
    #Kui faili pole, siis teeme tühja faili
    else:
        filmiDict = {}
    return filmiDict
 
def saadaMeil(saatjaMeil, saatjaParool, saajaMeil):
    msgSisu = ''
    for film in filmid:
        nimi = film.select_one('.list-item-desc-title a').text
        kpv = film.select_one('.event-releaseDate b').text
        zanrid = film.select_one('.genre-names b').text
        youtubeLink = film.select_one('.btn-group a')
       
        if youtubeLink:
            youtube = youtubeLink.get('href') #Päris youtube link
            trailer = (' Treileri link on: ' + str(youtube))
        else:
            urlmuutja = urllib.parse.urlencode({"search_query" : nimi}) #muudab otsingusõna URL'i osaks
            html_sisu = urllib.request.urlopen("http://www.youtube.com/results?" + urlmuutja) #avab lingi
            tulemused = re.findall(r'href=\"\/watch\?v=(.{11})', html_sisu.read().decode()) #leiab kõik otsingu tulemused
            youtube = ("http://www.youtube.com/watch?v=" + tulemused[0]) # võtab esimese tulemuse
            trailer = (' Kahjuks Apollo lehel trailerit pole, siin on YouTubest filmi pealkirja otsides leitud võimalik treiler: ' + str(youtube))
           
        uuid = film.select_one('.list-item-desc-title a').get('href') #URL ID, et eristada filme lihtsasti
       
        if uuid not in filmiDict:
            msgSisu += ('\n Apollos on uus film: ' + nimi + ', mis esilinastub ' + str(kpv) + '.' + str(trailer) + '. Filmi zanr on: ' + zanrid + '.\n')
 
        filmiDict[uuid] = {"nimi":nimi, "kuupäev":kpv, "zanr":zanrid, "treiler":youtube}
    msg = MIMEMultipart()
    msgTervitus = 'Tere!\n'
    msgLopp = '\nHead filmielamust!'
    msg4 = msgTervitus + msgSisu + msgLopp #Paneme emaili sisu kokku
    msg['Subject'] = "Uued filmid Apollos"
    msg.attach(MIMEText(msg4, 'plain')) #Paneme kokku emaili pealkirja ja sisu
    text = msg.as_string() #Tanu sellele on meil tapitahed!!
    if msgSisu != '':
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(saatjaMeil, saatjaParool)
        server.sendmail(saatjaMeil, saajaMeil, text.encode('utf-8')) #kui tahta mitmele inimesele saata, tuleb kopeerida seda rida teiste argumentidega
        server.quit()  
 
#Loeme andmed sisse html koodina
linkApollo = requests.get('https://www.apollokino.ee/soon')
supp = BeautifulSoup(linkApollo.text, 'html.parser')
#Otsime koha üles, kus asuvad meie filmid ja nende info
filmid = supp.select(".ContentBlockComingSoon .EventList-container > div")
#Kontrollime, kas fail on juba olemas ja loeme faili sisse juhul, kui see on olemas
filmiDict = kontrolliFilmiDicti('filmid.txt')
#NB! Saatja meil peab olema @gmail.com lõpuga!
saadaMeil('lehtmetslane@gmail.com', 'mees123GG', 'meeliste@mail.com')
 
json_string = json.dumps(filmiDict) #Teeb dictionary oma jamaks, et see ilusti stringina faili panna
#Kirjutame uue faili, kus sees on ka kõik uued filmid
fail = open('filmid.txt', 'w', encoding='utf-8')
fail.write(json_string)
fail.close()
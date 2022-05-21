import cv2
import sys
import os
import speech_recognition as sr
import webbrowser
import pyttsx3
import os.path
import requests
import json
from datetime import datetime

import python_weather
import asyncio

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

video_capture = cv2.VideoCapture(0)

count = 0;
tirouFoto = False


async def pegarTemperatura():
    client = python_weather.Client(format=python_weather.METRIC)
    robs = pyttsx3.init()
    print("Informe uma cidade: ")
    robs.say("Obrigado por informar uma cidade")

    som = recon.listen(source)
    cidade = recon.recognize_google(som, language='pt-br')
    recon.adjust_for_ambient_noise(source, duration=3)

    weather = await client.find(cidade)

    temperaturaAtual = "A temperatura da cidade de: " + cidade + " é de: " + str(
        weather.current.temperature) + " Graus Celsius"
    print(temperaturaAtual)
    robo.say(temperaturaAtual)
    robo.runAndWait()

    # Fecha o sistema
    await client.close()


def abrirWebsite(comando, url):
    robo.say("Abrindo " + comando)
    print("Abrindo " + comando + "...")
    robo.runAndWait()
    webbrowser.open(url, autoraise=True)


recon = sr.Recognizer()
resposta = ""
hora = (str(datetime.today().hour) + ":" + str(datetime.today().minute))

parar = False

while True:
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        face = frame[y:y + h, x:x + w]  # slice the face from the image
        if not tirouFoto:
            tirouFoto = True
            cv2.imwrite(str(count) + '.jpg', face)  # save the image
            count += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        video_capture.release()
        cv2.destroyAllWindows()
        with sr.Microphone(1) as source:
            while not parar:
                audio = recon.listen(source)
                recon.adjust_for_ambient_noise(source)
                res = recon.recognize_google(audio, language='pt-br')
                resposta = res.lower()
                print("Texto reconhecido: ", resposta.lower())

                if resposta == "ok sexta-feira":
                    robo = pyttsx3.init()
                    robo.say("Sim mestre. O que devo fazer?")
                    print("Sim mestre. O que devo fazer?")
                    robo.setProperty("voice", b'brasil')
                    robo.setProperty('rate', 140)
                    robo.setProperty('volume', 1)
                    robo.runAndWait()

                    while True:

                        audio = recon.listen(source)
                        res = recon.recognize_google(audio, language='pt-br')
                        recon.adjust_for_ambient_noise(source, duration=3)
                        resposta = res.lower()
                        print("Texto reconhecido: ", resposta)

                        if "notícias" in resposta:
                            abrirWebsite(resposta, 'https://g1.globo.com/sp/sao-paulo/')
                            break

                        if "que horas são" in resposta:
                            robo.say(hora)
                            print(hora)
                            robo.runAndWait()
                            break

                        if "temperatura atual" in resposta:
                            loop = asyncio.get_event_loop()
                            loop.run_until_complete(pegarTemperatura())
                            break

                        if "cadastrar evento na agenda" in resposta:
                            fala = "Ok, qual evento devo cadastrar?"
                            robo.say(fala)
                            print(fala)
                            robo.runAndWait()

                            audio = recon.listen(source)
                            resAgenda = recon.recognize_google(audio, language='pt-br')

                            file_exists = os.path.exists('agenda.txt')

                            if not file_exists:
                                text_file = open("agenda.txt", "w")
                                text_file.write(resAgenda)
                                text_file.close()
                                robo.say("Evento cadastrado")
                                print("Evento cadastrado")
                                break

                            else:
                                text_file = open("agenda.txt", "a")
                                text_file.write("\n" + resAgenda)
                                text_file.close()
                                robo.say("Evento cadastrado")
                                print("Evento cadastrado")
                                continue

                        if "ler agenda" in resposta:
                            with open("agenda.txt") as file:
                                for line in file:
                                    line = line.strip()  # preprocess line
                                    robo.say(line)
                                    robo.runAndWait()
                                break

                        if "dólar atual" in resposta:
                            requisicao = requests.get('https://economia.awesomeapi.com.br/all/USD-BRL')
                            cotacao = requisicao.json()

                            print('#### Cotação do Dolar ####')
                            print('Moeda: ' + cotacao['USD']['name'])
                            print('Data: ' + cotacao['USD']['create_date'])
                            valor = 'Valor atual: R$' + cotacao['USD']['bid']
                            robo.say(valor)
                            print(valor)
                            robo.runAndWait()
                            break

                        if "calculadora" in resposta:
                            while True:
                                try:
                                    fala = "O que deseja calcular?"
                                    robo.say(fala)
                                    print("O que deseja calcular?")
                                    audio = recon.listen(source)

                                    contatxt = recon.recognize_google(audio, language='pt')
                                    print("Texto reconhecido: '", contatxt)

                                    if contatxt == "fechar":
                                        break
                                    conta = contatxt.split()

                                    if conta[1] == "+":
                                        print("Resultado: ", contatxt, " = ", str(int(conta[0]) + int(conta[2])))

                                    elif conta[1] == "-":
                                        print("Resultado: ", contatxt, " = ", str(int(conta[0]) - int(conta[2])))

                                    elif conta[1] == "/":
                                        print("Resultado: ", contatxt, " = ", str(int(conta[0]) / int(conta[2])))

                                    elif conta[1] == "x":
                                        print("Resultado: ", contatxt, " = ", str(int(conta[0]) * int(conta[2])))
                                except:
                                    print('Alguma coisa bugou')
                                    break

                        elif "parar" in resposta:
                            robo.say("OK! Até mais tarde senhor!")
                            robo.runAndWait()
                            parar = True
                            break
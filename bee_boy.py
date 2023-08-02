import pandas as pd
from fuzzywuzzy import fuzz, process
import openai
import streamlit as st
import streamlit_chat
#testmerge

def get_completion(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=700,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    return response.choices[0].text

def get_index(item,list):
    index = 9999
    for i in range(len(list)):
        if list[i] == item:
            index = i
    return index

def find_similar_items_smart(input,data_base,liste_commentaire,liste_description):
    
    resultats_description = process.extract(input,liste_description, limit=9)
    resultats_commentaire = process.extract(input,liste_commentaire,limit=9)
    liste_elements_description = []
    liste_elements_commentaire = []
    for resultat in resultats_description:
        if resultat[1]>60:
            liste_elements_description.append(resultat[0])
        
    for resultat in resultats_commentaire:
        if resultat[1]>60:
            liste_elements_commentaire.append(resultat[0])
        
    liste_elements = []
    for item in liste_elements_description:
        index = get_index(item,liste_description)
        liste_elements.append(data_base[index])
    for item in liste_elements_commentaire:
        index = get_index(item,liste_commentaire)
        liste_elements.append(data_base[index])

    
    return liste_elements

def main():

    correct_password = "lalala"
    password = st.text_input("Entrer le mot de passe :", type="password")
    
    api_key = st.text_input("Entrer la clé d'API :", type="password")
    if password == correct_password and len(api_key)>50:
        df_historique_panne = pd.read_excel('Nouveau document texte.xlsx') 
        liste_commentaire  = df_historique_panne["commentaires"].tolist()
        
        liste_description = df_historique_panne["descriptions"].tolist()
        
        liste_commentaire_final = []
        for i in range(len(liste_commentaire)):
            liste_commentaire_final.append(" descriptions de la panne : "+str(liste_description[i])+" commentaire sur la panne : "+str(liste_commentaire[i]))
        
        openai.api_key = api_key
        st.title("Bee Boy actemium assistant")
        st.title("version 1.0")
        if "messages" not in st.session_state:
            first_txt = """Salut ! 👋 Je suis là pour transformer le dépannage en une tâche facile pour vous. Parlons de votre problème et découvrons les meilleures solutions ensemble."""
            st.session_state.messages = [{"role": "assistant", "message": first_txt,"content" :""}]
            


        user_input = st.chat_input()
        if user_input:
            st.toast('Vérification en cours...')
            st.session_state.messages.append({"role": "user", "message": user_input,"content":""})
            response = ""
            prompt = "est ce que cette phrase : " +user_input+" contient des  mots techniques en relation avec la maintenace industrielle? repond seulement par oui ou non"
            response1 = get_completion(prompt)
            if "oui" in response1.lower():
                st.toast('Recherche des pannes similaires... ',icon = "🤖")
                key_words = get_completion("detecte les mots clés de cette phrase : " +user_input+" .retourne seulement les mots clés")
                print(key_words)
                similar_data  = find_similar_items_smart(key_words,liste_commentaire_final,liste_commentaire,liste_description)
                
                prompt = "en se basant seulement sur cet historique de panne et de actions faites : " + str(similar_data) + " tire toutes les actions réalisées en relation avec  le probleme : "+user_input+". je veux la liste  avec les actions realise reformulés pour le probleme."
                response = get_completion(prompt)
                print(response)
                
            else:
                st.toast("c'est pas une question technique liée à la maintenance industrielle",icon = "😵")
                response = "Je suis votre assistant de maintenance, et je peux répondre uniquement à des questions techniques liées à la maintenance industrielle."
            st.session_state.messages.append({"role": "assistant", "message":response,"content":""})
        if "messages" in st.session_state:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["message"])
    else:
        st.error("Mot de passe incorrecte ou clé invalide.")
main()












            
                        


    
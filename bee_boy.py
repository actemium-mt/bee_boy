import pandas as pd
from fuzzywuzzy import fuzz, process
import openai
import streamlit as st
import streamlit_chat
#test push

def get_completion(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    return response.choices[0].text

def find_similar_items_smart(input,data_base):
    
    resultats = process.extract(input, data_base, limit=10)
    liste_elements = []
    for resultat in resultats:
        liste_elements.append(resultat[0])
    
    return liste_elements

def main():
    df_historique_panne = pd.read_excel('Nouveau document texte.xlsx') 
    liste_commentaire  = df_historique_panne["COMMENTAIRE "].tolist()
    liste_commentaire_non_null = []
    for i in range(len(liste_commentaire)):
        if str(liste_commentaire[i]) != 'nan':
            liste_commentaire_non_null.append(liste_commentaire[i])
    resultats = process.extract("probleme", liste_commentaire_non_null, limit=4000)
    liste_commentaire_final = []
    for resultat in resultats:
        liste_commentaire_final.append(resultat[0])
    api_key ="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"
    openai.api_key = api_key
    st.title("Bee Boy actemium assistant")
    if "messages" not in st.session_state:
        first_txt = """Salut ! 👋 Je suis là pour transformer le dépannage en une tâche facile pour vous. Parlons de votre problème et découvrons les meilleures solutions ensemble."""
        st.session_state.messages = [{"role": "assistant", "message": first_txt,"content" :""}]
        

    user_input = st.chat_input()
    if user_input:
        st.session_state.messages.append({"role": "user", "message": user_input,"content":""})
        response = ""
        prompt = "est ce que ceette phrase : " +user_input+" contient des  mots techniques en relation avec la maintenace industrielle? repond seulement par oui ou non"
        response1 = get_completion(prompt)
        if "oui" in response1.lower():
            similar_data  = find_similar_items_smart(user_input,liste_commentaire_final)
            prompt = "en se basant seulement sur ça " + str(similar_data) + " tire tout les actions les plus pertinentes en relation avec"+user_input+"et presente les comme des listes d'actions qu'on peut faire en reformulant une reponse technique et developpent bien chaque actions"
            response = get_completion(prompt)
        else:
            response = get_completion(user_input)
        st.session_state.messages.append({"role": "assistant", "message":response,"content":""})
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["message"])

main()












            
                        


    
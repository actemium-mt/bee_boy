import pandas as pd
from fuzzywuzzy import fuzz, process
import openai
import streamlit as st
import streamlit_chat
from streamlit_star_rating import st_star_rating
from PIL import Image
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
        liste_elements.append(str(data_base[index])+"||")
    for item in liste_elements_commentaire:
        index = get_index(item,liste_commentaire)
        liste_elements.append(str(data_base[index])+"||")

    
    return liste_elements

def main():
    image = Image.open('Boy-removebg-preview.png')
    correct_password = "lalala"
    password = st.text_input("Entrer le mot de passe :", type="password")
    api_key = st.text_input("Entrer la clé d'API :", type="password")
    first_txt = """Salut ! 👋 Je suis là pour transformer le dépannage en une tâche facile pour vous. Parlons de votre problème et découvrons les meilleures solutions ensemble."""
    sorry_text = """Je suis votre assistant de maintenance, et je peux répondre uniquement à des questions techniques liées à la maintenance industrielle."""
    df_commentaire = pd.read_excel("commentaire.xlsx")
    commentaire_liste = df_commentaire["Commentaire"].tolist()
    avis_liste = df_commentaire["Avis"].tolist()
    question_liste = df_commentaire["Question"].tolist()
    reponse_liste = df_commentaire["Réponse"].tolist()
    
    if password == correct_password and len(api_key)>50:
        df_historique_panne = pd.read_excel('Nouveau document texte.xlsx') 
        liste_commentaire  = df_historique_panne["commentaires"].tolist()
        
        liste_description = df_historique_panne["descriptions"].tolist()
        
        liste_commentaire_final = []
        for i in range(len(liste_commentaire)):
            liste_commentaire_final.append(" descriptions de la panne : "+str(liste_description[i])+" commentaire sur la panne : "+str(liste_commentaire[i]))
        
        openai.api_key = api_key
        st.title("Bee Boy actemium assistant")
        st.image(image)
        st.title("version 1.2")
        if "messages" not in st.session_state:
            
            st.session_state.messages = [{"role": "assistant", "message": first_txt,"content" :""}]
            

        response = ""
        user_input = st.chat_input()
        if user_input:
            st.toast('Vérification en cours...')
            st.session_state.messages.append({"role": "user", "message": user_input,"content":""})
            
            prompt = "est ce que cette phrase : " +user_input+" contient des  mots techniques en relation avec la maintenace industrielle? repond seulement par oui ou non"
            response1 = get_completion(prompt)
            if "oui" in response1.lower():
                st.toast('Recherche des pannes similaires... ',icon = "🤖")
                key_words = get_completion("detecte les mots clés de cette phrase : " +user_input+" .retourne seulement la liste des mots clés")
                print(key_words)
                key_words_list = key_words.split(",")
                important_key_words_list = []
                for word in key_words_list:
                    if 'panne' not in word.lower() and word not in '1 2 3 4 5 6 7 8 9' and 'prob' not in word.lower() and 'retour' not in word.lower() and 'erreur' not in word.lower() and 'machine' not in word.lower():
                        important_key_words_list.append(word)
                important_key_words = ' '.join(important_key_words_list)
                print(important_key_words)
                similar_data  = find_similar_items_smart(important_key_words,liste_commentaire_final,liste_commentaire,liste_description)
                print(similar_data)
                prompt = "en se basant seulement sur ces donnees:" + str(similar_data) + "tire toutes les actions faites (fait) en relation avec "+user_input

                response1 = get_completion(prompt)
                prompt2 = str(response1) + " reformule cette reponse en me donnant une liste (bullet point) des actions faites pour le probleme " + user_input
                response = get_completion(prompt2)
                print(response)
                
                
            else:
                st.toast("c'est pas une question technique liée à la maintenance industrielle",icon = "😵")
                response = sorry_text
            st.session_state.messages.append({"role": "assistant", "message":response,"content":""})

        if "messages" in st.session_state:
            i = 0
            j = 0
            
            for message in st.session_state.messages: 
                with st.chat_message(message["role"]):
                    st.write(message["message"])
                    if message["message"] != first_txt and message["role"] == "assistant" and message["message"]!=sorry_text:
                        form_key = "rating_form" + str(j+1000)
                        with st.form(key = form_key):
                            col1,col2 = st.columns(2)
                            with col1:
                                st.markdown("<h3>Commentaire</h3>", unsafe_allow_html=True)
                                commentaire = st.text_area("",key = i,placeholder = "Que pensez-vous de la réponse de Bee Boy",label_visibility="collapsed")
                            with col2:
                                stars = st_star_rating("Avis", maxValue=5, defaultValue=1, key=i+1,emoticons = True)
                            submitted = st.form_submit_button("Envoyer")
                            if submitted:
                                commentaire_liste.append(commentaire)
                                avis_liste.append(stars)
                                question_liste.append(st.session_state.messages[j-1]["message"])
                                reponse_liste.append(message["message"])
                                new_df_commentaire = pd.DataFrame({'Question':question_liste,'Réponse':reponse_liste,'Commentaire':commentaire_liste,'Avis':avis_liste})
                                new_df_commentaire.to_excel("commentaire.xlsx")
                                st.success("Merci pour votre retour, c'est très important pour l'amélioration de votre assistant préféré Bee Boy! 😀")

                i=i+2
                j=j+1
            

    else:
        st.error("Mot de passe incorrecte ou clé invalide.")
    
        
main()












            
                        


    
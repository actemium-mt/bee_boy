import pandas as pd
from fuzzywuzzy import fuzz, process
import openai
import streamlit as st
import streamlit_chat
from streamlit_star_rating import st_star_rating
from PIL import Image
import csv
from joblib import *
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

def extract(list):
    txt = ""
    for item in list:
        txt = txt  + str(item)
    return txt

def df_to_list(df):
    list = []
    for index,row in df.iterrows():
        list.append("Probleme : " + str(row["DESCIPTIONS "]) + " / " + " Machine : " + str(row["N°SAP_Designation"]) + " / " + " Organe Machine : " + str(row["ORGANE MACHINE "]) + " / " + " Commentaire : " + str(row["COMMENTAIRES"]) + " ||| ")
    return list

def main():
    sub_df = pd.DataFrame({})
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
    df_historique = pd.read_excel("analyse_panne.xlsx")
    
    data = load("data.joblib")
    liste_machine = data["liste_machine"]
    mapping_organe_machine = data["mapping_organe_machine"]
    
    
    
    text_utile = extract(sub_df)
    if password == correct_password and len(api_key)>50:
        openai.api_key = api_key
        st.title("Bee Boy actemium assistant")
        st.image(image)
        st.title("version 1.2")
        machines = st.multiselect("Machine(s):",liste_machine)
        expanded = not((len(machines) == 0))
        with st.expander("",expanded=expanded):
        
            set_oragane = set()
            for couple in mapping_organe_machine:
                if couple[0] in machines:
                    set_oragane = set_oragane.union(set(couple[1]))
            liste_organe_of_selected_machine = list(set_oragane)
            organes = st.multiselect("Organe machine",liste_organe_of_selected_machine)
        df_inter = df_historique[df_historique.apply(lambda row: row['N°SAP_Designation'] in machines, axis=1)]
        sub_df = df_inter[df_inter.apply(lambda row: row['ORGANE MACHINE '] in organes, axis=1)]
        
        sub_df_list = df_to_list(sub_df)
        if len(sub_df_list)//10 == 0:
            text_utile = extract(sub_df_list)
        else:
            st.success("Les données qui permettent de répondre à vos questions sont réparties sur plusieurs groupes. Si Bee Boy ne répond pas à votre question, essayez de passer au groupe suivant à l'aide du compteur ci-dessous (cliquer sur + ou -). Si aucun des groupes ne repondent à votre question, essayez de la formuler autrement.")
            number_of_sub_df = st.number_input("Compteur",min_value=1,max_value=len(sub_df_list)//10+1)
            if number_of_sub_df == len(sub_df_list)//10+1:
                text_utile = extract(sub_df_list[10*(number_of_sub_df-1):])
                print(str(10*(number_of_sub_df-1)) + "->" + str(len(sub_df_list)))
                
            elif number_of_sub_df == 1:
                text_utile = extract(sub_df_list[:9])
                print( "0 -> 9")
                
            else:
                text_utile = extract(sub_df_list[10*(number_of_sub_df-1):10*number_of_sub_df])
                print(str(10*(number_of_sub_df-1)) + "->" + str(10*number_of_sub_df))
                
            
            
           
            
        
        
        
        
        
        if "messages" not in st.session_state:
            
            st.session_state.messages = [{"role": "assistant", "message": first_txt,"content" :""}]
            

        response = ""
        user_input = st.chat_input()
        if user_input:
            prompt = "En ce basant uniquement sur ces données : ( " + text_utile + " ) reponds à la question suivante : " + user_input
            response = get_completion(prompt)
            st.toast('Vérification en cours...')
            st.session_state.messages.append({"role": "user", "message": user_input,"content":""})
            
            
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












            
                        


    
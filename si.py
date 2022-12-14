
#it is a web app based on art or we can say for art lovers
#This app fetch the infomation of each art showing over your streamlit dashboarrd
#If you need the tutorial please comment below

#import the required packages first by type pip install
import random
import re
import urllib.parse
from collections import OrderedDict

import requests
import streamlit as st
from si_query import si_works_query #here i import my query file

# Function that cleans raw text from JSON response
CLEANR = re.compile("<.*?>")


def cleanhtml(raw_text):
    cleantext = re.sub(CLEANR, "", raw_text)
    return cleantext


@st.cache(suppress_st_warning=True, show_spinner=False)
def get_si_data():
    # Smithsonian Linked Data SPARQL endpoint URL
    url = "http://edan.si.edu/saam/sparql"
    query = si_works_query()

    # Call the SPARQL endpoint, pull back data as JSON, and write it to a list
    r = requests.get(url, params={"format": "json", "query": query})
    data = r.json()
    return data


@st.cache(suppress_st_warning=True, show_spinner=False)
def construct_list():
    data = get_si_data()
    artists = []
    for item in data["results"]["bindings"]:
        shortBio = cleanhtml(item["shortBio"]["value"]) if "shortBio" in item else ""
        artists.append(
            OrderedDict(
                {
                    "uri": item["artist"]["value"],
                    "label": item["sampleLabel"]["value"],
                    "image": item["image"]["value"]
                    if "image" in item else "",
                    "birthDate": item["birthDate"]["value"]
                    if "birthDate" in item else "",
                    "deathDate": item["deathDate"]["value"]
                    if "deathDate" in item else "",
                    "shortBio": shortBio,
                    "nationalityLabel": item["nationalityLabel"]["value"]
                    if "nationalityLabel" in item else "",
                    "workRepresentation": item["workRepresentation"]["value"],
                    "work": item["work"]["value"],
                }
            )
        )
    return artists

def app():
    st.set_page_config(page_title="Art-Data-Visualization")
    st.markdown(
        "<h1 style='font-size: 3em; font-family: Verdana, Geneva, sans-serif;'>Art-Data-Visualization</h1>",
        unsafe_allow_html=True,
    )
   
    st.write("It is a web app for art lovers. You will get the data of each art. Refresh the page for more art.")
    with st.spinner(text="Loading ..."):
        list = construct_list()
        artist = random.choice(list)
        artistName = artist["label"]
        cleanArtistName = urllib.parse.quote(artistName)
        birthDate = artist["birthDate"][0:4]
        deathDate = artist["deathDate"]
        lifeRange = f"{birthDate} - {deathDate}"
        artistNat = artist["nationalityLabel"]
        if birthDate != "":
            artistDetails = f"{lifeRange}   *   {artistNat}"
        else:
            artistDetails = artistNat
        workId = artist["work"].partition("http://edan.si.edu/saam/id/object/")[2]
        workLink = f"https://americanart.si.edu/search?query={workId}"
        artistLink = f"https://americanart.si.edu/search?query={cleanArtistName}&f[0]=content_type:person"
        lodArtist = artist["uri"]
        lodWork = artist["work"]

        with st.container():
            st.image(artist["workRepresentation"])
            st.markdown(
                """<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """,
                unsafe_allow_html=True,
            )
        with st.container():
            st.header(artistName)
            st.text(artistDetails)
            col1, col2 = st.columns(2)

            if artist["image"] != "":
                with col1:
                    st.image(artist["image"], use_column_width="always")
                with col2:
                    st.markdown(artist["shortBio"])
            else:
                with col2:
                    st.markdown(artist["shortBio"])
            st.markdown(
                """<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """,
                unsafe_allow_html=True,
            )
            st.header("Links")
            st.markdown("_Data Source: Smithsonian American Art Museum_")
            st.markdown("The work: [Linked open data](%s)  *  [Search the SAAM catalog](%s)" % (lodWork, workLink))
            st.markdown("The artist: [Linked open data](%s)  *  [Search the SAAM catalog](%s)" % (lodArtist, artistLink))

        hide_streamlit_style = """
                    <style>
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

app()

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import json
import re
import uuid
import requests
from bs4 import BeautifulSoup
import chromadb
from flask import Flask, request, jsonify
import threading



# DECLARING VARIABLES

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0.5,
    timeout=None,
    max_retries=3,
    api_key="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",
)

prompt = PromptTemplate.from_template('''
### SCRAPED TEXT: {page}

### TASK INSTRUCTIONS:
Based on the above content, please extract and return information about the drug in the following categories. For each, list specific details provided, or use "not specified" if no information is found and no other details addition. 

### REQUIRED INFORMATION:
1. **Drug Name** - Primary name of the drug and common brand names.
2. **Recommended Foods** - List any foods recommended when taking this drug (if none, specify "none").
3. **Foods to Avoid** - List any foods that should be avoided when taking this drug.
4. **Interacting Drugs** - Provide a list of other drugs that interact with this drug. If a specific waiting period is mentioned for timing between medications, include the wait time in hours; if none is specified, use -1.
5. **Common Side Effects** - Symptoms commonly reported by patients using this drug.
6. **Serious Side Effects** - Symptoms or reactions that may require immediate medical attention.
7. **Primary Uses** - The main medical conditions this drug is prescribed to treat.
                                      
### SAMPLE FORMAT:
{{
    'drug': 'SampleMedicine',
    'super_food': ['none'], 
    'bad_food': ['grapefruit juice', 'infant soy formula', 'cheese', 'yogurt'], 
    'interactive_drug': [
        {{'name': 'Calcium carbonate', 'delta': 4}}, 
        {{'name': 'Sevelamer', 'delta': 4}}, 
        {{'name': 'Lanthanum', 'delta': 4}}, 
        {{'name': 'Cholestyramine', 'delta': 4}}, 
        {{'name': 'Sodium polystyrene sulfonate', 'delta': 4}}
    ]
    'common_symptom': ['fever', 'increased or change in appetite', 'weight loss or weight gain', 'changes in menstrual periods', 'vomiting', 'diarrhea'], 
    'serious_symptom': ['hives', 'difficult breathing', 'diarrhea', 'high blood sugar', 'increased thirst'], 
    'treatment': ['Hypothyroidism', 'Thyroid cancer', 'Myxedema coma']
}}
### OUTPUT FORMAT:
Return the information in STRICT JSON format, following this example:
{{
    "drug": "ExampleDrugName",
    "super_food": ["list any good foods here"],
    "bad_food": ["list any foods to avoid here"],
    "interactive_drug": [
        {{ "name": "OtherDrugName", "delta": integer in hours or -1 }}
    ],
    "common_symptom": ["list common symptoms here"],
    "serious_symptom": ["list serious symptoms here"],
    "treatment": ["main treatments or conditions for this drug"]
}}
### IMPORTANT:
- Output **only JSON** with no extra commentary or explanation.
- If a category has no information, use "not specified" or an empty list as applicable.

''')

client = chromadb.PersistentClient(path="db")
collection = client.get_or_create_collection(name="medDB")
app = Flask(__name__)




# UTILITY FUNCTIONS

def data_from(drug):
    gen = llm.invoke(f"{drug}'s most common generic name only").content.lower().replace(" ","-")
    response = requests.get(f"https://www.drugs.com/{gen}.html")
    if response.status_code != 200:
        response = requests.get(f"https://www.drugs.com/{drug.replace('','-')}.html")
        if response.status_code != 200:
            return
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find('div', id='content')
    text = content.get_text(separator=" ", strip=True)
    return text


def get_salt(medName):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(f"https://www.1mg.com/drugs/{medName}", headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        info_card = soup.find("div", class_="saltInfo")
        if info_card:
            drug = info_card.find('a')
            if drug:
                return drug.get_text().split('+')
            else:
                print("No salt link found.")
                return []
        else:
            print("Salt information not found.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    
def llmModel(medName):
    chain_extract = prompt | llm
    y = get_salt(medName)
    for x in y:
        try:
            r = re.sub(r"\s*\(.*?\)", "", x.strip())
            res = chain_extract.invoke(input={'page':data_from(r)})
            return json.loads(res.content)
        except:
            print("Some Error Occured")


app = Flask(__name__)



@app.route('/addDrug/<usr>', methods=['GET'])
def addDrugTrigger(usr):

    task_thread = threading.Thread(target=addDrugtask, args=(usr,))
    task_thread.start()

    return jsonify({
        "message": "Task has been triggered and is running in the background.",
        "status": "Task is being processed"
    }), 202

def addDrugtask(usr):
    url_get = "https://daily-doze.onrender.com/api/medication/user/"
    url_post = "https://daily-doze.onrender.com/api/medication/"
    response = requests.get(url_get+usr)
    if response.status_code == 200:
        user_medication = response.json()
        print("user meds::",user_medication['medicineDetails'])

        if 'medicineDetails' not in user_medication or not user_medication['medicineDetails']:
            return jsonify({"error": "No medication details found for user."}), 404
        
        for j in user_medication['medicineDetails']:
            link_response = requests.get("https://dailydoseapi.onrender.com/api/data/link/" + j['medName'])
            link_response.raise_for_status()
            prelink = link_response.json().get("link", "").split('/')[-2]
            if(prelink=="otc" or prelink==""):
                continue
            link = link_response.json().get("link", "").split('/')[-1]
            print("link::", link)
            

            x = llmModel(link)


            # print("X",x)


            print("Drug name::",x['drug'])
            query = queryDrug(x['drug']).get('distances', [])[0][0]
            print(type(query))
            print("queryDrug res::",query)

            if query < 1:
                # return jsonify({"mssg": "fail"}), 401
                print("fail")
            else:
                # print(x)
                # put_response = requests.put(url=url_post+j['_id'], json=x)
                put_response = requests.put(url=url_post+usr, json=x)
                if put_response.status_code != 200:
                    print("Failed to update medication",put_response.status_code)
                    # return jsonify({"error": "Failed to update medication"}), 500
                for i in x.get('interactive_drug', []):
                    collection.add(documents=str(i['name']), ids=[str(uuid.uuid4())], metadatas={"name": x['drug']})
        
    else:
        print("Failed to retrieve user medication:", response.status_code)



def queryDrug(drug):
    try:
        query_list = [drug]
        query_results = collection.query(query_texts=query_list, n_results=1)
        metadatas = query_results.get("metadatas", [])
        distances = query_results.get("distances", [])
        
        result = {
            "metadatas": metadatas,
            "distances": distances
        }
        
        return result

    except Exception as e:
        print("Error querying the database for drug interactions:", e)
        # traceback.print_exc()
        return {"metadatas": [], "distances": []}


if __name__=='__main__':
    app.run()
    # print(llmModel('thyronorm-50mcg-tablet-357013'))
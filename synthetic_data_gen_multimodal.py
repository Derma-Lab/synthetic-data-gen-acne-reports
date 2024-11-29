import os
import random
import csv
import base64
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
import requests
from langchain.chat_models import AzureChatOpenAI
from langchain_community.chat_models import AzureChatOpenAI


llm = AzureChatOpenAI(
    openai_api_key="0a077842da424c3593ee8aa9969b096c",
    openai_api_base="https://derma-lab-test.openai.azure.com/",
    openai_api_version="2023-03-15-preview",
    deployment_name="gpt-4o"
)


image_folder = 'resize_img'
output_csv = 'dermatology_reports_multimodal.csv'

image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]


# Function to generate random patient data
def generate_random_patient_data() -> Dict[str, Any]:
    ages = range(10, 80)
    symptoms = ["Itchy skin", "Redness", "Swelling", "Dry patches"]
    durations = ["1 week", "2 weeks", "1 month", "3 months"]
    histories = ["No significant history", "Family history of eczema"]
    allergies = ["None", "Peanuts", "Pollen"]
    medications = ["None", "Antihistamines", "Topical steroids"]

    return {
        "age": random.choice(ages),
        "symptoms": random.choice(symptoms),
        "duration": random.choice(durations),
        "history": random.choice(histories),
        "allergies": random.choice(allergies),
        "medications": random.choice(medications),
        "recent_changes": "None",
        "additional_symptoms": "None",
        "previous_treatments": "None",
        "impact": "Mild discomfort",
        "family_history": "None"
    }


# Function to encode image to Base64
def encode_image(image_path: str) -> str:
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


# Function to generate a multimodal prompt
def generate_multimodal_prompt(image_description: str, patient_data: Dict[str, Any]) -> str:
    return f"""
    You are a dermatologist handling a multimodal diagnostic case.

    Image Description:
    {image_description}

    Patient Data:
    {patient_data}

    Provide a complete assessment in the following format:
    1. DIAGNOSIS: [Diagnosis and reasoning]
    2. TREATMENT PLAN: [Detailed treatment recommendations]
    3. FOLLOW-UP: [Suggestions for further examination or follow-up if necessary]
    """


def get_image_description(image_path: str) -> str:
    image_content = encode_image(image_path)
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an experienced dermatologist. Please describe the visual symptoms and key diagnostic features of this image."
            },
            {
                "role": "user",
                "content": {
                    "type": "image",
                    "image_url": f"data:image/jpeg;base64,{image_content}"
                }
            }
        ]
    }

    try:
        response = requests.post(
            url=f"{llm.azure_endpoint}/chat/completions?api-version={llm.api_version}",
            headers={"Authorization": f"Bearer {llm.api_key}"},
            json=payload
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error processing image: {str(e)}"


# Process each image and generate a report
def process_image(image_path: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
    image_description = get_image_description(image_path)
    prompt = generate_multimodal_prompt(image_description, patient_data)

    # Get multimodal assessment from LLM
    assessment = llm.invoke([
        SystemMessage(content="You are a dermatologist."),
        HumanMessage(content=prompt)
    ])

    return {
        "image": os.path.basename(image_path),
        "patient_data": patient_data,
        "diagnosis_and_plan": assessment.content
    }


# Function to generate a case summary
def generate_case_summary(patient_data: Dict[str, Any]) -> str:
    return (
        f"The patient is a {patient_data['age']}-year-old presenting with "
        f"{patient_data['symptoms']} for {patient_data['duration']}. "
        f"They have a history of {patient_data['history']} and report "
        f"allergies to {patient_data['allergies']}. Current medications include "
        f"{patient_data['medications']}."
    )


# Write results to CSV
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(
        ["Image", "Age", "Symptoms", "Duration", "History", "Allergies", "Medications", "Case Summary", "Diagnosis and Plan"]
    )

    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        patient_data = generate_random_patient_data()
        report = process_image(image_path, patient_data)

        case_summary = generate_case_summary(patient_data)

        writer.writerow([
            report["image"],
            report["patient_data"]["age"],
            report["patient_data"]["symptoms"],
            report["patient_data"]["duration"],
            report["patient_data"]["history"],
            report["patient_data"]["allergies"],
            report["patient_data"]["medications"],
            case_summary,  # Add case summary here
            report["diagnosis_and_plan"]
        ])

        print(f"Processed {image_file} and saved multimodal report.")

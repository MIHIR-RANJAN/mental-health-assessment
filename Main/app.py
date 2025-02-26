import streamlit as st
import numpy as np
import torch
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

# Load models
@st.cache_resource
def load_models():
    bert_model_path = "mental_health_bert_model"
    bert_tokenizer = AutoTokenizer.from_pretrained(bert_model_path)
    bert_model = AutoModelForSequenceClassification.from_pretrained(bert_model_path)
    chatbot = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")
    return bert_tokenizer, bert_model, chatbot

# Define questionnaire
questions = [
    # Section A: Mood and Energy
    "I feel sad, empty, or hopeless",
    "I have little interest or pleasure in doing things",
    "I feel guilty or that I'm a failure",
    "I have thoughts that I would be better off dead or of hurting myself",
    "I feel unusually high, energetic, or euphoric (extremely happy)",
    "I need less sleep than usual but still don't feel tired",
    "My thoughts race and I can't slow my mind down",
    "I'm more talkative than usual or feel pressure to keep talking",
    
    # Section B: Anxiety and Stress
    "I feel nervous, anxious, or on edge",
    "I can't stop or control worrying",
    "I have difficulty relaxing",
    "I feel afraid as if something awful might happen",
    "I feel overwhelmed by my responsibilities",
    "I have physical symptoms like racing heart, sweating, or shortness of breath",
    "I avoid situations or places that make me anxious",
    
    # Section C: Behavioral Patterns
    "My mood changes dramatically and unpredictably",
    "I engage in impulsive behaviors I later regret (spending money, risky sex, substance use)",
    "I have intense and unstable relationships with others",
    "I have difficulty controlling my anger",
    "I feel disconnected from myself or my surroundings",
    "I experience extreme reactions to perceived abandonment",
    "I feel empty inside much of the time",
    
    # Section D: Thought Patterns
    "I have recurring unwanted thoughts that cause anxiety",
    "I engage in repetitive behaviors to reduce anxiety",
    "I'm suspicious of others' intentions toward me",
    "I have unusual beliefs or experiences others don't share",
    "I have difficulty concentrating or making decisions",
    "I'm excessively concerned with order, details, or rules",
    "I'm preoccupied with my appearance or perceived flaws",
    
    # Section E: Social and Functional Impact
    "I withdraw from social activities",
    "I have difficulty performing at work or school",
    "I have trouble maintaining personal relationships",
    "I neglect my self-care or household responsibilities",
    "I use alcohol or drugs to cope with my feelings",
    "I have changes in my appetite or weight"
]

# Section indices
sections = {
    "Depression": [0, 1, 2, 3],
    "Bipolar": [4, 5, 6, 7],
    "Anxiety": [8, 9, 10, 11, 12, 13, 14],
    "Personality Disorders": [15, 16, 17, 18, 19, 20, 21],
    "OCD and Thought Issues": [22, 23, 24, 25, 26, 27, 28],
    "Functional Impact": [29, 30, 31, 32, 33, 34]
}

# Thresholds for each condition
thresholds = {
    "Depression": 6,  # Out of 12 (4 questions, max 3 each)
    "Suicidal": 2,    # Question 4 alone, if ≥ 2
    "Bipolar": 8,     # Out of 12 (4 questions, max 3 each)
    "Anxiety": 10,    # Out of 21 (7 questions, max 3 each)
    "Personality Disorders": 10,  # Out of 21 (7 questions, max 3 each)
    "OCD": 6,         # Questions 22-23, if sum ≥ 6
    "Normal": float('inf')  # Default if others aren't met
}

def analyze_responses(responses):
    scores = {}
    
    # Calculate section scores
    for condition, indices in sections.items():
        scores[condition] = sum(responses[i] for i in indices)
    
    # Special case for suicidal ideation (question index 3)
    scores["Suicidal"] = responses[3]
    
    # Determine conditions meeting thresholds
    potential_conditions = []
    for condition, threshold in thresholds.items():
        if condition in scores and scores[condition] >= threshold:
            potential_conditions.append((condition, scores[condition]))
    
    # If no conditions meet thresholds, consider "Normal"
    if not potential_conditions:
        return "Normal", scores
    
    # Sort by score (highest first)
    potential_conditions.sort(key=lambda x: x[1], reverse=True)
    
    # Return the condition with highest score
    primary_condition = potential_conditions[0][0]
    
    return primary_condition, scores

def responses_to_text(responses):
    """Convert numerical responses to text for BERT model"""
    frequency = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
    text_responses = [f"{questions[i]}: {frequency[min(r, 3)]}" for i, r in enumerate(responses)]
    return " ".join(text_responses)

def get_online_resources(condition):
    """Fetch online resources and advice for the given condition"""
    
    # Define search terms for different conditions
    search_terms = {
        "Depression": ["depression self help", "depression coping strategies", "depression management techniques"],
        "Anxiety": ["anxiety management", "anxiety coping techniques", "anxiety relief strategies"],
        "Bipolar": ["bipolar disorder self management", "bipolar mood stability techniques", "living with bipolar"],
        "Personality Disorders": ["DBT skills", "emotional regulation techniques", "borderline personality self help"],
        "OCD and Thought Issues": ["OCD exposure response prevention", "intrusive thoughts management", "OCD self help"],
        "Stress": ["stress management techniques", "work life balance", "stress reduction methods"],
        "Suicidal": ["suicide prevention resources", "crisis management mental health", "suicide safety planning"],
        "Normal": ["mental wellness tips", "emotional resilience building", "preventive mental health"]
    }
    
    # Select the appropriate search terms
    terms = search_terms.get(condition, search_terms["Normal"])
    
    # Fallback resources in case API calls fail
    fallback_resources = {
        "Depression": [
            {"title": "NIMH - Depression", "link": "https://www.nimh.nih.gov/health/topics/depression"},
            {"title": "Mayo Clinic - Depression self-management", "link": "https://www.mayoclinic.org/diseases-conditions/depression/diagnosis-treatment/drc-20356013"},
            {"title": "Healthline - Natural Depression Remedies", "link": "https://www.healthline.com/health/depression/natural-remedies"}
        ],
        "Anxiety": [
            {"title": "NIMH - Anxiety Disorders", "link": "https://www.nimh.nih.gov/health/topics/anxiety-disorders"},
            {"title": "Mayo Clinic - Anxiety management", "link": "https://www.mayoclinic.org/diseases-conditions/anxiety/diagnosis-treatment/drc-20350967"},
            {"title": "Calm Clinic - Anxiety Techniques", "link": "https://www.calmclinic.com/anxiety/treatment/self-help"}
        ],
        "Bipolar": [
            {"title": "NIMH - Bipolar Disorder", "link": "https://www.nimh.nih.gov/health/topics/bipolar-disorder"},
            {"title": "Depression and Bipolar Support Alliance", "link": "https://www.dbsalliance.org/"},
            {"title": "Healthline - Living with Bipolar Disorder", "link": "https://www.healthline.com/health/bipolar-disorder/living-with"}
        ],
        "Personality Disorders": [
            {"title": "NAMI - Borderline Personality Disorder", "link": "https://www.nami.org/About-Mental-Illness/Mental-Health-Conditions/Borderline-Personality-Disorder"},
            {"title": "NHS - Personality disorders", "link": "https://www.nhs.uk/mental-health/conditions/personality-disorders/"},
            {"title": "Very Well Mind - DBT Skills", "link": "https://www.verywellmind.com/dialectical-behavior-therapy-dbt-for-bpd-425454"}
        ],
        "OCD and Thought Issues": [
            {"title": "International OCD Foundation", "link": "https://iocdf.org/"},
            {"title": "OCD-UK", "link": "https://www.ocduk.org/"},
            {"title": "Very Well Mind - OCD Self-Help", "link": "https://www.verywellmind.com/ocd-self-help-2510625"}
        ],
        "Stress": [
            {"title": "American Psychological Association ", "link": "https://www.apa.org/topics/stress"},
            {"title": "Mayo Clinic - Stress management", "link": "https://www.mayoclinic.org/healthy-lifestyle/stress-management/basics/stress-basics/hlv-20049495"},
            {"title": "HelpGuide - Stress Management", "link": "https://www.helpguide.org/articles/stress/stress-management.htm"}
        ],
        "Suicidal": [
            {"title": "National Suicide Prevention Lifeline", "link": "https://988lifeline.org/"},
            {"title": "Crisis Text Line", "link": "https://www.crisistextline.org/"},
            {"title": "American Foundation for Suicide Prevention", "link": "https://afsp.org/"}
        ],
        "Normal": [
            {"title": "Mental Health America - Staying Mentally Healthy", "link": "https://mhanational.org/staying-mentally-healthy"},
            {"title": "Mayo Clinic - Mental health: Overcoming the stigma", "link": "https://www.mayoclinic.org/diseases-conditions/mental-illness/in-depth/mental-health/art-20046477"},
            {"title": "Mind - How to improve mental wellbeing", "link": "https://www.mind.org.uk/information-support/tips-for-everyday-living/wellbeing/"}
        ]
    }
    
    try:
        # Use a medical/psychological API or search service here
        # This is a placeholder for actual API integration
        # You would implement calls to specific health advice APIs here
        
        # Simulate fetching strategies
        strategies = []
        resources = []
        
        # For demonstration, use a sample API call to get mental health strategies
        # In a real implementation, you would use a proper health API
        for term in terms[:1]:  # Limit to one term to avoid rate limits
            try:
                # Example of how you might fetch data from a search API
                # response = requests.get(f"https://api.example.com/health-search?q={term}")
                # data = response.json()
                
                # Since we can't make actual API calls, use fallback data
                strategies = [
                    f"Establish a consistent daily routine with regular sleep patterns",
                    f"Practice mindfulness meditation for 10-15 minutes daily",
                    f"Engage in regular physical activity (30 minutes, 5 days a week)",
                    f"Keep a mood journal to track triggers and patterns",
                    f"Connect with supportive friends or family members regularly",
                    f"Try cognitive behavioral techniques to challenge negative thoughts",
                    f"Set realistic, achievable goals and celebrate small wins",
                    f"Consider joining a support group (online or in-person)"
                ]
                
                # Add some variety based on the condition
                if condition == "Depression":
                    strategies.append("Schedule pleasurable activities even when motivation is low")
                    strategies.append("Limit alcohol and caffeine which can worsen mood")
                elif condition == "Anxiety":
                    strategies.append("Practice deep breathing exercises (4-7-8 technique)")
                    strategies.append("Create a worry schedule to contain anxious thoughts")
                elif condition == "Bipolar":
                    strategies.append("Maintain a consistent sleep schedule even during mood shifts")
                    strategies.append("Create a crisis plan for managing manic or depressive episodes")
                
                # Get resource links - in a real implementation, you'd fetch these from an API
                resources = fallback_resources.get(condition, fallback_resources["Normal"])
                
            except Exception as e:
                st.error(f"Error fetching recommendations: {str(e)}")
                # Use fallback data
                strategies = ["Error fetching specific strategies. Please check the resources below."]
                resources = fallback_resources.get(condition, fallback_resources["Normal"])
    
    except Exception as e:
        st.error(f"Error connecting to recommendation services: {str(e)}")
        # Use fallback data
        strategies = ["Unable to fetch online recommendations at this time."]
        resources = fallback_resources.get(condition, fallback_resources["Normal"])
    
    return {
        "strategies": strategies,
        "resources": resources
    }

def main():
    st.title("Comprehensive Mental Health Assessment")
    
    # Load models
    bert_tokenizer, bert_model, chatbot = load_models()
    
    # Initialize session state for responses
    if 'responses' not in st.session_state:
        st.session_state.responses = [0] * len(questions)
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    # Show instructions on first page
    if st.session_state.page == 0:
        st.markdown("""
        ## Instructions
        This questionnaire assesses various aspects of mental health. Please rate how often you've 
        experienced each symptom over the past 2 weeks.
        
        **Rating Scale:**
        - 0 = Not at all
        - 1 = Several days
        - 2 = More than half the days
        - 3 = Nearly every day
        
        Your responses are confidential and will be used to provide guidance only. 
        This is not a diagnostic tool and does not replace professional evaluation.
        """)
        
        if st.button("Begin Assessment"):
            st.session_state.page = 1
            st.rerun()
            
    # Questionnaire pages (5 sections)
    elif 1 <= st.session_state.page <= 5:
        section_names = ["Mood and Energy", "Anxiety and Stress", "Behavioral Patterns", 
                         "Thought Patterns", "Social and Functional Impact"]
        current_section = section_names[st.session_state.page - 1]
        
        st.subheader(f"Section {st.session_state.page}: {current_section}")
        
        # Calculate question indices for current section
        start_idx = (st.session_state.page - 1) * 7
        end_idx = min(start_idx + 7, len(questions))
        
        # Display questions for this section
        for i in range(start_idx, end_idx):
            st.session_state.responses[i] = st.select_slider(
                questions[i],
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not at all", "Several days", "More than half the days", "Nearly every day"][x],
                value=st.session_state.responses[i]
            )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        
        if st.session_state.page > 1:
            if col1.button("Previous Section"):
                st.session_state.page -= 1
                st.rerun()
                
        if st.session_state.page < 5:
            if col2.button("Next Section"):
                st.session_state.page += 1
                st.rerun()
        else:
            if col2.button("Submit Responses"):
                st.session_state.submitted = True
                st.session_state.page = 6
                st.rerun()
    
    # Results page
    elif st.session_state.page == 6:
        st.subheader("Assessment Results")
        
        with st.spinner("Analyzing responses..."):
            # Traditional threshold-based analysis
            condition, scores = analyze_responses(st.session_state.responses)
            
            # BERT model analysis
            text_input = responses_to_text(st.session_state.responses)
            inputs = bert_tokenizer(text_input, return_tensors="pt", truncation=True, padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = bert_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(predictions, dim=1).item()
            
            # Get model label mapping 
            class_names = ["Normal", "Depression", "Anxiety", "Bipolar", "Personality Disorder", "Stress", "Suicidal"]
            bert_prediction = class_names[predicted_class]
            
            # Combined result (give preference to BERT model but consider threshold analysis)
            final_result = bert_prediction
            
            # If BERT says normal but thresholds indicate an issue, use threshold result
            if bert_prediction == "Normal" and condition != "Normal":
                final_result = condition
                
            # Special case for suicidal - always prioritize this if threshold met
            if scores["Suicidal"] >= thresholds["Suicidal"]:
                final_result = "Suicidal"
        
        # Display results
        st.markdown(f"## Primary Assessment: {final_result}")
        
        # Generate explanation using chatbot
        explanation_prompt = f"Based on a mental health screening, someone showed signs of {final_result}. Provide a brief, supportive explanation of what this might mean and gentle advice on next steps. Be compassionate but not alarming."
        
        with st.spinner("Generating recommendations..."):
            explanation = chatbot(explanation_prompt, max_length=300)[0]['generated_text']
        
        st.markdown("### What This Means")
        st.write(explanation)
        
        # Show section scores
        st.markdown("### Assessment Breakdown")
        for section, score in scores.items():
            if section != "Suicidal":  # Already accounted for in Depression
                max_score = len(sections.get(section, [])) * 3
                if max_score > 0:
                    percentage = (score / max_score) * 100
                    st.markdown(f"**{section}**: {score}/{max_score} ({percentage:.1f}%)")
        
        # Fetch dynamic recommendations
        with st.spinner("Fetching latest evidence-based recommendations..."):
            st.markdown("### Evidence-Based Recommendations")
            st.info("Connecting to health resources to provide personalized strategies...")
            
            # Get online recommendations
            recommendations = get_online_resources(final_result)
        
        # Create tabs for strategies and resources
        tabs = st.tabs(["Daily Practices", "Recommended Resources"])
        
        with tabs[0]:
            st.markdown("#### Practices that may help:")
            # Display dynamically fetched strategies
            for i, strategy in enumerate(recommendations["strategies"], 1):
                st.markdown(f"{i}. {strategy}")
            
            st.info("💡 **Tip**: Start with just one or two practices and build gradually. Consistency matters more than quantity.")
        
        with tabs[1]:
            st.markdown("#### Helpful Resources:")
            # Display dynamically fetched resources with links
            for resource in recommendations["resources"]:
                st.markdown(f"- [{resource['title']}]({resource['link']})")
            
            st.markdown("#### Mobile Apps That May Help:")
            st.markdown("- **Headspace**: Guided meditation and mindfulness")
            st.markdown("- **Woebot**: AI-based cognitive behavioral therapy")
            st.markdown("- **MoodMission**: Evidence-based mood improvement activities")
            st.markdown("- **Daylio**: Mood and activity tracking")
        
        # Add visualization if needed
        if st.checkbox("Show detailed breakdown visualization"):
            # Create radar chart for section scores
            import matplotlib.pyplot as plt
            import pandas as pd
            
            # Prepare data for radar chart
            categories = list(sections.keys())
            values = []
            for category in categories:
                if category in scores:
                    # Normalize scores to percentages
                    max_possible = len(sections[category]) * 3
                    values.append((scores[category] / max_possible) * 100)
                else:
                    values.append(0)
            
            # Create the radar chart
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111, polar=True)
            
            # Set the angles for each category
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            values.append(values[0])  # Close the loop
            angles.append(angles[0])  # Close the loop
            categories.append(categories[0])  # Close the loop
            
            # Plot the radar chart
            ax.plot(angles, values)
            ax.fill(angles, values, alpha=0.1)
            
            # Set the labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories[:-1])
            
            # Set y-axis limits
            ax.set_ylim(0, 100)
            
            # Display the chart
            st.pyplot(fig)
        
        # Important disclaimer
        st.markdown("""
        ---
        **Important Disclaimer**: This assessment is for informational purposes only and is not a 
        diagnostic tool. The results should not be considered as a substitute for consultation 
        with a qualified mental health professional. If you're experiencing distress, please 
        seek help from a healthcare provider.
        """)
        
        # Restart button
        if st.button("Restart Assessment"):
            st.session_state.responses = [0] * len(questions)
            st.session_state.page = 0
            st.session_state.submitted = False
            st.rerun()
            
        # Resources section if high risk is detected
        if final_result in ["Suicidal", "Depression"] and any(st.session_state.responses[i] >= 2 for i in [3]):
            st.error("""
            ### Crisis Resources
            If you're having thoughts of harming yourself:
            - National Suicide Prevention Lifeline: 988 or 1-800-273-8255
            - Crisis Text Line: Text HOME to 741741
            - Or go to your nearest emergency room
            """)

if __name__ == '__main__':
    main()
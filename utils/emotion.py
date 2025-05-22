from transformers import pipeline
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Cache the emotion classifier model to avoid reloading
@st.cache_resource
def load_emotion_classifier():
    """Load and cache the emotion classification model."""
    try:
        classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
        return classifier
    except Exception as e:
        st.error(f"Error loading emotion model: {str(e)}")
        return None


def analyze_emotions(text):
    """Analyze emotions in the given text using the cached model."""
    if not text:
        return {}

    classifier = load_emotion_classifier()
    if not classifier:
        return {}

    try:
        result = classifier(text)
        # Convert to a simple dictionary format
        emotions = {item['label']: item['score'] for item in result[0]}
        return emotions
    except Exception as e:
        st.error(f"Error analyzing emotions: {str(e)}")
        return {}


def get_emotion_color(emotion):
    """Return a color code for each emotion for consistent visualization."""
    colors = {
        'joy': '#FFD700',  # Gold
        'sadness': '#1E90FF',  # DodgerBlue
        'anger': '#FF4500',  # OrangeRed
        'fear': '#800080',  # Purple
        'love': '#FF69B4',  # HotPink
        'surprise': '#00FF7F',  # SpringGreen
        'disgust': '#A52A2A',  # Brown
        'neutral': '#A9A9A9'  # DarkGray
    }
    return colors.get(emotion, '#808080')  # Default to gray


def plot_emotion_bar_chart(emotions_data):
    """Create a horizontal bar chart of emotions."""
    if not emotions_data:
        return None

    # Sort emotions by score in descending order
    sorted_emotions = dict(sorted(emotions_data.items(), key=lambda item: item[1], reverse=True))

    fig, ax = plt.subplots(figsize=(10, 4))

    emotions = list(sorted_emotions.keys())
    scores = list(sorted_emotions.values())
    colors = [get_emotion_color(emotion) for emotion in emotions]

    y_pos = np.arange(len(emotions))

    ax.barh(y_pos, scores, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(emotions)
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Score')
    ax.set_title('Emotion Analysis')

    # Add score values at the end of each bar
    for i, v in enumerate(scores):
        ax.text(v + 0.01, i, f'{v:.2f}', va='center')

    plt.tight_layout()
    return fig


def plot_emotion_trends(df, emotion_type='dominant'):
    """Plot emotion trends over time.

    Args:
        df: DataFrame with emotion data
        emotion_type: Either 'dominant' to show counts of dominant emotions or
                     a specific emotion name to show its score trend
    """
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))

    if emotion_type == 'dominant':
        # Count occurrences of each dominant emotion
        counts = df['dominant_emotion'].value_counts()
        labels = counts.index
        values = counts.values
        colors = [get_emotion_color(emotion) for emotion in labels]

        ax.bar(labels, values, color=colors)
        ax.set_xlabel('Emotions')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Dominant Emotions')
        plt.xticks(rotation=45)

    else:
        # Plot the trend of a specific emotion's score over time
        if emotion_type in df.columns:
            ax.plot(df['timestamp'], df[emotion_type], marker='o',
                    color=get_emotion_color(emotion_type), linewidth=2)
            ax.set_xlabel('Date')
            ax.set_ylabel('Score')
            ax.set_title(f'Trend of {emotion_type.capitalize()} Over Time')
            plt.xticks(rotation=45)
            fig.tight_layout()
        else:
            return None

    plt.tight_layout()
    return fig
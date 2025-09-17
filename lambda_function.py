import os
import json
import boto3
import requests

# Initialize SNS client
sns = boto3.client("sns")

# Load environment variables
API_KEY = os.environ["API_KEY"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

def lambda_handler(event, context):
    try:
        # 1. Fetch live NBA scores from sportsdata.io
        url = "https://api.sportsdata.io/v3/nba/scores/json/GamesByDate/2025-JAN-01"
        headers = {"Ocp-Apim-Subscription-Key": API_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.text}")

        games = response.json()

        # 2. Format scores
        messages = []
        for game in games:
            home = game["HomeTeam"]
            away = game["AwayTeam"]
            home_score = game.get("HomeTeamScore", "TBD")
            away_score = game.get("AwayTeamScore", "TBD")
            status = game.get("Status", "Scheduled")
            messages.append(f"{away} {away_score} - {home} {home_score} ({status})")

        final_message = "\n".join(messages) if messages else "No NBA games found today."

        # 3. Publish to SNS
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=final_message,
            Subject="NBA Live Scores"
        )

        return {"status": "success", "message": final_message}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "error": str(e)}
"""
Emotion and sentiment analysis service
"""
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple
import logging
from models.conversation import EmotionType

logger = logging.getLogger(__name__)


class EmotionService:
    """Emotion detection and sentiment analysis"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    async def analyze_emotion(self, text: str) -> Tuple[EmotionType, float]:
        """
        Analyze emotion from text
        
        Args:
            text: User's message
            
        Returns:
            Tuple of (EmotionType, confidence_score)
        """
        try:
            if not text or not text.strip():
                return EmotionType.NEUTRAL, 1.0
            
            # Get sentiment scores
            vader_scores = self.vader.polarity_scores(text)
            textblob_sentiment = TextBlob(text).sentiment
            
            # Combine scores for emotion detection
            emotion, confidence = self._determine_emotion(
                vader_scores,
                textblob_sentiment
            )
            
            logger.info(f"Detected emotion: {emotion.value} (confidence: {confidence:.2f})")
            return emotion, confidence
            
        except Exception as e:
            logger.error(f"Emotion analysis error: {e}")
            return EmotionType.NEUTRAL, 0.5
    
    def _determine_emotion(
        self,
        vader_scores: Dict[str, float],
        textblob_sentiment
    ) -> Tuple[EmotionType, float]:
        """
        Determine emotion from sentiment scores
        
        Uses rule-based approach combining VADER and TextBlob.
        """
        compound = vader_scores['compound']
        polarity = textblob_sentiment.polarity
        subjectivity = textblob_sentiment.subjectivity
        
        # Negative emotions
        if vader_scores['neg'] > 0.5:
            if compound < -0.6:
                return EmotionType.ANGRY, vader_scores['neg']
            elif compound < -0.3:
                return EmotionType.FRUSTRATED, vader_scores['neg']
            else:
                return EmotionType.SAD, vader_scores['neg']
        
        # Positive emotions
        elif vader_scores['pos'] > 0.5:
            if compound > 0.6:
                return EmotionType.EXCITED, vader_scores['pos']
            else:
                return EmotionType.HAPPY, vader_scores['pos']
        
        # Confusion detection (high subjectivity, neutral sentiment)
        elif subjectivity > 0.6 and abs(polarity) < 0.2:
            return EmotionType.CONFUSED, subjectivity
        
        # Neutral
        else:
            confidence = 1.0 - abs(compound)
            return EmotionType.NEUTRAL, confidence
    
    async def get_sentiment_score(self, text: str) -> float:
        """
        Get simple sentiment score (-1 to 1)
        
        Returns:
            Float from -1 (negative) to 1 (positive)
        """
        try:
            scores = self.vader.polarity_scores(text)
            return scores['compound']
        except Exception as e:
            logger.error(f"Sentiment scoring error: {e}")
            return 0.0
    
    async def analyze_conversation_sentiment(
        self,
        messages: list
    ) -> Dict[str, float]:
        """
        Analyze overall conversation sentiment
        
        Returns:
            Dict with sentiment metrics
        """
        try:
            if not messages:
                return {
                    "overall": 0.0,
                    "trend": "neutral",
                    "volatility": 0.0
                }
            
            # Get sentiment for each message
            sentiments = []
            for msg in messages:
                if hasattr(msg, 'content'):
                    score = await self.get_sentiment_score(msg.content)
                    sentiments.append(score)
            
            if not sentiments:
                return {"overall": 0.0, "trend": "neutral", "volatility": 0.0}
            
            # Calculate metrics
            overall = sum(sentiments) / len(sentiments)
            
            # Trend: compare first half vs second half
            mid = len(sentiments) // 2
            if mid > 0:
                first_half = sum(sentiments[:mid]) / mid
                second_half = sum(sentiments[mid:]) / (len(sentiments) - mid)
                trend_value = second_half - first_half
                
                if trend_value > 0.2:
                    trend = "improving"
                elif trend_value < -0.2:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "neutral"
            
            # Volatility: standard deviation
            import numpy as np
            volatility = float(np.std(sentiments))
            
            return {
                "overall": overall,
                "trend": trend,
                "volatility": volatility,
                "scores": sentiments
            }
            
        except Exception as e:
            logger.error(f"Conversation sentiment analysis error: {e}")
            return {"overall": 0.0, "trend": "neutral", "volatility": 0.0}

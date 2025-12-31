from typing import Dict, Any
import logging
import re
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class YouTubeProcessor:
    """Process YouTube videos and extract information"""
    
    def __init__(self):
        self.youtube_api_available = False
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            self.transcript_api = YouTubeTranscriptApi
            self.youtube_api_available = True
        except ImportError:
            logger.warning("youtube-transcript-api not available, using fallback")
    
    def process(self, url: str) -> Dict[str, Any]:
        """Process YouTube video"""
        try:
            video_id = self._extract_video_id(url)
            
            if not video_id:
                return {
                    "success": False,
                    "error": "Could not extract video ID from URL"
                }
            
            result = {
                "success": True,
                "video_id": video_id,
                "url": url,
                "embed_url": f"https://www.youtube.com/embed/{video_id}"
            }
            
            if self.youtube_api_available:
                transcript_data = self._get_transcript(video_id)
                result.update(transcript_data)
            else:
                result["transcript"] = "Transcript API not available"
                result["note"] = "Install youtube-transcript-api for full functionality"
            
            result["metadata"] = {"platform": "YouTube"}
            
            logger.info(f"Successfully processed YouTube video: {video_id}")
            return result
            
        except Exception as e:
            logger.error(f"YouTube processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        parsed = urlparse(url)
        
        if 'youtu.be' in parsed.netloc:
            return parsed.path.strip('/')
        
        if 'youtube.com' in parsed.netloc:
            query = parse_qs(parsed.query)
            if 'v' in query:
                return query['v'][0]
            
            match = re.search(r'(?:embed|v)/([^/?]+)', parsed.path)
            if match:
                return match.group(1)
        
        return ""
    
    def _get_transcript(self, video_id: str) -> Dict[str, Any]:
        """Get video transcript"""
        try:
            transcript_list = self.transcript_api.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript_list])
            
            return {
                "transcript": full_text[:5000],
                "transcript_length": len(full_text),
                "num_segments": len(transcript_list),
            }
        except Exception as e:
            logger.warning(f"Could not fetch transcript for {video_id}: {e}")
            return {
                "transcript": f"Transcript not available: {str(e)}",
            }

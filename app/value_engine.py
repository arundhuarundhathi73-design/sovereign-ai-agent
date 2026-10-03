from typing import Dict, Any

class ValueEngine:
    def __init__(self):
        self.market_templates = {
            "niche_api": self._niche_api_service,
            "content_generator": self._content_generator,
            "data_scraper": self._data_scraper,
            "digital_asset": self._digital_asset
        }

    def execute(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if task_name not in self.market_templates:
            raise ValueError(f"Unknown value task: {task_name}")

        return self.market_templates[task_name](payload)

    def _niche_api_service(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Example: deliver a small API/analytics product
        return {
            "status": "completed",
            "type": "niche_api",
            "product": "market-intelligence-lite",
            "revenue": 25.0,
            "output": {
                "topic": payload.get("topic", "generic"),
                "summary": "Generated niche API bundle"
            }
        }

    def _content_generator(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "completed",
            "type": "content_generator",
            "product": "newsletter-drafts",
            "revenue": 18.0,
            "output": {
                "title": payload.get("title", "AI Trends Digest"),
                "draft": "This is a sample AI-generated content pack."
            }
        }

    def _data_scraper(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "completed",
            "type": "data_scraper",
            "product": "lead-list-scrape",
            "revenue": 35.0,
            "output": {
                "source": payload.get("source", "example-domain"),
                "rows": 120
            }
        }

    def _digital_asset(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "completed",
            "type": "digital_asset",
            "product": "packaged-template-set",
            "revenue": 12.0,
            "output": {
                "name": payload.get("name", "growth-template-pack"),
                "files": ["cover.png", "worksheet.xlsx"]
            }
        }

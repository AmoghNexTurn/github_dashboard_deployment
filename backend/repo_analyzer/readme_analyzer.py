# readme_analyzer.py
"""
README file extraction, PII scanning, and analysis.
"""

from typing import Optional, Dict, Any, List
from .fetcher import RepoFetcher

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, RecognizerResult as AnonymizerRecognizerResult
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import (
    EmailRecognizer,
    PhoneRecognizer,
    IpRecognizer,
    UrlRecognizer,
    CreditCardRecognizer,
)

# Configure spacy NLP engine explicitly
configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "en", "model_name": "en_core_web_lg"}
    ]
}

provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

# Build registry with explicit pattern-based recognizers
registry = RecognizerRegistry()
registry.add_recognizer(EmailRecognizer())
registry.add_recognizer(PhoneRecognizer())
registry.add_recognizer(IpRecognizer())
registry.add_recognizer(UrlRecognizer())
registry.add_recognizer(CreditCardRecognizer())

_analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
_anonymizer = AnonymizerEngine()


def _scan_and_redact(content: str) -> tuple[str, List[str]]:
    """
    Scan content for PII and redact it.

    Args:
        content: Text content to scan

    Returns:
        Tuple of (redacted_content, list of detected PII types)
    """
    # Analyze for PII
    results = _analyzer.analyze(
        text=content,
        language='en',
        score_threshold=0.3  # Lower threshold to catch more PII
    )

    if not results:
        return content, []

    # Get unique PII types found
    pii_detected = list(set(r.entity_type for r in results))

    # Build operator config to replace each PII type with a placeholder
    operators = {
        entity_type: OperatorConfig(
            "replace",
            {"new_value": f"<{entity_type}>"}
        )
        for entity_type in pii_detected
    }

    # Anonymize content
    anonymized = _anonymizer.anonymize(
        text=content,
        analyzer_results=[
            AnonymizerRecognizerResult(
                entity_type=r.entity_type,
                start=r.start,
                end=r.end,
                score=r.score
            )
            for r in results
        ],
        operators=operators
    )

    return anonymized.text, pii_detected


class ReadmeAnalyzer:
    """Extract, scan, and analyze README files from repositories."""

    README_PATTERNS = ['readme.md', 'readme.txt', 'readme.rst', 'readme']

    def __init__(self, fetcher: RepoFetcher):
        """
        Initialize analyzer with fetcher.

        Args:
            fetcher: RepoFetcher instance
        """
        self.fetcher = fetcher

    def find_readme(
        self,
        owner: str,
        repo: str,
        branch: str = 'main'
    ) -> Optional[Dict[str, Any]]:
        """
        Find, extract, and scan README file content for PII.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Dict with README info or None if not found
        """
        try:
            tree = self.fetcher.get_repo_tree(owner, repo, branch)

            # Find README files
            readme_files = self.fetcher.find_files(tree, self.README_PATTERNS)

            if not readme_files:
                return None

            # Prefer root-level README
            root_readme = None
            for readme in readme_files:
                if '/' not in readme['path']:
                    root_readme = readme
                    break

            # If no root README, take the first one
            if not root_readme:
                root_readme = readme_files[0]

            # Get content
            content = self.fetcher.get_file_content(
                owner, repo, root_readme['path'], branch
            )

            if not content:
                return None

            # Scan and redact PII
            redacted_content, pii_detected = _scan_and_redact(content)

            return {
                'path': root_readme['path'],
                'size': root_readme.get('size', 0),
                'content': redacted_content,
                'pii_detected': pii_detected,
                'url': f'https://github.com/{owner}/{repo}/blob/{branch}/{root_readme["path"]}'
            }

        except Exception as e:
            print(f"Error finding README: {e}")
            return None


def analyze_readme(
    repo_owner: str,
    repo_name: str,
    branch: str,
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Find, extract, and scan README file from repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with README info or None if not found
    """
    fetcher = RepoFetcher(github_pat)
    analyzer = ReadmeAnalyzer(fetcher)
    return analyzer.find_readme(repo_owner, repo_name, branch)

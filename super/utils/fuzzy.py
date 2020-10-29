from fuzzywuzzy import process
import structlog

logger = structlog.getLogger(__name__)


def fuz(word, words, default=None, threshold=60):
    result = process.extract(word, words, limit=1)
    logger.info("utils/fuz/fuz", word=word, result=result, words=words[:10])
    return result[0][0] if result[0][1] > threshold else default

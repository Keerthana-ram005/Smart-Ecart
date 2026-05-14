import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model globally on startup bypassing the pipeline() abstraction 
# which occasionally has issues registering tasks locally.
try:
    logger.info("Loading summarization model...")
    tokenizer = AutoTokenizer.from_pretrained("t5-small")
    summarizer_model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
except Exception as e:
    logger.error(f"Failed to load summarization model: {str(e)}")
    tokenizer = None
    summarizer_model = None

def generate_summary(transcript: str) -> str:
    """Takes full raw transcript and outputs a concise recipe summary."""
    logger.info("Generating summary...")
    
    if not transcript or len(transcript.split()) < 20:
        return "Insufficient audio dialog context to generate a meaningful summary."
        
    if not summarizer_model or not tokenizer:
        return "Summary AI model unavailable."

    try:
        # Safely truncate transcript to maximum 400 words to prevent T5 context length memory crashes
        safe_transcript = " ".join(transcript.split()[:400])
        
        # T5 uses the "summarize: " prefix
        input_text = "summarize: " + safe_transcript
        
        # Tokenize manually, forcefully truncating to model max_length 512 just in case
        inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        
        # Calculate dynamic max_length based on input string
        input_len = len(input_text.split())
        max_len = max(20, min(60, input_len // 2))
        min_len = min(10, max_len - 10)
        
        # Generate outputs via robust Beam Search to block repetition loops
        outputs = summarizer_model.generate(
            **inputs, 
            max_length=max_len, 
            min_length=min_len, 
            num_beams=4,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        
        # Decode tensor to string
        summary_result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if summary_result:
            result = summary_result.strip()
            # Capitalize first letter for cleanliness
            return result[0].upper() + result[1:]
            
        return "Summary could not be generated."
        
    except Exception as e:
        logger.error(f"Error during NLP summarization: {str(e)}")
        return "Failed to parse transcript summary."

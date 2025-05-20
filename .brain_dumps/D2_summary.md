# Brain Dump D2 Summary

## Tokenization Insights
- Possibility to adapt tokenizer for HTML input
- Make HTML elements (div, table, etc.) single tokens
- Hypothesis that Claude may do this, explaining their better coding capabilities

## Evaluation Metrics
- Precision, recall, and F1-score for performance evaluation
- Vector similarity between labeled data and AI-labeled data (scale 0-1)
- Amount of errors as final metric
- Quality of extraction

## Dataset Preparation Plan
1. Use real-world data
2. Use existing script that marks content with xdata tag
3. Run script on raw HTML
4. Save processed content into separate files for extraction
5. Label at least 10 websites, including complex ones (GitHub) and interesting sites (Google Search)
6. Process data through the system for manual labeling
7. Augment data to create variations (for buttons, etc.)
8. Use processed data to train models (Mistral, LLaM)

## Implementation Approach
1. Practical method using headless browser:
   - Go to page
   - Activate page using headful browser
   - Click buttons
   - Capture HTML (already marked)
   - Feed to AI
   - Save to file
2. Create static analyzer to process through fine-tuned model

## Testing and Comparison
- Compare approach with general-purpose models
- Test with Claude (Haiku, 3, or 7 in batch mode) and GPT
- Implement basic markup fixes with Mistral
- Use retry (3 attempts) for issues
- Evaluate error rates and extraction quality
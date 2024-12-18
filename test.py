import re

def remove_search_queries_and_after(text):
    # Use regex to match "### Search Queries" and everything after it
    cleaned_text = re.sub(r'### Search Queries.*', '', text, flags=re.DOTALL)
    return cleaned_text.strip()  # Strip trailing whitespace if needed

# Example usage
input_string = """Some relevant text
with multiple lines.

### Search Queries
irrelevant content that needs to be removed."""
output_string = remove_search_queries_and_after(input_string)
print(output_string)

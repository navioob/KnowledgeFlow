from doc2json.grobid2json.process_pdf import process_pdf_stream
import os
import json
from tqdm import tqdm

##processing functions

def generate_tei_json(file_path, file_bytes):
    filename = file_path.split('/')[-1].split('.')[0]
    data = process_pdf_stream(filename,"", file_bytes)

    return data

def merge_hierarchical_sections(data):
    merged_sections = {}
    current_none_section = None  # Track the ongoing 'None' section block
    all_text = ""  # This will store all concatenated text
    last_valid_sec_num = None  # Keep track of the last valid section number
    pending_none_group = None  # Track if a group of None sections needs assigning

    # Iterate through the body_text list
    for entry in data['body_text']:
        sec_num = entry.get('sec_num')
        all_text += " " + entry['text']  # Append the current text to all_text

        if sec_num is None:  # Handle 'None' sections
            if current_none_section is None:
                # Start a new 'None' section block
                current_none_section = {
                    'section': entry['section'],
                    'sec_num': None,
                    'text': entry['text'],
                    'eq_spans': entry.get('eq_spans', []),
                    'list_of_sections': [entry]
                }
            else:
                # Append to the existing 'None' block
                current_none_section['text'] += " " + entry['text']
                current_none_section['eq_spans'].extend(entry.get('eq_spans', []))
                current_none_section['list_of_sections'].append(entry)
            continue

        # If a valid sec_num appears after 'None', decide grouping for 'None'
        if current_none_section:
            if not last_valid_sec_num:
                # Case 1: 'None' at the start of the document
                main_sec_num = sec_num.split('.')[0]
                none_sec_num = f"{main_sec_num}.0"  # Assign to the main section's first subsection
            elif pending_none_group:
                # Case 2: 'None' following another valid section
                none_sec_num = pending_none_group
                pending_none_group = None
            else:
                # Case 3: 'None' before a valid section
                last_main_sec_num = last_valid_sec_num.split('.')[0]
                none_sec_num = f"{last_valid_sec_num}.1"  # Assign as the next subsection of the last valid section

            current_none_section['sec_num'] = none_sec_num
            merged_sections[none_sec_num] = current_none_section
            current_none_section = None  # Reset for future blocks

        # Handle valid sec_num
        main_sec_num = sec_num.split('.')[0]

        # Update pending group for future None sections
        pending_none_group = f"{sec_num}.1"

        # Initialize if main_sec_num is not in merged_sections
        if sec_num not in merged_sections:
            merged_sections[sec_num] = {
                'section': entry['section'],
                'sec_num': sec_num,
                'text': entry['text'],
                'eq_spans': entry.get('eq_spans', []),
                'list_of_sections': [entry]
            }
        else:
            # Append the text and eq_spans to the main section
            merged_sections[sec_num]['text'] += " " + entry['text']
            merged_sections[sec_num]['eq_spans'].extend(entry.get('eq_spans', []))
            merged_sections[sec_num]['list_of_sections'].append(entry)

        last_valid_sec_num = sec_num  # Update last valid section

    # Handle 'None' at the end of the document
    if current_none_section:
        if last_valid_sec_num:
            last_main_sec_num = last_valid_sec_num.split('.')[0]
            none_sec_num = f"{last_valid_sec_num}.1"  # Assign as the next subsection
        else:
            none_sec_num = "0.0"  # Default section number if no valid sections exist

        current_none_section['sec_num'] = none_sec_num
        merged_sections[none_sec_num] = current_none_section

    # Convert merged_sections back to a list, preserving the order of section numbers
    merged_body_text = list(merged_sections.values())

    # Return the updated data with merged sections, including the concatenated all_text
    return {
        'title': data['title'],
        'authors': data['authors'],
        'abstract': data.get('abstract', ''),
        'all_text': all_text.strip(),
        'body_text': merged_body_text
    }

def group_main_sections(data):
    grouped_sections = {}

    for section in data['body_text']:
        sec_num = section.get('sec_num')

        if not sec_num:
            # Skip sections without a valid section number
            continue

        # Extract the main section number (before the first dot)
        main_sec_num = sec_num.split('.')[0]

        # If the main section is not already initialized, create it
        if main_sec_num not in grouped_sections:
            grouped_sections[main_sec_num] = {
                'section': f"Section {main_sec_num}",
                'sec_num': main_sec_num,
                'text': section['text'],
                'eq_spans': section.get('eq_spans', []),
                'list_of_sections': section['list_of_sections']
            }
        else:
            # Append the text and details to the main section
            grouped_sections[main_sec_num]['text'] += " " + section['text']
            grouped_sections[main_sec_num]['eq_spans'].extend(section.get('eq_spans', []))
            grouped_sections[main_sec_num]['list_of_sections'].extend(section['list_of_sections'])

    # Convert grouped_sections back to a list to match the original structure
    grouped_body_text = list(grouped_sections.values())

    # Return updated data with grouped sections
    return {
        'title': data['title'],
        'authors': data['authors'],
        'abstract': data.get('abstract', ''),
        'all_text': data['all_text'],  # Reuse the all_text from the input
        'body_text': grouped_body_text
    }

class Parser:
    def __init__(self):
        pass

    def extract_text(self, file_path, file_bytes):
        extracted_json = generate_tei_json(file_path, file_bytes)

        paper = {
            'title':extracted_json['title'],
            'authors': extracted_json['authors'],
            'abstract': extracted_json['abstract'],
            'body_text': [{'text': chunk['text'], 
                        'section': chunk['section'],
                        'sec_num': chunk['sec_num'], 
                        'eq_spans': chunk['eq_spans']} for chunk in extracted_json['pdf_parse']['body_text']]}
        
        #check if there are all missing section number
        all_section_number = [section['sec_num'] for section in paper['body_text']]
        if all(obj is None for obj in all_section_number):
            unqiue_sections = []
            [unqiue_sections.append(section['section']) for section in paper['body_text'] if section['section'] not in unqiue_sections]
            print(unqiue_sections)
            for section in paper['body_text']:
                section_number_extracted = unqiue_sections.index(section['section'])
                section['sec_num'] = f"{section_number_extracted+1}"

        merged_data = merge_hierarchical_sections(paper)
        merged_data = group_main_sections(merged_data)
        print(merged_data)
        return merged_data


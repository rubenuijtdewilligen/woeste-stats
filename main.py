import pandas as pd
from docx import Document

def parse_multi_table_document(file_path):
    doc = Document(file_path)
    all_data = []
    current_date = "Onbekende datum"
    
    for element in doc.element.body:
        if element.tag.endswith('p'):
            text = "".join(node.text for node in element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')).strip()
            if text and len(text) < 25:
                current_date = text
        
        elif element.tag.endswith('tbl'):
            for table in doc.tables:
                if table._element == element:
                    for row in table.rows[1:]:
                        dag_raw = row.cells[0].text.strip().split('\n')[0]
                        dag = dag_raw.strip()
                        verhuring_cell = row.cells[1].text.strip().split('\n')
                        verhuring = verhuring_cell[0] if verhuring_cell else ""
                        
                        nazi_shifts = []
                        nazi_text = row.cells[6].text.strip().split('\n')
                        for line in nazi_text:
                            if 'Open:' in line:
                                naam = line.replace('Open:', '').strip()
                                if naam:
                                    nazi_shifts.append((naam, "Open"))
                                    all_data.append([current_date, dag, naam, "Open", 1, verhuring])
                            elif 'Sluit:' in line:
                                naam = line.replace('Sluit:', '').strip()
                                if naam:
                                    nazi_shifts.append((naam, "Sluit"))
                                    all_data.append([current_date, dag, naam, "Sluit", 1, verhuring])

                        shift_mapping = {
                            3: "Open", 
                            4: "Spits", 
                            5: "Sluit", 
                            7: "Naschoonmaak"
                        }
                        
                        for col_idx, shift_name in shift_mapping.items():
                            namen = row.cells[col_idx].text.strip().split('\n')
                            for naam in namen:
                                naam = naam.strip()
                                if naam:
                                    if (naam, shift_name) not in nazi_shifts:
                                        all_data.append([current_date, dag, naam, shift_name, 0, verhuring])
                    break

    df = pd.DataFrame(all_data, columns=['Week van', 'Dag', 'Naam', 'Shift', 'Nazi?', 'Verhuring'])
    return df

df = parse_multi_table_document("input.docx")
df.to_excel("output.xlsx", index=False)
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_dataframe(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define the namespace dictionary
    namespaces = {
        'ss': 'urn:schemas-microsoft-com:office:spreadsheet'
    }

    # Initialize data list
    data = []

    # Find the rows in the worksheet
    for row in root.findall('.//ss:Row', namespaces):
        cells = row.findall('.//ss:Cell', namespaces)
        row_data = []
        for cell in cells:
            data_element = cell.find('.//ss:Data', namespaces)
            if data_element is not None:
                row_data.append(data_element.text)
            else:
                row_data.append(None)
        data.append(row_data)

    # Convert list of lists to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])  # First row is header
    return df


def xml_to_excel(xml_file, excel_file):
    df = xml_to_dataframe(xml_file)
    df.to_excel(excel_file, index=False)


# Example usage
xml_file = '../data/firma_stok_31.XML'  # Replace with your XML file
excel_file = '../data/output.xlsx'  # Replace with your desired Excel file name

xml_to_excel(xml_file, excel_file)
print(f"Converted {xml_file} to {excel_file}")

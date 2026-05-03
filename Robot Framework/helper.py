import pandas as pd
from pathlib import Path
from selenium.webdriver.common.by import By


def read_html_table_to_dataframe(table_element, filter_date=None):
    columns = table_element.find_elements(By.CLASS_NAME, "y-column")

    headers = []
    all_data = []

    for column in columns:
        header = column.find_element(By.ID, "header").text.strip()
        headers.append(header)

        parent_cells = column.find_elements(By.CSS_SELECTOR, "g.column-cell")

        cells_with_position = []
        for parent in parent_cells:
            transform = parent.get_attribute("transform")
            if "translate" in transform:
                y_str = transform.split(",")[1].replace(")", "").strip()
                y_pos = float(y_str)

                try:
                    text_elem = parent.find_element(By.CLASS_NAME, "cell-text")
                    text = text_elem.text.strip()

                    if text and text != header:
                        cells_with_position.append((y_pos, text))
                except:
                    pass

        cells_with_position.sort(key=lambda x: x[0])
        column_data = [text for y, text in cells_with_position]
        all_data.append(column_data)

    num_rows = len(all_data[0])
    rows = [[all_data[col][i] for col in range(len(all_data))]
            for i in range(num_rows)]

    df = pd.DataFrame(rows, columns=headers)

    if 'Visit Date' in df.columns:
        df['Visit Date'] = pd.to_datetime(df['Visit Date']).dt.strftime('%Y-%m-%d')

    if 'Average Time Spent' in df.columns:
        df['Average Time Spent'] = pd.to_numeric(df['Average Time Spent'], errors='coerce')

    if filter_date and 'Visit Date' in df.columns:
        df = df[df['Visit Date'] == filter_date]

    df = df.sort_values(by=list(df.columns)).reset_index(drop=True)

    return df


def read_parquet_data(parquet_folder, filter_date=None):
    parquet_path = Path(parquet_folder)

    if not parquet_path.exists():
        raise FileNotFoundError(f"Parquet folder not found: {parquet_folder}")

    df = pd.read_parquet(parquet_path)

    df = df[['facility_type', 'visit_date', 'avg_time_spent']]

    if filter_date:
        df['visit_date'] = pd.to_datetime(df['visit_date']).dt.strftime('%Y-%m-%d')
        df = df[df['visit_date'] == filter_date]

    df = df.rename(columns={
        'facility_type': 'Facility Type',
        'visit_date': 'Visit Date',
        'avg_time_spent': 'Average Time Spent'
    })

    df['Visit Date'] = pd.to_datetime(df['Visit Date']).dt.strftime('%Y-%m-%d')
    df['Average Time Spent'] = pd.to_numeric(df['Average Time Spent'], errors='coerce')

    df = df.sort_values(by=list(df.columns)).reset_index(drop=True)

    return df


def compare_dataframes(df1, df2):
    result = {
        'match': False,
        'differences': ''
    }

    if df1.empty and df2.empty:
        result['differences'] = f"No data found for the given date in either source."
        return result

    if df1.empty or df2.empty:
        result['differences'] = f"No data found for the given date in {'HTML' if df1.empty else 'Parquet'}."
        return result

    if df1.shape != df2.shape:
        result[
            'differences'] = f"Shape mismatch: HTML has {df1.shape[0]} rows x {df1.shape[1]} cols, Parquet has {df2.shape[0]} rows x {df2.shape[1]} cols"
        return result

    if not df1.columns.equals(df2.columns):
        result[
            'differences'] = f"Column mismatch:\nHTML columns: {list(df1.columns)}\nParquet columns: {list(df2.columns)}"
        return result

    comparison = df1.compare(df2)

    if comparison.empty:
        result['match'] = True
        result['differences'] = 'DataFrames match exactly!'
        return result

    diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
    result['differences'] = diff.to_string()
    return result
